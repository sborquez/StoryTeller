from __future__ import annotations
from typing import Any
from configparser import ConfigParser

from story_teller.teller.chains import ChainBuilder, RunnableSequence


class Teller:
    """Entry point for the story teller."""

    def __init__(self, chain: RunnableSequence, learner: Any) -> None:
        """Initialize the story teller.

        Args:
            chain (RunnableSequence): A Chain for writing pages, audio and images
                with a generative model.
            learner (Any): Best story path generator, learns from user
                feedback how to generate the best story.
        """
        self._chain = chain
        self._learner = learner

    @classmethod
    def from_config(cls, config: ConfigParser) -> Teller:
        """Create a new teller.

        Args:
            config (ConfigParser): The configuration parser instance.

        Returns:
            Teller: A new teller instance.
        """

        return Teller(
            chain=ChainBuilder.from_config(config),
            learner=None,
        )
