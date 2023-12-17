from typing import List, Optional
import logging

# from story_teller.story.path import Path
from story_teller.app.base import (
    AlertSystemEvent, ChoiceInputEvent, TextInputEvent, QuitEvent,
    Event, StateMachine, State,
    RenderData, RenderSceneData, RenderHUDData, RenderControlsData,
    RenderSceneLayoutType,
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
        self._title = "Story Teller - Choose Your Own Adventure"
        self._description_placeholder = "Enter a description..."
        self._choices = {
            "start": {
                "text": "Start",
                "enabled": False,
            },
            "change_story": {
                "text": "Change Story",
                "enabled": True,
            },
        }
        self._description = None
        self._ready = False
        self._alert = None

    def on_enter(self):
        """Enter the state.

        This method is called when the state is entered.
        """
        logger.info("Entering title state.")
        # story_tree = self._state_machine.context.story_tree
        # self._state_machine.context.current_path = Path(story_tree)
        # logger.info(f"Creating path from story tree {story_tree}.")
        self._choices["start"]["enabled"] = True

    def on_exit(self):
        """Exit the state.

        This method is called when the state is exited.
        """
        logger.info("Exiting title state.")

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
                description=self._description or self._description_placeholder,
            ),
            hud=RenderHUDData(
                karma={},  # TODO
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
            if isinstance(event, ChoiceInputEvent):
                # TODO: Handle choice input event.
                pass
            elif isinstance(event, TextInputEvent):
                # TODO: Handle text input event.
                pass
            elif isinstance(event, QuitEvent):
                self._state_machine.end()
            elif isinstance(event, AlertSystemEvent):
                self._alert = event.content
