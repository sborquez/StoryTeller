from typing import Callable
from configparser import ConfigParser
import uuid
import os

from google.cloud import texttospeech
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    RunnablePassthrough, RunnableLambda, RunnableBranch, RunnableSequence
)
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate


def _gcp_tts_generator(
        voice: str = "en-US-Neural2-C", language: str = "en-US",
        output_folder: str = "./audio") -> Callable:
    def tts_generator(prompt: str) -> dict:
        # Instantiates a client
        client = texttospeech.TextToSpeechClient()

        # Set the text input to be synthesized
        text = prompt.text
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Build the voice request, select the language code and voice name
        voice_config = texttospeech.VoiceSelectionParams(
            language_code=language, name=voice
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            pitch=4.0,
            speaking_rate=1.20,
        )

        # Perform the text-to-speech request on the text input with the
        # selected voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice_config,
            audio_config=audio_config,
        )

        # The response's audio_content is binary.
        random_name = f"{str(uuid.uuid4())}.mp3"
        output_file = os.path.join(output_folder, random_name)
        with open(output_file, "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)
        return output_file
    return tts_generator


class _Prompts:
    """Container for prompts. This class is used to store the default prompts
    and load them from the environment variables.
    """

    # Prompts components
    # Writter
    writer_task = """
    You are story writer. You help the user write a page of a story.
    The workflow of the story writing is the following:
    1. Understand the <context> for setting up an engaging story.
    2. The user will respond with the <action> taken from the last page.
    3. If it is the first page, the action should be "start".
    4. Write the next page of the story from the <action> and the current <karma_points>. Write the consecuence of the action and current state in the page's <description>, a list of 2 possible <next_action>s, and the <karma_points> change for the story.
    5. Repeat the step 2 to 4 until you reach the max length of the story. If you reach the ending page, there should be only one <next_action> with the "End" action.
    """

    writer_rules = """
    The writer rules are:
    1. The first page (number 1) always start with the "start" action. No other action is allowed.
    2. The last page (number MAX_PAGES) always end by one "End" next_action. No other next_action is allowed.
    3. An action is a string of max 50 characters, with only the description of the action.
    4. A description is a string of max 250 characters.
    5. The karma_points is a list of 4 float numbers, representing the change for the story in 4 dimensions:
    - Technology. Higher is more advanced. Lower is no technology.
    - Happiness. Higher is humans are happier. Lower is humans are unhappier.
    - Safety. Higher is humans are safer. Lower is humans doesn't exist.
    - Control. Higher is humans have more control. Lower is AGI has more control.
    The values are between -1 and 1 and the story final karma_points is the aggregation of page karma_points changes.
    6. The max length of the story is MAX_PAGES pages, so the last pages ends the story. Take in account the rythm of the story and the length of the pages, so the story is engaging.
    7. Use the JSON output format defined in the [output_format] section.
    """

    writer_output_format = """
    The output JSON format:
    - "description": The description of the current page.
    - "next_actions": The list of the next actions.
    - "karma_points": A list representing the karma points change for the page.
    """

    writer_knowledge = """
    Knowledge for story inspiration:
    - The writer knows the following characters: CHARACTERS
    - The story categories: CATEGORIES
    - Ispired by the following books: BOOKS
    - Ispired by the following movies: MOVIES
    - Ispired by the following anime: ANIMES
    """

    drawer_task = """
    Generate a short prompt to generate an image based on:
    1. Scene description: {description}
    2. Use this style: STYLE
    3. Generate consistent images with this seed: SEED
    4. The length of the prompt should not be more than 1000 characters.
    5. Not render any text in the image!!!
    """

    # Default prompt replacements
    replace = {
        "MAX_PAGES": "5",
        "STYLE": "90s aesthetics, with a dark style and pixel art graphics. Using the following colors: #000000, #ffffff, #ff0000, #00ff00, #0000ff, #ffff00, #ff00ff, #00ffff",
        "CHARACTERS": 'Sebastian, Fran',
        "CATEGORIES": 'sci-fi, utopia, dystopia',
        "BOOKS": '"1984", "Life 3.0: Alpha team tale"',
        "MOVIES": '"The Matrix", "The Terminator"',
        "ANIMES": '"Ghost in the Shell", "Serial Experiments Lain"',
        "SEED": "123456789",
    }

    @staticmethod
    def get_prompt(name: str, prompt_replace: dict = {}) -> str:
        """Get the prompt by name.

        Args:
            name (str): The name of the prompt.

        Returns:
            str: The prompt.
        """
        prompt = _Prompts.__dict__[name]
        for key, value in prompt_replace.items():
            prompt = prompt.replace(key, value)
        return prompt

    @staticmethod
    def get_default_replace() -> dict:
        """Get the default prompt replacements.

        Returns:
            dict: The default prompt replacements.
        """
        return _Prompts.replace.copy()


class ChainFactory:
    """Chain factory class.

    This class is used to create a new teller.
    """

    @classmethod
    def from_config(cls, config: ConfigParser) -> RunnableSequence:
        """Create a new teller.

        Args:
            config (ConfigParser): The configuration parser instance.

        Returns:
            RunnableSequence: A new chain instance.
        """
        prompt_replace = _Prompts.get_default_replace()
        for key in prompt_replace.keys():
            prompt_replace[key] = config.get("prompt_replace", key.lower(), fallback=prompt_replace[key])

        # Writer
        writer_chain = cls._build_writer(config, prompt_replace)
        # Drawer
        if config.get("writer", "drawer", fallback="disabled") == "enabled":
            drawer = cls._build_drawer(config, prompt_replace)
        else:
            drawer = RunnableLambda(lambda x: None)
        # Speaker
        if config.get("writer", "speaker", fallback="disabled") == "enabled":
            speaker = cls._build_speaker(config, prompt_replace)
        else:
            speaker = RunnableLambda(lambda x: None)

        # Chain
        chain = (
            RunnablePassthrough.assign(page=writer_chain)
            | {
                "page": RunnableLambda(lambda x: x["page"]),
                "image_url": RunnableLambda(lambda x: x["page"]) | drawer,
                "audio_file": RunnableLambda(lambda x: {"description": x["page"]["description"], "action": x["action"], "page_number": x["page_number"]}) | speaker,
            }
        )
        return chain

    @classmethod
    def _build_writer(cls, config: ConfigParser, prompt_replace: dict = {}) -> RunnableSequence:
        # Writer Prompt
        task = _Prompts.get_prompt("writer_task", prompt_replace)
        rules = _Prompts.get_prompt("writer_rules", prompt_replace)
        knowledge = _Prompts.get_prompt("writer_knowledge", prompt_replace)
        output_format = _Prompts.get_prompt("writer_output_format", prompt_replace)
        messages = [
            ("system",
                "[task]: " + task + "\n"
                "[rules]: " + rules + "\n"
                "[knowledge]: " + knowledge + "\n"
                "[output_format]: " + output_format + "\n"
                "[context]: {context}\n"
             ),
            ("ai",
                "I will write the next page of the story as "
                "defined in the [task] in the format defined in [rules] and using the [knowledge]"
                "and the [context]"
                "Here a list of the previous pages: {pages}\n"
                "This is the current karma points: {karma_points}\n"
                "This is the page number {page_number}"
             ),
            ("human", "I choice the action {action}"),
        ]
        # Writer Chain
        model = config.get("writer", "model", fallback="gpt-4")
        temperature = config.get("writer", "temperature", fallback=0.9)
        writer_chain = (
            ChatPromptTemplate.from_messages(messages)
            | ChatOpenAI(model=model, temperature=temperature)
            | JsonOutputParser()
        )
        return writer_chain

    @classmethod
    def _build_drawer(cls, config: ConfigParser, prompt_replace: dict = {}) -> RunnableSequence:
        # Drawer Prompt
        drawer_task = _Prompts.get_prompt("drawer_task", prompt_replace)
        # Drawer Chain
        prompter_model = config.get("drawer", "prompter_model", fallback="gpt-4")
        prompter_temperature = float(config.get("drawer", "prompter_temperature", fallback="0.0"))
        drawer_model = config.get("drawer", "drawer_model", fallback="dall-e-3")
        size = config.get("drawer", "image_size", fallback="1024x1024")
        quality = config.get("drawer", "image_quality", fallback="standard")

        drawer = (
            ChatPromptTemplate.from_template(drawer_task)
            | ChatOpenAI(
                model=prompter_model, temperature=prompter_temperature
            )
            | StrOutputParser()
            | RunnableLambda(
                lambda x: DallEAPIWrapper(
                    model=drawer_model, size=size, quality=quality
                ).run(x)
            )
        )
        return drawer

    @classmethod
    def _build_speaker(cls, config: dict, prompt_replace: dict = {}) -> RunnableSequence:

        voice = config.get("speaker", "voice", fallback="en-US-Neural2-C")
        language = config.get("speaker", "language", fallback="en-US")
        output_folder = config.get("speaker", "data", fallback="./tmp/audio")

        speaker = (
            RunnableBranch(
                (
                    lambda x: x["page_number"] == 1,
                    PromptTemplate.from_template("{description}")
                ),
                PromptTemplate.from_template(
                    "You choose: {action}. {description}."
                )
            )
            | RunnableLambda(
                _gcp_tts_generator(voice, language, output_folder)
            )
        )
        return speaker
