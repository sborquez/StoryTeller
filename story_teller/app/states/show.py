import logging
from typing import List, Optional

from story_teller.app.base import (
    StateMachine, State,
    Event,
    AlertSystemEvent, QuitEvent,
    RenderData,
    RenderSceneLayoutType, RenderSceneData, RenderHUDData, RenderControlsData,
)
from story_teller.app.states import StateRegistry


logger = logging.getLogger(__name__)


class ShowState(State):
    """Show state.

    This is the show state. This state only shows information
    to the user with no user interaction.
    """

    def __init__(self, state_machine: StateMachine) -> None:
        """Initialize the show state.

        Args:
            state_machine (StateMachine): The state machine instance.
        """
        super().__init__(state_machine)
        self._title = "Story Teller - Instructions"
        # The game instructions
        self._description = """
        This is a story telling game. You can construct your own story by
        choosing the next action. The story will be created based on your
        choices.

        -o-

        You can choose between two actions created by the AI. The AI will
        create the actions based on your previous choices.

        -o-

        Keep an eye on your karma. It will determine the outcome of your
        story, so choose wisely.

        -o-

        Good luck!
        """
        self._ready = False
        self._alert = None

        self._karma = {}

    def on_enter(self) -> None:
        """Enter the state.

        This method is called when the state is entered.
        """
        logger.info("Entering show state.")
        self._karma = self._state_machine\
            .context \
            .current_path \
            .compute_karma() \
            .to_dict()

    def on_exit(self) -> None:
        """Exit the state.

        This method is called when the state is exited.
        """
        logger.info("Exiting show state.")

    def render(self) -> RenderData:
        """Render the state.

        This method is called when the state is rendered.

        Returns:
            RenderData: The render data.
        """
        alert = self._alert
        self._alert = None
        return RenderData(
            layout=RenderSceneLayoutType.MOVIE,
            scene=RenderSceneData(
                title=self._title,
                description=self._description,
                image=None,
            ),
            hud=RenderHUDData(
                karma=self._karma,
                alert=alert,
            ),
            controls=RenderControlsData(
                choices_name=[],
                choices_text=[],
                choices_enabled=[],
                text_input_target=[],
                text_input_placeholder=[],
                text_input_enabled=[],
            ),
        )

    def handle_events(self, events: List[Event]) -> Optional[State]:
        for event in events:
            if isinstance(event, AlertSystemEvent):
                if (event.type == AlertSystemEvent.Type.TRIGGER) \
                   and (event.content == "ready"):
                    self._ready = True
                    next_state = StateRegistry.get("InteractState")
                    return next_state(self._state_machine)
                elif event.type == AlertSystemEvent.Type.ERROR:
                    self._alert = event.message
                    return None
            elif isinstance(event, QuitEvent):
                self._state_machine.end()
                return None
