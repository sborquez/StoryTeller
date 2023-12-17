import logging
from typing import List  # , Optional

from story_teller.app.base import (
    StateMachine,
    Event,
    # AlertSystemEvent, ChoiceInputEvent, TextInputEvent, QuitEvent,
    State,
    RenderData,
    # RenderSceneData, RenderHUDData, RenderControlsData,
    # RenderSceneLayoutType,
)


logger = logging.getLogger(__name__)


class InteractState(State):
    """Interact state.

    This is the interact state. This state is used to interact with the user.
    """

    def __init__(self, state_machine: StateMachine) -> None:
        """Initialize the interact state.

        Args:
            state_machine (StateMachine): The state machine instance.
        """
        super().__init__(state_machine)
        self._title = "Story Teller - Choose Your Own Adventure"
        self._ready = False
        self._alert = None

    def on_enter(self) -> None:
        """Enter the state.

        This method is called when the state is entered.
        """
        logger.info("Entering interact state.")

    def on_exit(self) -> None:
        """Exit the state.

        This method is called when the state is exited.
        """
        logger.info("Exiting interact state.")

    def render(self) -> RenderData:
        """Render the state.

        This method is called when the state is rendered.

        Returns:
            RenderData: The render data.
        """
        pass

    def handle_events(self, events: List[Event]) -> State | None:
        return super().handle_events(events)
