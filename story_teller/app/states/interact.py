import logging
from typing import List

from story_teller.app.base import (
    StateMachine, State,
    Event,
    AlertSystemEvent, ChoiceInputEvent, QuitEvent,
    RenderData,
    RenderSceneData, RenderHUDData, RenderControlsData,
    RenderSceneLayoutType,
)
from story_teller.app.states import StateRegistry
from story_teller.story.page import PageType


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
        self._title = "[Action taken]"
        self._description = "[Page Description]"
        self._image = "[Image URL|Path]"
        self._page = None
        self._end_page = False
        self._alert = None
        self._choices = {
            "action1": {
                "text": "Action 1 Placeholder",
                "enabled": True,
            },
            "action2": {
                "text": "Action 2 Placeholder",
                "enabled": True,
            },
        }
        self._karma = {}

    def on_enter(self) -> None:
        """Enter the state.

        This method is called when the state is entered.
        """
        logger.info("Entering interact state.")
        self._page = self._state_machine\
            .context\
            .current_path\
            .get_current_page()
        # Update title
        if self._page.page_type == PageType.START:
            self._title = "Your story starts here!"
        else:
            self._title = f"Choice: {self._page.action}"

        # Update the next pages.
        if self._page.page_type == PageType.END:
            self._choices = {}
            self._layout = RenderSceneLayoutType.MOVIE
            self._end_page = True
        else:
            # TODO: Move this responsibility to the Teller.
            self._next_actions = self._state_machine\
                .context\
                .current_path\
                .view_action_options()\
                .keys()

            # Update the choices.
            self._choices = {}
            for action in self._next_actions:
                self._choices[action] = {
                    "text": action,
                    "enabled": True,
                }
            self._layout = RenderSceneLayoutType.INTERACTION
            self._end_page = False

        # Update the karma points.
        self._karma = self._state_machine\
            .context \
            .current_path \
            .compute_karma() \
            .to_dict()

        # Update the page description.
        self._description = self._page.description.page

    def on_exit(self) -> None:
        """Exit the state.

        This method is called when the state is exited.
        """
        logger.info("Exiting interact state.")
        if self._end_page:
            self._state_machine.context.current_path.finish()

    def render(self) -> RenderData:
        """Render the state.

        This method is called when the state is rendered.

        Returns:
            RenderData: The render data.
        """
        alert = self._alert
        self._alert = None
        return RenderData(
            layout=self._layout,
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
                    True for _ in self._choices.values()
                ],
                text_input_target=[],
                text_input_placeholder=[],
                text_input_enabled=[],
            ),
        )

    def handle_events(self, events: List[Event]) -> State | None:
        for event in events:
            if isinstance(event, AlertSystemEvent):
                if (event.type == AlertSystemEvent.Type.TRIGGER) \
                   and (event.content == "ready"):
                    next_state = StateRegistry.get("GameOverState")
                    return next_state(self._state_machine)
                elif event.type == AlertSystemEvent.Type.ERROR:
                    self._alert = event.content
                    return None

            # Choices events
            elif isinstance(event, ChoiceInputEvent):
                logging.info(f"Choice event: {event.choice}")
                self._state_machine\
                    .context\
                    .current_path\
                    .take_action(event.choice)
                return InteractState(self._state_machine)

            # Exit event
            elif isinstance(event, QuitEvent):
                self._state_machine.end()
                return None
