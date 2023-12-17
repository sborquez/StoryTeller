from typing import List, Optional
import logging

# from story_teller.story.path import Path
from story_teller.app.base import (
    StateMachine,
    Event, AlertSystemEvent, ChoiceInputEvent, TextInputEvent, QuitEvent,
    State,
    RenderData, RenderSceneData, RenderHUDData, RenderControlsData,
    RenderSceneLayoutType,
)
from story_teller.app.states.show import ShowState


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
        self._description_placeholder = \
            "You can't start a story without a description!\n" \
            "Write a short starting description for your story."
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
        self._text_inputs = {
            "description": {
                "placeholder": "Enter your story description...",
                "enabled": False,
            }
        }
        self._description = None
        self._ready = False
        self._alert = None

    def on_enter(self):
        """Enter the state.

        This method is called when the state is entered.
        """
        logger.info("Entering title state.")
        # TODO: load story tree from file, if doesn't exist, disable start
        # story_tree = self._state_machine.context.story_tree
        # self._state_machine.context.current_path = Path(story_tree)
        # logger.info(f"Creating path from story tree {story_tree}.")

        # if there are no story, force user to change story
        self._choices["start"]["enabled"] = False
        self._choices["change_story"]["enabled"] = False
        self._text_inputs["description"]["enabled"] = True

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
                text_input_target=[
                    text_input for text_input in self._text_inputs.keys()
                ],
                text_input_placeholder=[
                    text_input["placeholder"]
                    for text_input in self._text_inputs.values()
                ],
                text_input_enabled=[
                    text_input["enabled"]
                    for text_input in self._text_inputs.values()
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
                match event.choice:
                    case "start":
                        logging.info("Starting story.")
                        if not self._ready:
                            raise RuntimeError("Title state not ready.")
                        return ShowState(self._state_machine)
                    case "change_story":
                        logging.info("Changing story.")
                        self._choices["change_story"]["enabled"] = False
                        self._choices["start"]["enabled"] = False
                        self._text_inputs["description"]["enabled"] = True
                        return None
            elif isinstance(event, TextInputEvent):
                if event.text == "":
                    self._alert = "Please enter a non-empty description."
                    return None
                self._choices["change_story"]["enabled"] = True
                self._choices["start"]["enabled"] = True
                # TODO: Modify story tree
                self._description = event.text
                self._text_inputs["description"]["enabled"] = False
                self._ready = True
            elif isinstance(event, QuitEvent):
                self._state_machine.end()
                return None
            elif isinstance(event, AlertSystemEvent):
                self._alert = event.content
