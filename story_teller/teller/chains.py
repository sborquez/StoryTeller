from configparser import ConfigParser
import uuid
import os

from google.cloud import texttospeech
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableBranch, RunnableSequence
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate


def _gcp_tts_generator(voice="en-US-Neural2-C", language="en-US", output_folder="./audio"):
    def generator(prompt):
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

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice_config, audio_config=audio_config
        )

        # The response's audio_content is binary.
        random_name = f"{str(uuid.uuid4())}.mp3"
        output_file = os.path.join(output_folder, random_name)
        with open(output_file, "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)
        return output_file
    return generator


class _Prompts:
    """Container for prompts. This class is used to store the default prompts
    and load them from the environment variables.
    """

    # Prompts components
    # Writter
    writer_task = """
    You are story writer. You help the user write a page of a story.
    The workflow of the story writing is the following:
    1. The first step is to understand the <context> for setting up a engaging story.
    2. The user will respond with the <action> he wants to take from the last page. If it is the first page, the action should be "start".
    3. Write the next page of the story for <action> taken by the user and the current <karma_points>, write the consecuence of the action and current state in the page's <description>, a list of 2 possible <next_action>s, and the <karma_points> change for the story.
    4. Repeat the step 2 and 3 until you reach the max length of the story. If you reach the ending page, there should be only one <next_action> with the "End" action.
    """

    writer_rules = """
    The writer rules are:
    1. The first page (number 1) of the story should always start by a "start" action. No other action is allowed.
    2. The last page (number MAX_PAGES) of the story should always end by one "End" next_action. No other next_action is allowed.
    3. An action is a string of max 30 characters, with only the description of the action.
    4. A description is a string of max 250 characters, with only the description of the page.
    5. The karma_points is a list of 4 float numbers, representing the karma points change for the story. The values are between -1 and 1. The sum of all karma points is the total karma points of the story. The karma points are:
    - The dimension of technology. Higher is more advanced. Lower is no technology.
    - The dimension of happiness. Higher is humans are happier. Lower is humans are unhappier.
    - The dimension of safety. Higher is humans are safer. Lower is humans doesn't exist.
    - The dimension of control. Higher is humans have more control. Lower is AGI has more control.
    6. The max length of the story is MAX_PAGES pages, so the last pages should end the story. Take in account the rythm of the story and the length of the pages, so the story is engaging.
    7. Use the JSON output format defined in the [output_format] section.
    """

    writer_output_format = """
    The output format is the following JSON keys:
    - "description": The description of the current page.
    - "next_actions": The list of the next actions. Each action is a string of max 30 characters.
    - "karma_points": A list of 4 float numbers, representing the karma points change for the story.
    """

    writer_knowledge = """
    The writer has the following knowledge for story inspiration:
    - The writer knows the following characters: "Sebastian", "Fran"
    - The story should by a "sci-fi" story, "utopia" or "dystopia".
    - Ispired by the following books: "1984", "Life 3.0: Alpha team tale"
    - Ispired by the following movies: "The Matrix", "The Terminator"
    - Ispired by the following games: "Detroit: Become Human", "Deus Ex"
    - Ispired by the following TV series: "Westworld", "Black Mirror"
    - Ispired by the following anime: "Ghost in the Shell", "Serial Experiments Lain"
    """

    # Drawer
    drawer_style = "90s aesthetics, with a dark and gritty style and pixel art graphics. Using the following colors: #000000, #ffffff, #ff0000, #00ff00, #0000ff, #ffff00, #ff00ff, #00ffff"

    drawer_task = """
    Generate a short prompt to generate an image based on:
    1. Scene description: {description}
    2. Use this style: STYLE
    3. Generate consistent images with this seed: [SEED]
    4. The length of the prompt should not be more than 1000 characters.
    5. Not render any text in the image!!!
    """

    @staticmethod
    def get_prompt(name: str, replace: dict = {}) -> str:
        """Get the prompt by name.

        Args:
            name (str): The name of the prompt.

        Returns:
            str: The prompt.
        """
        prompt = _Prompts.__dict__[name]
        for key, value in replace.items():
            prompt = prompt.replace(key, value)
        return prompt


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
        # TODO
        return None
        # chain = (
        #     RunnablePassthrough.assign(page=writer_chain)
        #     | {
        #         "page": RunnableLambda(lambda x: x["page"]),
        #         "image_url": RunnableLambda(lambda x: x["page"]) | image_generator,
        #         "audio_file": RunnableLambda(lambda x: {"description": x["page"]["description"], "action": x["action"], "page_number": x["page_number"]}) | audio_generator,
        #     }
        # )

    @classmethod
    def _build_writer(cls, writter_config: dict, chain_config: dict = {}) -> RunnableSequence:
        # Writer Prompt
        replace = {
            "MAX_PAGES": str(chain_config.get("max_pages", 5)),
        }
        task = _Prompts.get_prompt("writer_task", replace)
        rules = _Prompts.get_prompt("writer_rules", replace)
        knowledge = _Prompts.get_prompt("writer_knowledge", replace)
        output_format = _Prompts.get_prompt("writer_output_format", replace)
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
        model = writter_config.get("model", "gpt-4")
        temperature = writter_config.get("temperature", 0.9)
        writer_chain = (
            ChatPromptTemplate.from_messages(messages)
            | ChatOpenAI(model=model, temperature=temperature)
            | JsonOutputParser()
        )
        return writer_chain

    @classmethod
    def _build_image_generator(cls, image_generator_config: dict, chain_config: dict = {}) -> RunnableSequence:
        # Drawer Prompt
        drawer_style = _Prompts.get_prompt("drawer_style")
        drawer_seed = str(uuid.uuid4())[0:8]
        drawer_task = _Prompts.get_prompt(
            "drawer_task", {"STYLE": drawer_style, "SEED": drawer_seed}
        )
        # Drawer Chain
        prompter_model = image_generator_config.get("prompter_model", "gpt-4")
        prompter_temperature = image_generator_config.get("prompter_temperature", 0.0)
        drawer_model = image_generator_config.get("drawer_model", "dall-e-3")
        size = image_generator_config.get("image_size", "1024x1024")
        quality = image_generator_config.get("image_quality", "standard")

        image_generator = (
            ChatPromptTemplate.from_template(drawer_task)
            | ChatOpenAI(model=prompter_model, temperature=prompter_temperature)
            | StrOutputParser()
            | RunnableLambda(
                lambda x: DallEAPIWrapper(
                    model=drawer_model, size=size, quality=quality
                ).run(x))
        )
        return image_generator

    @classmethod
    def _build_audio_generator(cls, audio_generator_config: dict, chain_config: dict = {}) -> RunnableSequence:

        voice = audio_generator_config.get("voice", "en-US-Neural2-C")
        language = audio_generator_config.get("language", "en-US")
        output_folder = chain_config.get("tmp_data", "./tmp/audio")
        # max_pages = chain_config.get("max_pages", 5)

        audio_generator = (
            RunnableBranch(
                (lambda x: x["page_number"] == 1, PromptTemplate.from_template("{description}")),
                # (lambda x: x["page_number"] == max_pages, PromptTemplate.from_template("{description}")),
                PromptTemplate.from_template("You choose: {action}. {description}.")
            )
            | RunnableLambda(_gcp_tts_generator(voice, language, output_folder))
        )
        return audio_generator
