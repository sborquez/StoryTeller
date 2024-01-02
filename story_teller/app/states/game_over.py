from typing import List, Optional
import logging

from story_teller.app.base import (
    StateMachine,
    Event,
    AlertSystemEvent, ChoiceInputEvent, QuitEvent,
    State,
    RenderData,
    RenderSceneData, RenderHUDData, RenderControlsData,
    RenderSceneLayoutType,
)
from story_teller.app.states.title import TitleState


logger = logging.getLogger(__name__)


class GameOverState(State):
    """Game Over state.

    This is the final state. This state is used to recieve feedback for the story.
    """

    def __init__(self, state_machine: StateMachine) -> None:
        """Initialize the game over state.

        Args:
            state_machine (StateMachine): The state machine instance.
        """
        super().__init__(state_machine)

        self._title = "Game Over"
        self._choices = {
            str(score): {"text": "Score: " + str(score), "enabled": True}
            for score in (-2, -1, 0, 1, 2)
        }
        self._description = None
        self._alert = None
        self._karma = {}

    def on_enter(self):
        """Enter the state.

        This method is called when the state is entered.
        """
        self._karma = self._state_machine.context.current_path.compute_karma()

    def on_exit(self):
        """Exit the state.

        This method is called when the state is exited.
        """
        logger.info("Exiting game over state.")
        # TODO: Teller should use the feedback to update the story tree
        self._state_machine.context.current_path = None

    def render(self) -> RenderData:
        """Render the state.

        This method is called when the state is rendered.

        Returns:
            RenderData: The render data.
        """
        alert = self._alert
        self._alert = None
        return RenderData(
            layout=RenderSceneLayoutType.MAIN,
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
                choices_name=[
                    choice for choice in self._choices.keys()
                ],
                choices_text=[
                    choice["text"] for choice in self._choices.values()
                ],
                choices_enabled=[
                    choice["enabled"] for choice in self._choices.values()
                ],
                text_input_target=[],
                text_input_placeholder=[],
                text_input_enabled=[],
            ),
        )

    def handle_events(self, events: List[Event] = []) -> Optional[State]:
        """Handle events.

        Args:
            events (list): A list of events.

        Returns:
            State: The new state.
        """
        for event in events:

            # Choices events
            if isinstance(event, ChoiceInputEvent):
                feedback = event.choice
                logging.info("Feedback submitted.")

                # Update the current path
                self._state_machine\
                    .context\
                    .current_path\
                    .feedback(feedback)

                # Go to start state
                self._state_machine\
                    .context\
                    .current_path\
                    .start()

                return TitleState(self._state_machine)

            # Exit event
            elif isinstance(event, QuitEvent):
                self._state_machine.end()
                return None

            # System events
            elif isinstance(event, AlertSystemEvent):
                self._alert = event.content
