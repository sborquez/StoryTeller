from typing import Dict
from story_teller.app.base import State


class StateRegistry:
    """States registry class.

    This class is used to register the states.
    """

    _STATES: Dict[str, State] = {}

    @staticmethod
    def register(name: str, state: State) -> None:
        """Register a state.

        Args:
            state (State): The state to register.
        """
        StateRegistry._STATES[name] = state

    @staticmethod
    def get(name: str) -> State:
        """Get a state.

        Args:
            name (str): The name of the state.

        Returns:
            State: The state.
        """
        return StateRegistry._STATES[name]


# Register states
from story_teller.app.states.title import TitleState  # noqa: F401, E402, E501
StateRegistry.register("TitleState", TitleState)

from story_teller.app.states.show import ShowState  # noqa: F401, E402, E501
StateRegistry.register("ShowState", ShowState)

from story_teller.app.states.interact import InteractState  # noqa: F401, E402, E501
StateRegistry.register("InteractState", InteractState)

from story_teller.app.states.game_over import GameOverState  # noqa: F401, E402, E501
StateRegistry.register("GameOverState", GameOverState)
