from __future__ import annotations
from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Any, Dict, List

import pydantic

from story_teller.story.tree import StoryTree
from story_teller.story.path import Path
from story_teller.story.app.states import State


class Context(pydantic.BaseModel):
    """Context class.

    This class is used to represent the context or shared data between the
    states. For example, the context can contain the story tree, the current
    path, etc.
    """
    story_tree: StoryTree
    current_path: Path
    # TODO: Add more context data
    # learner: Learner
    # writer: Writer
    # drawer: Drawer


class StateMachine(ABC):
    """State Machine base class.

    This class is inherited by the PyGame GUI and the CLI NoGUI concrete state
    machines, and provides to the story teller the user interface control.
    """

    def __init__(self, initial_state: State, context: Context) -> None:
        """Initialize the state machine.

        Args:
            initial_state (State): The initial state.
        """
        self.current_state = initial_state
        self.context = context
        self.current_state.on_enter()

    def change_state(self, new_state: State) -> None:
        """Change the current state.

        Args:
            new_state (State): The new state.
        """
        self.current_state.on_exit()
        self.current_state = new_state
        self.current_state.on_enter()

    def handle_events(self, events: List[Event]) -> bool:
        """Handle events.

        Args:
            events (list): A list of events.
        """
        new_state = self.current_state.handle_events(events)
        if new_state is not None:
            self.change_state(new_state)
            return True
        return False

    def update(self) -> None:
        """Update the current state."""
        self.current_state.update()

    @abstractmethod
    def render(self) -> None:
        """Render the current state."""
        render_data = self.current_state.render()
        print(render_data)

    @abstractmethod
    def get_events(self) -> List[Event]:
        """Get events.

        Returns:
            list: A list of events.
        """
        pass


class EventType(StrEnum):
    """All supported events."""
    # TODO: Add all supported events
    ...


class Event(pydantic.BaseModel):
    """Event class.

    This class is used to represent an event.
    """

    event_type: EventType
    payload: Dict[str, Any]
