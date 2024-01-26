from configparser import ConfigParser
import time
from typing import List

from colorama import just_fix_windows_console
from termcolor import colored

from story_teller.app.base import (
    App, AppFactory, Context,
    Event, AlertSystemEvent, ChoiceInputEvent, TextInputEvent, QuitEvent,
    RenderData, RenderControlsData, RenderSceneLayoutType,
)
from story_teller.app.states.title import TitleState
from story_teller.story.tree import StoryTreeFactory


class CLIApp(App):
    """CLI App class.

    This is the user interface for the CLI version of the app.
    """

    def __init__(self, context: Context, width: int, height: int) -> None:
        """Initialize the CLI app."""
        super().__init__(context)
        self.WIDTH = width
        self.HEIGHT = height

    def run(self) -> None:
        """Run the CLI app.

        This method is used to run the CLI app.
        """
        title_state = TitleState(self._state_machine)
        self._state_machine.push(title_state)
        self._start()
        try:
            self._loop()
        except KeyboardInterrupt:
            pass
        self._clean_up()

    def _start(self) -> None:
        """Start the CLI app.

        This method is used to start the CLI app.
        """
        self._running = True
        # use Colorama to make Termcolor work on Windows too
        just_fix_windows_console()

        # Clear the screen
        self._clear_screen()

        # DEBUG
        if os.getenv("STORYTELLER_DEBUG", "false").lower() == "true":
            print("DEBUG MODE... skipping intro...")
            time.sleep(1)
            return
        self._render_intro()

    def _loop(self) -> None:
        """Quit the CLI app.

        This method is used to quit the CLI app.
        """
        while self._running and not self._state_machine.in_end_state:
            render_data = self._state_machine.get_render_data()
            try:
                self._render(render_data)
                events = []
                events += self._get_system_events(render_data.layout)
                events += self._get_user_choice(render_data.controls)
                events += self._get_user_text_input(render_data.controls)
            except KeyboardInterrupt:
                events = [QuitEvent()]

            self._state_machine.handle_events(events)
            time.sleep(.1)

    def _clean_up(self) -> None:
        """Clean up the CLI app.

        This method is used to stop the CLI app.
        """
        self._clear_screen()
        print(colored("Goodbye! thanks for playing!", "black", "on_green"))

    def _get_system_events(self, layout: RenderSceneLayoutType) -> List[Event]:
        match layout:
            case RenderSceneLayoutType.MAIN:
                return []
            case RenderSceneLayoutType.INTERACTION:
                return []
            case RenderSceneLayoutType.MOVIE:
                return [AlertSystemEvent("ready", "trigger")]

    def _get_user_choice(self, control: RenderControlsData) -> List[Event]:
        """Get the events.

        This method is used to get the events from the user choice input.

        Returns:
            List[Event]: A list of events.
        """
        choices = []
        for name, enabled in zip(
            control.choices_name,
            control.choices_enabled,
        ):
            if not enabled:
                continue
            choices.append(name)
        if not choices:
            return []
        user_input = input(colored("Choice:", "black", "on_yellow") + " ")
        user_input = user_input.strip()
        if user_input == "":
            return []
        elif user_input.isdigit() and 1 <= int(user_input) <= len(choices):
            choice_name = choices[int(user_input) - 1]
            return [ChoiceInputEvent(choice_name)]
        else:
            return [AlertSystemEvent("Invalid choice", "error")]

    def _get_user_text_input(self, control: RenderControlsData) -> List[Event]:
        """Get the events.

        This method is used to get the events from the user text input.

        Returns:
            List[Event]: A list of events.
        """
        text_input_events = []
        for target, enabled in zip(
            control.text_input_target,
            control.text_input_enabled,
        ):
            if not enabled:
                continue
            user_input = input(
                colored(f"Text [{target}]:", "black", "on_yellow") + " "
            )
            user_input = user_input.strip()
            text_input_events.append(
                TextInputEvent(target, user_input)
            )
        return text_input_events

    def _render(self, render_data: RenderData) -> None:
        """Render the render data.

        This method is used to render the render data.

        Args:
            render_data (RenderData): The render data.
        """
        self._clear_screen()
        match render_data.layout:
            case RenderSceneLayoutType.MAIN:
                self._render_main_layout(render_data)
            case RenderSceneLayoutType.INTERACTION:
                self._render_interaction(render_data)
            case RenderSceneLayoutType.MOVIE:
                self._render_movie(render_data)
            case _:
                raise NotImplementedError

    def _clear_screen(self) -> None:
        """Clean the screen.

        This method is used to clean the screen.
        """
        print("\033c", end="")

    def _show_title_ui(self, render_data: RenderData) -> None:
        title = render_data.scene.title
        print(colored(title.center(self.WIDTH), "black", "on_cyan"))

    def _show_alert_ui(self, render_data: RenderData) -> None:
        alert = render_data.hud.alert
        if alert is not None:
            print(colored(alert.center(self.WIDTH), "black", "on_red"))

    def _show_karma_ui(self, render_data: RenderData) -> None:
        karma = render_data.hud.karma
        karma_text = ""
        for name, value in karma.items():
            karma_text += f"{name}: {value:.2f} "
        print(colored(karma_text.center(self.WIDTH), "black", "on_light_grey"))

    def _show_description_ui(self, render_data: RenderData) -> None:
        # Split the description into lines, with padding two spaces
        # on the left and right.
        description = render_data.scene.description
        description = description.replace("\n\n", "\n\t\n")
        description_lines = description.split("\n")
        print(colored(self.WIDTH * "*", 'cyan'))
        for description_line in description_lines:
            for i in range(0, len(description_line), self.WIDTH - 4):
                line = description_line[i:i + self.WIDTH - 4]
                line = colored("* ", 'cyan') \
                    + line.strip().center(self.WIDTH - 4) \
                    + colored(" *", 'cyan')
                print(line)
        print(colored(self.WIDTH * "*", 'cyan'))

    def _show_control_ui(self, render_data: RenderData) -> None:
        controls = render_data.controls
        controls_title = colored(self.WIDTH * "-", "cyan") + "\n"
        control_title_content = ''
        if sum(controls.choices_enabled) > 0:
            control_title_content += \
                f"{colored('Choice', 'black', 'on_yellow')}" \
                " one " \
                f"{colored('<option>', 'red')}"
        if sum(controls.text_input_enabled) > 0:
            if control_title_content:
                control_title_content += " and "
            control_title_content += \
                f"{colored('Type', 'black', 'on_yellow')}" \
                " the " \
                f"{colored('<text>', 'red')}"
        if not control_title_content:
            control_title_content += "No options"
        controls_title += control_title_content.center(self.WIDTH) + "\n"
        controls_title += colored(self.WIDTH * "-", "cyan")
        print(controls_title)

        # The controls are rendered in the bottom of the screen
        # with the format:
        #  --------------------
        #   <1>. Choice 1
        #   <2>. Choice 2
        #   ...
        #   [text] Text placeholder
        #  --------------------
        control_lines = []
        i = 0
        for enabled, text in zip(
            controls.choices_enabled,
            controls.choices_text,
        ):
            if not enabled:
                continue
            i += 1
            control_lines.append(
                f"{colored(f'{i}', 'red')}. {text}"
            )
        for target, enabled, placeholder in zip(
            controls.text_input_target,
            controls.text_input_enabled,
            controls.text_input_placeholder,
        ):
            if not enabled:
                continue
            control_lines.append(
                f"[{colored(target, 'red')}]: {placeholder}"
            )

        for line in control_lines:
            print(line)
        print(colored(self.WIDTH * "-", "cyan"))

    def _render_intro(self) -> None:
        # Print the credits in the center (horizontal and vertical)
        # of the screen and in green
        credits = "Story Teller by Sebastián Bórquez"
        # Rotating loading animation in the center (horizontal and vertical)
        # below the credits
        loading = ".--^^--."
        print("\n" * (self.HEIGHT // 2 - 1))
        print(colored(credits.center(self.WIDTH), "black", "on_cyan"))
        print()
        print("Loading".center(self.WIDTH))
        print()
        print("\n" * (self.HEIGHT // 2 - 3))
        move_up = "\033[F" * (self.HEIGHT // 2 - 3)
        print(move_up, end="")
        for _ in range(int(len(loading) * 2.5)):
            print("\033[F", end="")
            print(loading.center(self.WIDTH))
            time.sleep(.25)
            loading = loading[1:] + loading[0]
        # Clean up the loading animation
        print("\033[F", end="")
        print(" " * self.WIDTH, end="")
        print("\033[F" * 2, end="")
        print("Done!".center(self.WIDTH))
        print()
        print("Press [Enter] to continue...".center(self.WIDTH))
        print("\n" * (self.HEIGHT // 2 - 1))
        input()

    def _render_main_layout(self, render_data: RenderData) -> None:

        # Title UI
        self._show_title_ui(render_data)

        # Alerts UI
        self._show_alert_ui(render_data)

        # Description UI
        self._show_description_ui(render_data)

        # Control UI
        self._show_control_ui(render_data)

    def _render_movie(self, render_data: RenderData) -> None:
        # Title UI
        self._show_title_ui(render_data)

        # Alerts UI
        self._show_alert_ui(render_data)

        # Karma UI
        self._show_karma_ui(render_data)

        # Description UI
        self._show_description_ui(render_data)

        # Wait for the user to press enter
        input(
            colored("Press [Enter] to continue...", "black", "on_yellow")
            .center(self.WIDTH)
        )

    def _render_interaction(self, render_data: RenderData) -> None:
        # Title UI
        self._show_title_ui(render_data)

        # Alerts UI
        self._show_alert_ui(render_data)

        # Karma UI
        self._show_karma_ui(render_data)

        # Description UI
        self._show_description_ui(render_data)

        # Control UI
        self._show_control_ui(render_data)


class CLIAppFactory(AppFactory):

    DEFAULT_CONFIG = {
        "width": 80,
        "height": 24,
    }

    @classmethod
    def from_config(cls, config: ConfigParser) -> CLIApp:
        """Build the CLI app.

        This method is used to build the CLI app.

        Args:
            config:

        Returns:
            CLIApp: The CLI app.
        """
        context = Context.from_config(config)
        width = config.getint("cli", "width", fallback=cls.DEFAULT_CONFIG["width"])
        height = config.getint("cli", "height", fallback=cls.DEFAULT_CONFIG["height"])
        return CLIApp(context, width, height)

    @classmethod
    def from_scratch(cls) -> CLIApp:
        """Build the CLI app from scratch.

        This method is used to build the CLI app from scratch.

        Returns:
            CLIApp: The CLI app.
        """
        raise NotImplementedError


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    # Load configuration
    load_dotenv()
    # config = ConfigParser()
    config = ConfigParser(os.environ)
    if os.path.exists(os.getenv("STORYTELLER_CONFIG_FILE")):
        config.read(os.getenv("STORYTELLER_CONFIG_FILE"))
    else:
        print("No config file found, using default settings")

    app = CLIAppFactory.from_config(config)
    app.run()
