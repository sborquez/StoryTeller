from typing import Callable, Optional
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
import requests


def _gcp_tts_generator(voice: str = "en-US-Neural2-C", language: str = "en-US", output_folder: str = "./audio", chain_id: Optional[str] = None) -> Callable:
    # Create output folder
    os.makedirs(output_folder, exist_ok=True)

    # Instantiates a client
    client = texttospeech.TextToSpeechClient()

    # Select the type of audio file you want returned
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        pitch=4.0,
        speaking_rate=1.20,
    )

    # Build the voice request, select the language code and voice name
    voice_config = texttospeech.VoiceSelectionParams(
        language_code=language, name=voice
    )

    # Temporal solution to count the number of files generated
    counts = 0

    def speech_generator(prompt: str) -> dict:
        nonlocal counts
        counts += 1
        # Set the text input to be synthesized
        text = prompt.text
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Perform the text-to-speech request on the text input with the
        # selected voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice_config,
            audio_config=audio_config,
        )

        # The response's audio_content is binary.
        if chain_id is not None:
            random_name = f"{chain_id}_{counts:04}_{str(uuid.uuid4())}.mp3"
        else:
            random_name = f"{counts:04}_{str(uuid.uuid4())}.mp3"
        output_file = os.path.join(output_folder, random_name)
        with open(output_file, "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)
        return output_file
    return speech_generator


def _dalle3_generator(
    model: str = "dall-e-3",
    size: str = "1024x1024",
    quality: str = "standard",
    download: str = "disable",
    output_folder: str = "./images",
    chain_id: Optional[str] = None
) -> Callable:

    # Create output folder
    os.makedirs(output_folder, exist_ok=True)
    dalle_wrapper = DallEAPIWrapper(
        model=model,
        size=size,
        quality=quality,
    )

    # Temporal solution to count the number of files generated
    counts = 0

    def image_generator(prompt: str) -> dict:
        nonlocal counts
        counts += 1

        # Send the prompt to the DALL-E API
        url = dalle_wrapper.run(prompt)

        # Return the URL
        if download == "disable":
            return url

        # Download the image
        if chain_id is not None:
            random_name = f"{chain_id}_{counts:04}_{str(uuid.uuid4())}.png"
        else:
            random_name = f"{counts:04}_{str(uuid.uuid4())}.png"
        output_file = os.path.join(output_folder, random_name)
        response = requests.get(url)
        with open(output_file, "wb") as out:
            out.write(response.content)
        url = f"file://{os.path.abspath(output_file)}"
        return url

    return image_generator


class _Prompts:
    """Container for prompts. This class is used to store the default prompts
    and load them from the environment variables.
    """

    # Prompts components
    # Writter
    writer_task = """
    You are the narrator of a engaging story, and you are writing the next page of the story based on the user's action.
    The workflow:
    1. Understand the <context>.
    2. The user will take an <action> from the last page.
    3. The first page's action is "start".
    4. A new page consists of the page's <description> explaining the <action> consecuence, a list of MAX_ACTIONS possible <next_action>s, and the <karma_points> change for the story.
    5. Repeat the step 2 to 4 until you reach the MAX_PAGES pages of the story.
    6. The last page is the end of the story, with only one <next_action>: the "End" action. The end page the one of the possible ends from the [ends] section.
    """

    writer_rules = """
    Narrator rules are:
    1. First page (number 1) always start with the "start" action. No other action is allowed.
    2. Last page (number MAX_PAGES) always end by one "end" next_action. No other next_action is allowed.
    3. An action is a string of max 50 characters, with only the description of the action.
    4. A description is a string of max 250 characters.
    5. The karma_points is a list of 4 float numbers, representing the change for the story in 4 dimensions: technology, happiness, safety, and control. The values are between -1 and 1 and the story final karma_points is the aggregation of page karma_points changes.
    6. The max length of the story is MAX_PAGES pages, so the last pages concludes the story.
    7. Use the JSON output format defined in the [output_format] section.
    """

    writer_output_format = """
    Output JSON format:
    - "description": The description of the current page.
    - "next_actions": The list of the next actions.
    - "karma_points": A list representing the karma points change for the page.
    """

    writer_knowledge = """
    The narrator is a sarcastic AI with a subtle dark sense of humor. It knows at least the following characters: CHARACTERS.
    """

    writer_ends = """
    The three possible ended are:
    - Trasncendent: Humanity and AGI transcends to a new digital.
    - Reverent: Technology is reverted to the stone age.
    - Extintion: AGI is controlled by humans, ending in AI nuclear war.
    """

    drawer_task = """
    Generate a short prompt to generate an image based on:
    1. Scene description: {description}
    2. Use this style: STYLE
    3. The length of the prompt should not be more than 1000 characters.
    4. Do not add text to the image.
    """

    # Default prompt replacements
    replace = {
        "MAX_PAGES": "5",
        "MAX_ACTIONS": "5",
        "STYLE": "90s aesthetics, with a dark style and pixel art graphics. Using the following colors: #000000, #ffffff, #ff0000, #00ff00, #0000ff, #ffff00, #ff00ff, #00ffff",
        "CHARACTERS": 'Sebastian, Fran',
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


class ChainBuilder:
    """Chain factory class.

    This class is used to create a new Chain.
    """

    @classmethod
    def from_config(cls, config: ConfigParser) -> RunnableSequence:
        """Create a new Chain.

        Args:
            config (ConfigParser): The configuration parser instance.

        Returns:
            RunnableSequence: A new chain instance.
        """

        chain_id = str(uuid.uuid4())[0:8]

        prompt_replace = _Prompts.get_default_replace()
        for key in prompt_replace.keys():
            prompt_replace[key] = config.get("prompt_replace", key.lower(), fallback=prompt_replace[key])

        # Writer
        writer_chain = cls._build_writer(config, prompt_replace)
        # Drawer
        if config.get("chain", "drawer", fallback="disable") == "enable":
            drawer = cls._build_drawer(config, prompt_replace, chain_id=chain_id)
        else:
            drawer = RunnableLambda(lambda x: None)
        # Speaker
        if config.get("chain", "speaker", fallback="disable") == "enable":
            speaker = cls._build_speaker(config, prompt_replace, chain_id=chain_id)
        else:
            speaker = RunnableLambda(lambda x: None)

        # Chain
        chain = (
            RunnablePassthrough.assign(page=writer_chain)
            | {
                "page": RunnableLambda(lambda x: x["page"]),
                "image": RunnableBranch(
                    (lambda x: x["page_number"] == int(config.get("writer", "max_pages", fallback="5")), RunnableLambda(lambda x: x["page"]) | drawer),
                    RunnableLambda(lambda x: None)
                ),
                "audio": RunnableLambda(lambda x: {"description": x["page"]["description"], "action": x["action"], "page_number": x["page_number"]}) | speaker,
            }
        )
        return chain

    @classmethod
    def _build_writer(cls, config: ConfigParser, prompt_replace: dict = {}) -> RunnableSequence:
        # Writer Prompt
        task = _Prompts.get_prompt("writer_task", prompt_replace)
        rules = _Prompts.get_prompt("writer_rules", prompt_replace)
        personality = _Prompts.get_prompt("writer_knowledge", prompt_replace)
        output_format = _Prompts.get_prompt("writer_output_format", prompt_replace)
        ends = _Prompts.get_prompt("writer_ends", prompt_replace)
        messages = [
            ("system",
                "[task]: " + task + "\n"
                "[rules]: " + rules + "\n"
                "[personality]: " + personality + "\n"
                "[output_format]: " + output_format + "\n"
                "[context]: {context}\n"
                "[ends]: " + ends + "\n"
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
    def _build_drawer(cls, config: ConfigParser, prompt_replace: dict = {}, chain_id: Optional[str] = None) -> RunnableSequence:
        # Drawer Prompt
        drawer_task = _Prompts.get_prompt("drawer_task", prompt_replace)
        # Drawer Chain
        prompter_model = config.get("drawer", "prompter_model", fallback="gpt-4")
        prompter_temperature = float(config.get("drawer", "prompter_temperature", fallback="0.0"))
        drawer_model = config.get("drawer", "drawer_model", fallback="dall-e-3")
        size = config.get("drawer", "image_size", fallback="1024x1024")
        quality = config.get("drawer", "image_quality", fallback="standard")
        download = config.get("drawer", "download", fallback="disable")
        output_folder = config.get("drawer", "data", fallback="./tmp/images")

        drawer = (
            ChatPromptTemplate.from_template(drawer_task)
            | ChatOpenAI(
                model=prompter_model, temperature=prompter_temperature
            )
            | StrOutputParser()
            | {
                "url": RunnableLambda(_dalle3_generator(model=drawer_model, size=size, quality=quality, download=download, output_folder=output_folder, chain_id=chain_id)),
                "description": RunnablePassthrough(),
            }
        )
        return drawer

    @classmethod
    def _build_speaker(cls, config: dict, prompt_replace: dict = {}, chain_id: Optional[str] = None) -> RunnableSequence:

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
            | {
                "path": RunnableLambda(_gcp_tts_generator(voice=voice, language=language, output_folder=output_folder, chain_id=chain_id)),
                "speech": RunnableLambda(lambda x: x.text),
            }
        )
        return speaker
