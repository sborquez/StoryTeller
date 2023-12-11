from typing import Any, Dict, List, Optional
import logging

from story_teller.story.path import Path
from story_teller.app.state_machine import StateMachine, Event
from story_teller.app.states import State
from story_teller.app.state_machine import (
    Event, TextInputEvent, ChoiceInputEvent
)


logger = logging.getLogger(__name__)


class TitleState(State):
    """Title state.

    This is the title state. It is the first state that is shown to the user.
    """

    def __init__(self, state_machine: StateMachine) -> None:
        """Initialize the title state.

        Args:
            state_machine (StateMachine): The state machine instance.
        """
        super().__init__(state_machine)
        self._title = "Story Teller"
        self._description_placeholder = "Enter a description..."
        self._choices = {
            "start": "Start",
            "change_story": "Change Story",
            "quit": "Quit"
        }
        self._description = None
        self._ready = False

    def on_enter(self):
        """Enter the state.

        This method is called when the state is entered.
        """
        logger.info("Entering title state.")
        story_tree = self._state_machine.context.story_tree


    def on_exit(self):
        """Exit the state.

        This method is called when the state is exited.
        """
        logger.info("Exiting title state.")
        story_tree = self._state_machine.context.story_tree
        self._state_machine.context.current_path = Path(story_tree)
        logger.info(f"Creating path from story tree {story_tree}.")

    def render(self) -> Dict[str, Any]:
        """Render the state.

        This method is called when the state is rendered.

        Returns:
            Dict[str, Any]: The render data.
        """
        return {
            "title": self._title,
            "description_placeholder": self._description_placeholder,
            "choices": self._choices,
            "description": self._description,
            "ready": self._ready
        }

    def handle_events(self, events: List[Event] = []) -> Optional[State]:
        """Handle events.

        Args:
            events (list): A list of events.

        Returns:
            State: The new state.
        """
        pass
