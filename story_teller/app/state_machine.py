from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import pydantic

from story_teller.story.tree import StoryTree
from story_teller.story.path import Path
from story_teller.app.states import State


class Context(pydantic.BaseModel):
    """Context class.

    This class is used to represent the context or shared data between the
    states. For example, the context can contain the story tree, the current
    path, etc.
    """
    story_tree: StoryTree
    current_path: Optional[Path] = None
    # TODO: Add more context data
    # learner: Learner
    # writer: Writer
    # drawer: Drawer


class Event(ABC):
    """Event class.

    This class is used to represent an event.
    """


class TextInputEvent(Event):
    """Text input event class.

    This class is used to represent a text input event.
    """

    def __init__(self, text: str) -> None:
        """Initialize the text input event.

        Args:
            text (str): The text input.
        """
        self.text = text


class ChoiceInputEvent(Event):
    """Choice input event class.

    This class is used to represent a choice input event.
    """

    def __init__(self, choice: str, choices: Dict[str, Any]) -> None:
        """Initialize the choice input event.

        Args:
            choice (str): The choice input.
        """
        self.choice = choice
        self.choices = choices


class QuitEvent(Event):
    """Quit event class.

    This class is used to represent a quit event.
    """

    def __init__(self) -> None:
        """Initialize the quit event."""
        pass


class StateMachine:
    """State Machine for the app.

    This class is inherited by the PyGame GUI and the CLI NoGUI concrete state
    machines, and provides to the story teller the user interface control.
    """

    def __init__(self, context: Context) -> None:
        """Initialize the state machine.

        Args:
            initial_state (State): The initial state.
        """
        self.current_state = None
        self.context = context

    def set_initial_state(self, initial_state: State) -> None:
        """Set the initial state.

        Args:
            initial_state (State): The initial state.
        """
        self.current_state = initial_state
        self.current_state.on_enter()

    def change_state(self, new_state: State) -> None:
        """Change the current state.

        Args:
            new_state (State): The new state.
        """
        self.current_state.on_exit()
        self.current_state = new_state
        self.current_state.on_enter()

    def handle_events(self, events: List[Event] = []) -> bool:
        """Handle events.

        Args:
            events (list): A list of events.

        Returns:
            bool: True if the state has changed, False otherwise.
        """
        new_state = self.current_state.handle_events(events)
        if new_state is not None:
            self.change_state(new_state)
            return True
        return False

    def get_render_data(self) -> Dict[str, Any]:
        """Render the current state."""
        render_data = self.current_state.render()
        return render_data


class App(ABC):
    """App class.

    This class is used to represent an app.
    """

    def __init__(self, state_machine: StateMachine, context: Context) -> None:
        """Initialize the app."""
        self._running = False
        self._state_machine = state_machine
        self._context = context

    @abstractmethod
    def run(self) -> None:
        """Start the app."""
        self._running = True

    @abstractmethod
    def stop(self) -> None:
        """Stop the app."""
        self._running = False

    @abstractmethod
    def loop(self) -> None:
        """Loop the app."""
        while self._running:
            pass
