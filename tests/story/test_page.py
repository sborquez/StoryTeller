from story_teller.story.page import (
    Page, Description, KarmaPoints, Image, PageType
)


def test_new_karma_points():
    karma = KarmaPoints(technology=0.0, happiness=0.0, safety=0.0, control=0.0)

    assert karma.technology == 0.0
    assert karma.happiness == 0.0
    assert karma.safety == 0.0
    assert karma.control == 0.0


def test_add_karma_points():
    karma = KarmaPoints(technology=0.0, happiness=0.0, safety=0.0, control=0.0)
    karma += KarmaPoints(technology=0.5, happiness=0.5, safety=0.5, control=0.5)

    assert karma.technology == 0.5
    assert karma.happiness == 0.5
    assert karma.safety == 0.5
    assert karma.control == 0.5

    karma += KarmaPoints(technology=1.0, happiness=1.0, safety=1.0, control=1.0)
    assert karma.technology == 1.0
    assert karma.happiness == 1.0
    assert karma.safety == 1.0
    assert karma.control == 1.0

    karma += KarmaPoints(technology=-1.0, happiness=-1.0, safety=-1.0, control=-1.0)
    karma += KarmaPoints(technology=-1.0, happiness=-1.0, safety=-1.0, control=-1.0)
    assert karma.technology == -1.0
    assert karma.happiness == -1.0
    assert karma.safety == -1.0
    assert karma.control == -1.0


def test_sub_karma_points():
    karma = KarmaPoints(technology=0.0, happiness=0.0, safety=0.0, control=0.0)
    karma -= KarmaPoints(technology=0.5, happiness=0.5, safety=0.5, control=0.5)

    assert karma.technology == -0.5
    assert karma.happiness == -0.5
    assert karma.safety == -0.5
    assert karma.control == -0.5

    karma -= KarmaPoints(technology=1.0, happiness=1.0, safety=1.0, control=1.0)
    assert karma.technology == -1.0
    assert karma.happiness == -1.0
    assert karma.safety == -1.0
    assert karma.control == -1.0

    karma -= KarmaPoints(technology=-1.0, happiness=-1.0, safety=-1.0, control=-1.0)
    karma -= KarmaPoints(technology=-1.0, happiness=-1.0, safety=-1.0, control=-1.0)
    assert karma.technology == 1.0
    assert karma.happiness == 1.0
    assert karma.safety == 1.0
    assert karma.control == 1.0


def test_new_page():
    page = Page(
        action="Test",
        page_type=PageType.NORMAL,
        karma=KarmaPoints(technology=0.0, happiness=0.0, safety=0.0, control=0.0),
    )

    assert page.action == "Test"
    assert page.page_type == PageType.NORMAL
    assert page.karma == KarmaPoints(technology=0.0, happiness=0.0, safety=0.0, control=0.0)
    assert page.description is None
    assert page.image is None


def test_new_page_with_description():
    page = Page(
        action="Test",
        page_type=PageType.NORMAL,
        karma=KarmaPoints(technology=0.0, happiness=0.0, safety=0.0, control=0.0),
        description=Description(page="Test description", action="Test action", image="Test image"),
    )

    assert page.action == "Test"
    assert page.page_type == PageType.NORMAL
    assert page.karma == KarmaPoints(technology=0.0, happiness=0.0, safety=0.0, control=0.0)
    assert page.image is None
    assert page.description.page == "Test description"
    assert page.description.action == "Test action"
    assert page.description.image == "Test image"


def test_new_page_with_image():
    page = Page(
        action="Test",
        page_type=PageType.NORMAL,
        karma=KarmaPoints(technology=0.0, happiness=0.0, safety=0.0, control=0.0),
        image=Image(path="Test image", url="Test url", description="Test description"),
    )

    assert page.action == "Test"
    assert page.page_type == PageType.NORMAL
    assert page.karma == KarmaPoints(technology=0.0, happiness=0.0, safety=0.0, control=0.0)
    assert page.description is None
    assert page.image.path == "Test image"
    assert page.image.url == "Test url"
    assert page.image.description == "Test description"
