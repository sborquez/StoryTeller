import time
from typing import Any, Dict, List

from colorama import just_fix_windows_console
from termcolor import colored

from story_teller.app.base import (
    App, Context, Event, RenderData,
    AlertSystemEvent, ChoiceInputEvent, QuitEvent
)
from story_teller.app.states import TitleState
from story_teller.story.tree import StoryTreeFactory


class CLIApp(App):
    """CLI App class.

    This is the user interface for the CLI version of the app.
    """

    WIDTH = 80
    HEIGHT = 24

    def __init__(self, context: Context) -> None:
        """Initialize the CLI app."""
        super().__init__(context)

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
        print("\033c", end="")

        # DEBUG
        return

        # Print the credits in the center (horizontal and vertical)
        # of the screen and in green
        credits = "Story Teller by Sebastián Bórquez"
        # Rotating loading animation in the center (horizontal and vertical)
        # below the credits
        loading = ".--^^--."
        print("\n" * (self.HEIGHT//2 - 1))
        print(colored(credits.center(self.WIDTH), "black", "on_cyan"))
        print()
        print("Loading".center(self.WIDTH))
        print()
        print("\n" * (self.HEIGHT//2 - 3))
        move_up = "\033[F" * (self.HEIGHT//2 - 3)
        print(move_up, end="")
        for _ in range(int(len(loading) * 2.5)):
            print("\033[F", end="")
            print(loading.center(self.WIDTH))
            time.sleep(.25)
            loading = loading[1:] + loading[0]
        # Clean up the loading animation
        print("\033[F", end="")
        print(" " * self.WIDTH, end="")
        print("\033[F"*2, end="")
        print("Done!".center(self.WIDTH))
        print()
        print("Press any key to continue...".center(self.WIDTH))
        print("\n" * (self.HEIGHT//2 - 1))
        input()

    def _loop(self) -> None:
        """Quit the CLI app.

        This method is used to quit the CLI app.
        """
        while self._running and not self._state_machine.in_end_state:
            render_data = self._state_machine.get_render_data()
            self._render(render_data)
            choices = []
            for choice_name, choice_text, choice_enabled in zip(
                render_data.controls.choices_name,
                render_data.controls.choices_text,
                render_data.controls.choices_enabled,
            ):
                if not choice_enabled:
                    continue
                choices.append((len(choices) + 1, choice_name, choice_text))
            if choices:
                events = self._get_user_choice(choices)
            else:
                raise NotImplementedError
            self._state_machine.handle_events(events)
            time.sleep(.1)

    def _clean_up(self) -> None:
        """Clean up the CLI app.

        This method is used to stop the CLI app.
        """
        pass

    def _get_user_choice(self, choices: List[tuple]) -> List[Event]:
        """Get the events.

        This method is used to get the events from the user input.

        Returns:
            List[Event]: A list of events.
        """
        user_input = input().strip().lower()
        if user_input == "q":
            return [QuitEvent()]
        elif user_input == "":
            return []
        elif user_input in [str(choice[0]) for choice in choices]:
            choice_name = choices[int(user_input) - 1][1]
            return [ChoiceInputEvent(choice_name)]
        else:
            return [AlertSystemEvent("Invalid choice")]

    def _render(self, render_data: RenderData) -> None:
        print("\033c", end="")
        print(render_data.layout)
        print(render_data.scene)
        print(render_data.controls)
        print(render_data.hud)


class CLIAppFactory:

    DEFAULT_SETTINGS = {
        "story_file": None,
    }

    @classmethod
    def from_settings(cls, settings: Dict[str, Any]) -> CLIApp:
        """Build the CLI app.

        This method is used to build the CLI app.

        Returns:
            CLIApp: The CLI app.
        """
        story_file = settings.get("story_file", None)
        if story_file is None:
            story_tree = StoryTreeFactory.create_empty()
        else:
            story_tree = StoryTreeFactory.from_json(story_file)

        context = Context(
            story_tree=story_tree,
            current_path=None,
        )
        return CLIApp(context)

    @classmethod
    def from_scratch(cls) -> CLIApp:
        """Build the CLI app from scratch.

        This method is used to build the CLI app from scratch.

        Returns:
            CLIApp: The CLI app.
        """
        settings = cls.DEFAULT_SETTINGS
        app = cls.build_from_settings(settings)
        return app


if __name__ == "__main__":
    import os

    # Get the story file path in the test directory
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    story_file = os.path.join(root_dir, "tests", "data", "sample.json")

    settings = {
        "story_file": story_file,
    }
    app = CLIAppFactory.from_settings(settings)
    app.run()
