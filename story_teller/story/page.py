from __future__ import annotations
from enum import StrEnum
from typing import Dict, Optional
import uuid

import pydantic


class Image(pydantic.BaseModel):
    """Image for the page."""

    # Local path to the image.
    path: Optional[str] = pydantic.Field(
        default=None,
        description="Local path to the image. If the image is not local, use the url field instead.",
    )
    # Remote url to the image.
    url: Optional[str] = pydantic.Field(
        default=None,
        description="Remote url to the image. If the image is local, use the path field instead.",
    )


class Description(pydantic.BaseModel):
    """Description of the page in the story."""

    page: str = pydantic.Field(
        description="The description of the page from the story."
    )

    image: Optional[str] = pydantic.Field(
        default=None,
        description="A visual description of the current page of the story."
    )


class KarmaPoints(pydantic.BaseModel):
    """Points of change of karma for a page story. The values are between -1 and 1. The sum of all karma points is the total karma points of the story."""

    technology: float = pydantic.Field(
        default=0.0,
        description="The dimension of technology. Higher is more advanced. Lower is no technology.",
    )
    happiness: float = pydantic.Field(
        default=0.0,
        description="The dimension of happiness. Higher is humans are happier. Lower is humans are unhappier.",
    )
    safety: float = pydantic.Field(
        default=0.0,
        description="The dimension of safety. Higher is humans are safer. Lower is humans doesn't exist.",
    )
    control: float = pydantic.Field(
        default=0.0,
        description="The dimension of control. Higher is humans have more control. Lower is AGI has more control.",
    )

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

    # This page is the context, previous to select actions
    CONTEXT = "context"
    # The page is the start of the story, its action is the start of the story.
    START = "start"
    # The page is a normal page.
    ACTION = "action"
    # The page is the end of the story.
    END = "end"


class Page(pydantic.BaseModel):
    """A page in the story."""
    uuid: str = pydantic.Field(default_factory=lambda: uuid.uuid4().hex)
    page_type: PageType = pydantic.Field(default=PageType.ACTION)
    action: Optional[str] = pydantic.Field(default=None)
    karma: KarmaPoints = pydantic.Field(default=KarmaPoints())
    description: Optional[Description] = pydantic.Field(default=None)
    image: Optional[Image] = pydantic.Field(default=None)


class PageRepository:
    """A repository of pages."""

    def __init__(self, pages: Dict[str, Page]) -> None:
        self.pages = pages

    @classmethod
    def from_dict(cls, pages_data: Dict[str, Page]) -> PageRepository:
        """Create a page repository from a dictionary."""
        pages = {}
        for page_uuid, page_data in pages_data.items():
            page_type = PageType(page_data["page_type"])
            karma = KarmaPoints(**page_data["karma"])
            description = Description(**page_data["description"])
            image = Image(**page_data["image"]) if page_data["image"] else None
            page = Page(
                uuid=page_uuid,
                page_type=page_type,
                action=page_data["action"],
                karma=karma,
                description=description,
                image=image,
            )
            pages[page_uuid] = page
        return cls(pages=pages)

    @classmethod
    def to_dict(cls, repository: PageRepository) -> Dict[str, Page]:
        """Create a dictionary from a page repository."""
        pages = {}
        for page_uuid, page in repository.pages.items():
            pages[page_uuid] = {
                "uuid": page.uuid,
                "page_type": page.page_type.value,
                "action": page.action,
                "karma": page.karma.model_dump(),
                "description": page.description.model_dump(),
                "image": page.image.model_dump() if page.image else None,
            }
        return pages

    def add_page(self, page: Page, safe: bool = True) -> None:
        """Add a page to the repository."""
        if safe and page.uuid in self.pages:
            raise ValueError(f"Page with uuid {page.uuid} already exists.")
        self.pages[page.uuid] = page

    def get_page(self, uuid: str) -> Optional[Page]:
        """Get a page from the repository."""
        return self.pages.get(uuid, None)

    def remove_page(self, uuid: str) -> None:
        """Remove a page from the repository."""
        if uuid not in self.pages:
            raise ValueError(f"Page with uuid {uuid} does not exist.")
        del self.pages[uuid]

    def __repr__(self) -> str:
        pages_uuids = [page_uuid for page_uuid in self.pages.keys()]
        return f"PageRepository(pages={pages_uuids})"

    def __getitem__(self, uuid: str) -> Optional[Page]:
        """Get a page from the repository."""
        return self.get_page(uuid)

    def __contains__(self, uuid: str) -> bool:
        """Check if a page is in the repository."""
        return uuid in self.pages

    def __len__(self) -> int:
        """Get the number of pages in the repository."""
        return len(self.pages)
