import logging
import random
from typing import List, Optional

from story_teller.app.base import (
    StateMachine, State,
    Event, AlertSystemEvent, ChoiceInputEvent, TextInputEvent, QuitEvent,
    RenderData, RenderSceneData, RenderHUDData, RenderControlsData,
    RenderSceneLayoutType,
)
from story_teller.app.states import StateRegistry
from story_teller.story.page import Page, PageType, Description
from story_teller.story.path import Path
from story_teller.story.tree import StoryTree, StoryTreeFactory


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

        story_tree = self._state_machine.context.story_tree
        context_page = story_tree.get_context_page()

        if context_page is None:
            # if there are no story, force user to change story
            self._choices["start"]["enabled"] = False
            self._choices["change_story"]["enabled"] = False
            self._text_inputs["description"]["enabled"] = True
            self._ready = False
        else:
            self._choices["start"]["enabled"] = True
            self._choices["change_story"]["enabled"] = True
            self._text_inputs["description"]["enabled"] = False
            self._description = context_page.description.page
            self._ready = True

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
                image=None,
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

            # Choices events
            if isinstance(event, ChoiceInputEvent):
                match event.choice:
                    case "start":
                        logging.info("Starting story.")
                        if not self._ready:
                            raise RuntimeError("Title state not ready.")
                        # Start new path
                        self._state_machine.context.current_path = \
                            self._start_new_path(
                                self._state_machine.context.story_tree,
                            )
                        next_state = StateRegistry.get("ShowState")
                        return next_state(self._state_machine)
                    case "change_story":
                        logging.info("Changing story.")
                        self._choices["change_story"]["enabled"] = False
                        self._choices["start"]["enabled"] = False
                        self._text_inputs["description"]["enabled"] = True
                        return None

            # Text input events
            elif isinstance(event, TextInputEvent):
                if event.text == "":
                    self._alert = "Please enter a non-empty description."
                    return None
                self._choices["change_story"]["enabled"] = True
                self._choices["start"]["enabled"] = True
                self._description = event.text
                self._text_inputs["description"]["enabled"] = False
                self._ready = True
                # Modify story tree
                self._state_machine.context.story_tree = \
                    self._get_new_story_tree(event.text)

            # Exit event
            elif isinstance(event, QuitEvent):
                self._state_machine.end()
                return None

            # System events
            elif isinstance(event, AlertSystemEvent):
                self._alert = event.content

    @staticmethod
    def _get_new_story_tree(description: str) -> StoryTree:
        """Get a new story tree."""
        story_tree = StoryTreeFactory.from_scratch()
        story_tree.add_page(
            page=Page(
                page_type=PageType.CONTEXT,
                description=Description(page=description),
            ),
        )
        return story_tree

    @staticmethod
    def _start_new_path(story_tree: StoryTree) -> Path:
        """Get a new path."""
        new_path = Path(story_tree)
        # TODO: move this responsibility to Teller
        actions = new_path.view_action_options()
        if len(actions) == 0:
            raise RuntimeError("No action available.")
        selected = random.choice(list(actions.keys()))
        new_path.take_action(selected)
        return new_path
