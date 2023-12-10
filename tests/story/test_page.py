from typing import Any, Dict

from story_teller.story.page import (
    Description, Image, KarmaPoints, Page, PageRepository, PageType
)


def test_new_karma_points() -> None:
    karma = KarmaPoints(technology=0.0, happiness=0.0, safety=0.0, control=0.0)

    assert karma.technology == 0.0
    assert karma.happiness == 0.0
    assert karma.safety == 0.0
    assert karma.control == 0.0


def test_add_karma_points() -> None:
    karma = KarmaPoints(
        technology=0.0, happiness=0.0, safety=0.0, control=0.0
    )
    karma += KarmaPoints(
        technology=0.5, happiness=0.5, safety=0.5, control=0.5
    )

    assert karma.technology == 0.5
    assert karma.happiness == 0.5
    assert karma.safety == 0.5
    assert karma.control == 0.5

    karma += KarmaPoints(
        technology=1.0, happiness=1.0, safety=1.0, control=1.0
    )
    assert karma.technology == 1.0
    assert karma.happiness == 1.0
    assert karma.safety == 1.0
    assert karma.control == 1.0

    karma += KarmaPoints(
        technology=-1.0, happiness=-1.0, safety=-1.0, control=-1.0
    )
    karma += KarmaPoints(
        technology=-1.0, happiness=-1.0, safety=-1.0, control=-1.0
    )
    assert karma.technology == -1.0
    assert karma.happiness == -1.0
    assert karma.safety == -1.0
    assert karma.control == -1.0


def test_sub_karma_points() -> None:
    karma = KarmaPoints(
        technology=0.0, happiness=0.0, safety=0.0, control=0.0
    )
    karma -= KarmaPoints(
        technology=0.5, happiness=0.5, safety=0.5, control=0.5
    )

    assert karma.technology == -0.5
    assert karma.happiness == -0.5
    assert karma.safety == -0.5
    assert karma.control == -0.5

    karma -= KarmaPoints(
        technology=1.0, happiness=1.0, safety=1.0, control=1.0
    )
    assert karma.technology == -1.0
    assert karma.happiness == -1.0
    assert karma.safety == -1.0
    assert karma.control == -1.0

    karma -= KarmaPoints(
        technology=-1.0, happiness=-1.0, safety=-1.0, control=-1.0
    )
    karma -= KarmaPoints(
        technology=-1.0, happiness=-1.0, safety=-1.0, control=-1.0
    )
    assert karma.technology == 1.0
    assert karma.happiness == 1.0
    assert karma.safety == 1.0
    assert karma.control == 1.0


def test_new_page() -> None:
    page = Page(
        action="Test",
        page_type=PageType.ACTION,
        karma=KarmaPoints(
            technology=0.0, happiness=0.0, safety=0.0, control=0.0
        ),
    )

    assert page.action == "Test"
    assert page.page_type == PageType.ACTION
    assert page.karma == KarmaPoints(
        technology=0.0, happiness=0.0, safety=0.0, control=0.0
    )
    assert page.description is None
    assert page.image is None


def test_new_page_with_description() -> None:
    page = Page(
        action="Test",
        page_type=PageType.ACTION,
        karma=KarmaPoints(
            technology=0.0, happiness=0.0, safety=0.0, control=0.0
        ),
        description=Description(
            page="Test description", action="Test action", image="Test image"
        ),
    )

    assert page.action == "Test"
    assert page.page_type == PageType.ACTION
    assert page.karma == KarmaPoints(
        technology=0.0, happiness=0.0, safety=0.0, control=0.0
    )
    assert page.image is None
    assert page.description.page == "Test description"
    assert page.description.action == "Test action"
    assert page.description.image == "Test image"


def test_new_page_with_image() -> None:
    page = Page(
        action="Test",
        page_type=PageType.ACTION,
        karma=KarmaPoints(
            technology=0.0, happiness=0.0, safety=0.0, control=0.0
        ),
        image=Image(
            path="Test image", url="Test url", description="Test description"
        ),
    )

    assert page.action == "Test"
    assert page.page_type == PageType.ACTION
    assert page.karma == KarmaPoints(
        technology=0.0, happiness=0.0, safety=0.0, control=0.0
    )
    assert page.description is None
    assert page.image.path == "Test image"
    assert page.image.url == "Test url"
    assert page.image.description == "Test description"


def test_PageRepository_init() -> None:
    repository = PageRepository()
    assert len(repository.pages) == 0


def test_PageRepository_from_dict(pages_data: Dict[str, Any]) -> None:
    repository = PageRepository.from_dict(pages_data)
    # Check the number of pages
    assert len(repository.pages) == 5
    assert all([
        isinstance(page, Page)
        for page in repository.pages.values()
    ])
    assert all([
        isinstance(page.karma, KarmaPoints)
        for page in repository.pages.values()
    ])
    assert all([
        isinstance(page.description, Description)
        for page in repository.pages.values()
    ])
    assert all([
        isinstance(page.image, Image) or page.image is None
        for page in repository.pages.values()
    ])
    assert all([
        page_uuid == page.uuid
        for page_uuid, page in repository.pages.items()
    ])

    # Check the first page
    assert repository.pages["0"].action == "start"
    assert repository.pages["0"].page_type == PageType.START
    assert repository.pages["0"].karma == KarmaPoints(
        technology=0.0, happiness=0.0, safety=0.0, control=0.0
    )
    assert isinstance(repository.pages["0"].description, Description)
    assert isinstance(repository.pages["0"].image, Image)

    # Check end page
    assert repository.pages["2"].action == "action2"
    assert repository.pages["2"].page_type == PageType.END
    assert repository.pages["2"].karma == KarmaPoints(
        technology=0.0, happiness=0.0, safety=0.0, control=0.0
    )
    assert isinstance(repository.pages["2"].description, Description)
    assert isinstance(repository.pages["2"].image, Image)

    # Check action page
    assert repository.pages["4"].action == "action4"
    assert repository.pages["4"].page_type == PageType.ACTION
    assert repository.pages["4"].karma == KarmaPoints(
        technology=0.0, happiness=0.0, safety=0.0, control=0.0
    )
    assert isinstance(repository.pages["4"].description, Description)
    assert repository.pages["4"].image is None


def test_PageRepository_to_dict(pages_data: Dict[str, Any]) -> None:
    repository = PageRepository.from_dict(pages_data)
    pages_data_from_repo = PageRepository.to_dict(repository)
    for page_uuid, page_data in pages_data_from_repo.items():
        print(page_data)
        assert page_uuid == page_data["uuid"]
        assert PageType(page_data["page_type"])
        assert isinstance(page_data["karma"], dict)
        assert isinstance(page_data["description"], dict)
        assert isinstance(page_data["image"], dict) \
            or page_data["image"] is None
        assert page_data == pages_data[page_uuid]
