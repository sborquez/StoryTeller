from __future__ import annotations
from enum import StrEnum
from typing import Optional
import uuid

import pydantic


class Image(pydantic.BaseModel):
    """Image for the page."""

    path: Optional[str] = pydantic.Field(default=None)
    url: Optional[str] = pydantic.Field(default=None)
    description: Optional[str] = pydantic.Field(default=None)

    def load(self):
        """Load the image from the path."""
        pass

    def save(self):
        """Save the image to the path."""
        pass


class Description(pydantic.BaseModel):
    """Description of the page."""

    # The description of the currect state of the world.
    page: str

    # The description of the consequences of the action
    action: str

    # A visual description of the current state of the world.
    image: str


class KarmaPoints(pydantic.BaseModel):
    """Points of story karma. The values are between -1 and 1."""

    # The point in the dimension of technology. Higher is more advanced.
    # Lower is no technology.
    technology: float
    # The point in the dimension of happiness. Higher is humans are happier.
    # Lower is humans are unhappier.
    happiness: float
    # The point in the dimension of safety. Higher is humans are safer.
    # Lower is humans doesn't exist.
    safety: float
    # The point in the dimension of control. Higher is humans have more
    # control. Lower is AGI has more control.
    control: float

    @classmethod
    def cap(cls, value: float) -> float:
        return max(-1.0, min(1.0, value))

    def __init__(self, **data):
        super().__init__(**data)
        self.technology = self.cap(self.technology)
        self.happiness = self.cap(self.happiness)
        self.safety = self.cap(self.safety)
        self.control = self.cap(self.control)

    def __add__(self, other: KarmaPoints) -> KarmaPoints:
        return KarmaPoints(
            technology=self.cap(self.technology + other.technology),
            happiness=self.cap(self.happiness + other.happiness),
            safety=self.cap(self.safety + other.safety),
            control=self.cap(self.control + other.control),
        )

    def __sub__(self, other: KarmaPoints) -> KarmaPoints:
        return KarmaPoints(
            technology=self.cap(self.technology - other.technology),
            happiness=self.cap(self.happiness - other.happiness),
            safety=self.cap(self.safety - other.safety),
            control=self.cap(self.control - other.control),
        )


class PageType(StrEnum):
    """The type of the page."""

    # The page is the start of the story.
    START = "start"
    # The page is the end of the story.
    END = "end"
    # The page is a normal page.
    NORMAL = "normal"


class Page(pydantic.BaseModel):
    """A page in the story."""
    uuid: str = pydantic.Field(default_factory=lambda: uuid.uuid4().hex)
    page_type: PageType = pydantic.Field(default=PageType.NORMAL)
    action: str = pydantic.Field(min_length=1, max_length=100)
    karma: KarmaPoints
    description: Optional[Description] = pydantic.Field(default=None)
    image: Optional[Image] = pydantic.Field(default=None)
