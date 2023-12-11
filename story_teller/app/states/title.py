from typing import Any, Dict, List, Optional

from story_teller.app.states import State
from story_teller.story.app.state_machine import Event


class TitleState(State):
    """Title state.

    This is the title state. It is the first state that is shown to the user.
    """

    def on_enter(self):
        """Enter the state.

        This method is called when the state is entered.
        """
        pass

    def on_exit(self):
        """Exit the state.

        This method is called when the state is exited.
        """
        pass

    def update(self):
        """Update the state.

        This method is called when the state is updated.
        """
        pass

    def render(self) -> Dict[str, Any]:
        """Render the state.

        This method is called when the state is rendered.

        Returns:
            Dict[str, Any]: The render data.
        """
        pass

    def handle_events(self, events: List[Event]) -> Optional[State]:
        """Handle events.

        Args:
            events (list): A list of events.

        Returns:
            State: The new state.
        """
        pass
