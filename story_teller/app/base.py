from __future__ import annotations
from abc import ABC, abstractmethod
from enum import StrEnum
from typing import Dict, List, Optional, NamedTuple


from story_teller.story.tree import StoryTree
from story_teller.story.path import Path


class Context(NamedTuple):
    """Context class.

    This class is used to represent the context or shared data between the
    states. For example, the context can contain the story tree, the current
    path, etc.
    """
    story_tree: StoryTree
    current_path: Optional[Path] = None

    # TODO: Add more context data
    # learner: Learner
    # writer: Writer
    # drawer: Drawer


class Event(ABC):
    """Event class.

    This class is used to represent an event.
    """


class TextInputEvent(Event):
    """Text input event class.

    This class is used to represent a text input event.
    """

    def __init__(self, target: str, text: str) -> None:
        """Initialize the text input event.

        Args:
            text (str): The text input.
        """
        self.target = target
        self.text = text


class ChoiceInputEvent(Event):
    """Choice input event class.

    This class is used to represent a choice input event.
    """

    def __init__(self, choice: str) -> None:
        """Initialize the choice input event.

        Args:
            choice (str): The choice input.
        """
        self.choice = choice


class AlertSystemEvent(Event):
    """Alert system event class.

    This class is used to represent an alert system event.
    """

    class Type(StrEnum):
        ERROR = "error"
        TRIGGER = "trigger"
        INFO = "info"

    def __init__(self, content: str, type: Type | str) -> None:
        """Initialize the alert system event.

        Args:
            content (str): The alert.
        """
        if isinstance(type, str):
            type = AlertSystemEvent.Type(type)
        self.type = type
        self.content = content


class QuitEvent(Event):
    """Quit event class.

    This class is used to represent a quit event.
    """

    def __init__(self) -> None:
        """Initialize the quit event."""
        pass


class RenderSceneLayoutType(StrEnum):
    """Render scene layout type class.

    This class is used to represent the render scene layout type.

    Description:
        MAIN: The main layout. The scene is rendered in the "center" of the
            UI, waiting for the user input.
        INTERACTION: The interaction layout. This is an composite layout,
            where the scene is rendered, with the HUD and waiting for the
            user input.
        MOVIE: The movie layout. This is only used for non-interactive scenes.
    """
    MAIN = "main"
    INTERACTION = "interaction"
    MOVIE = "movie"


class RenderSceneData(NamedTuple):
    """Render scene data class.

    This class is used to represent the render scene data.
    """
    title: str
    description: str
    # TODO: Add more scene data
    # image: str
    # audio: str
    # action: str


class RenderHUDData(NamedTuple):
    """Render HUD data class.

    This class is used to represent the render HUD data.
    """
    # TODO: Add more HUD data
    karma: Dict[str, float]
    alert: Optional[str]


class RenderControlsData(NamedTuple):
    """Render controls data class.

    This class is used to represent the render controls data.
    """
    choices_name: List[str]
    choices_text: List[str]
    choices_enabled: List[bool]

    text_input_target: List[str]
    text_input_placeholder: List[Optional[str]]
    text_input_enabled: List[bool]


class RenderData(NamedTuple):
    """Render data class.

    This class is used to represent the render data.
    """
    layout: RenderSceneLayoutType
    scene: RenderSceneData
    hud: RenderHUDData
    controls: RenderControlsData


class State(ABC):
    """State Machine base class.

    This class is the base class for all states. It provides the basic
    functionality for the state machine. The state machine is app agnostic,
    so it can be used with the PyGame GUI or the CLI NoGUI.
    """

    def __init__(self, state_machine: StateMachine) -> None:
        """Initialize the state machine.

        Args:
            state_machine (StateMachine): The state machine instance.
                It is used to push and pop states, and access the context.
        """
        self._state_machine = state_machine

    @abstractmethod
    def on_enter(self):
        """Enter the state.

        This method is called when the state is entered.
        """
        pass

    @abstractmethod
    def on_exit(self):
        """Exit the state.

        This method is called when the state is exited.
        """
        pass

    @abstractmethod
    def render(self) -> RenderData:
        """Render the state.

        This method is called when the state is rendered.

        Returns:
            RenderData: The render data.
        """
        pass

    @abstractmethod
    def handle_events(self, events: List[Event]) -> Optional[State]:
        """Handle events.

        This method is called when the state is handling events.

        Args:
            events (list): A list of events.
        """
        pass


class StateMachine:
    """State Machine for the app.

    This class is inherited by the PyGame GUI and the CLI NoGUI concrete state
    machines, and provides to the story teller the user interface control.
    """

    def __init__(self, context: Context) -> None:
        """Initialize the state machine.

        Args:
            initial_state (State): The initial state.
        """
        self.current_state = None
        self.in_end_state = False
        self.context = context

    def push(self, new_state: State) -> None:
        """Change the current state.

        Args:
            new_state (State): The new state.
        """
        if self.current_state is not None:
            self.current_state.on_exit()
        self.current_state = new_state
        self.current_state.on_enter()

    def handle_events(self, events: List[Event] = []) -> bool:
        """Handle events.

        Args:
            events (list): A list of events.

        Returns:
            bool: True if the state has changed, False otherwise.
        """
        new_state = self.current_state.handle_events(events)
        if new_state is not None:
            self.push(new_state)
            return True
        return False

    def get_render_data(self) -> RenderData:
        """Render the current state."""
        render_data = self.current_state.render()
        return render_data

    def end(self) -> None:
        """End the state machine."""
        if self.in_end_state:
            return
        if self.current_state is not None:
            self.current_state.on_exit()
        self.current_state = None
        self.in_end_state = True


class App(ABC):
    """App class.

    This class is used to represent an app.
    """

    def __init__(self, context: Context) -> None:
        """Initialize the app."""
        self._running = False
        self._context = context
        self._state_machine = StateMachine(context)

    @abstractmethod
    def run(self) -> None:
        """Start the app."""
        self._running = True

    @abstractmethod
    def _start(self) -> None:
        """Start the app."""
        pass

    @abstractmethod
    def _loop(self) -> None:
        """Loop the app."""
        while self._running:
            pass

    @abstractmethod
    def _clean_up(self) -> None:
        """Clean up the app."""
        pass
