from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from story_teller.story.app.state_machine import StateMachine, Event


class State(ABC):
    """State Machine base class.

    This class is the base class for all states. It provides the basic
    functionality for the state machine. The state machine is app agnostic,
    so it can be used with the PyGame GUI or the CLI NoGUI.
    """

    def __init__(self, state_machine: StateMachine) -> None:
        """Initialize the state machine.

        Args:
            state_machine (StateMachine): The state machine instance.
        """
        self._state_machine = state_machine

    @abstractmethod
    def on_enter(self):
        """Enter the state.

        This method is called when the state is entered.
        """
        pass

    @abstractmethod
    def on_exit(self):
        """Exit the state.

        This method is called when the state is exited.
        """
        pass

    @abstractmethod
    def update(self):
        """Update the state.

        This method is called when the state is updated.
        """
        pass

    @abstractmethod
    def render(self) -> Dict[str, Any]:
        """Render the state.

        This method is called when the state is rendered.

        Returns:
            Dict[str, Any]: The render data.
        """
        pass

    @abstractmethod
    def handle_events(self, events: List[Event]) -> Optional[State]:
        """Handle events.

        This method is called when the state is handling events.

        Args:
            events (list): A list of events.
        """
        pass
