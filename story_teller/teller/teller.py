from typing import Any
from configparser import ConfigParser


class Teller:
    """Entry point for the story teller."""

    def __init__(self, writer: Any, learner: Any,
                 drawer: Any, repository: Any) -> None:
        """Initialize the story teller.

        Args:
            writer (Any): Generative model for writing pages and images
                descriptions.
            learner (Any): Best story path generator, learns from user
                feedback how to generate the best story.
            drawer (Any): Generative model for drawing images.
            repository (Any): Media repository, stores and retrieves images
                from storage.
        """
        self._writer = writer
        self._learner = learner
        self._drawer = drawer
        self._repository = repository


class TellerFactory:
    """Teller factory class.

    This class is used to create a new teller.
    """

    @classmethod
    def from_config(cls, config: ConfigParser) -> Teller:
        """Create a new teller.

        Args:
            config (ConfigParser): The configuration parser instance.

        Returns:
            Teller: A new teller instance.
        """

    @classmethod
    def from_scratch() -> Teller:
        """Create a new teller.

        Returns:
            Teller: A new teller instance.
        """
