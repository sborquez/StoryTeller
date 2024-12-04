from pytest import raises


from story_teller.story.path import Path
from story_teller.story.page import KarmaPoints, Page
from story_teller.story.tree import TreeNode, StoryTreeFactory


def test_create_path_from_empty_StoryTree() -> None:
    """Test the creation of an empty story tree. Should fail."""
    story_tree = StoryTreeFactory.create_empty()
    with raises(ValueError):
        Path(story_tree)


def test_create_Path_from_StoryTree(sample_data_file: str) -> None:
    """Test the creation of a path from a story tree."""
    story_tree = StoryTreeFactory.from_json(sample_data_file)
    path = Path(story_tree)
    assert path.starting_page_node.page_uuid == "0"
    assert path._current_page_node.page_uuid == "0"
    assert path._story_tree == story_tree
    assert path._is_finished is False
    assert path._pages_uuid == ["0"]
    assert path._actions_taken == ["start"]


def test_Path_view_action_options(sample_data_file: str) -> None:
    """Test that actions can be viewed in a path."""
    story_tree = StoryTreeFactory.from_json(sample_data_file)
    path = Path(story_tree)
    actions = path.view_action_options()
    assert len(actions) == 2
    assert isinstance(actions, dict)
    assert all(isinstance(key, str) for key in actions.keys())
    assert all(isinstance(value, TreeNode) for value in actions.values())

    assert actions["action1"].page_uuid == "1"
    assert actions["action4"].page_uuid == "4"


def test_Path_take_actions(sample_data_file: str) -> None:
    """Test that actions can be taken in a path."""
    story_tree = StoryTreeFactory.from_json(sample_data_file)
    path = Path(story_tree)
    assert path._current_page_node.page_uuid == "0"
    assert path._pages_uuid == ["0"]
    assert path._actions_taken == ["start"]
    assert path._is_finished is False
    path.take_action("action1")
    assert path._current_page_node.page_uuid == "1"
    assert path._pages_uuid == ["0", "1"]
    assert path._actions_taken == ["start", "action1"]
    assert path._is_finished is False
    path.take_action("action2")
    assert path._current_page_node.page_uuid == "2"
    assert path._pages_uuid == ["0", "1", "2"]
    assert path._actions_taken == ["start", "action1", "action2"]
    assert path._is_finished is True


def test_Path_take_actions_with_go_back(sample_data_file: str) -> None:
    """Test that actions can be taken in a path."""
    story_tree = StoryTreeFactory.from_json(sample_data_file)
    path = Path(story_tree)
    assert path._current_page_node.page_uuid == "0"
    assert path._pages_uuid == ["0"]
    assert path._actions_taken == ["start"]
    assert path._is_finished is False
    path.take_action("action1")
    assert path._current_page_node.page_uuid == "1"
    assert path._pages_uuid == ["0", "1"]
    assert path._actions_taken == ["start", "action1"]
    assert path._is_finished is False
    path.take_action("action2")
    assert path._current_page_node.page_uuid == "2"
    assert path._pages_uuid == ["0", "1", "2"]
    assert path._actions_taken == ["start", "action1", "action2"]
    assert path._is_finished is True
    path.go_back()
    assert path._current_page_node.page_uuid == "1"
    assert path._pages_uuid == ["0", "1"]
    assert path._actions_taken == ["start", "action1"]
    assert path._is_finished is False
    path.take_action("action3")
    assert path._current_page_node.page_uuid == "3"
    assert path._pages_uuid == ["0", "1", "3"]
    assert path._actions_taken == ["start", "action1", "action3"]
    assert path._is_finished is True
    path.go_back()
    assert path._current_page_node.page_uuid == "1"
    assert path._pages_uuid == ["0", "1"]
    assert path._actions_taken == ["start", "action1"]
    assert path._is_finished is False
    path.go_back()
    assert path._current_page_node.page_uuid == "0"
    assert path._pages_uuid == ["0"]
    assert path._actions_taken == ["start"]
    assert path._is_finished is False
    path.take_action("action4")
    assert path._current_page_node.page_uuid == "4"
    assert path._pages_uuid == ["0", "4"]
    assert path._actions_taken == ["start", "action4"]
    assert path._is_finished is False


def test_Path_fails_to_go_back() -> None:
    """Test that going back fails when it should."""
    story_tree = StoryTreeFactory.create_empty()
    story_tree.add_page(Page(action="start"))
    path = Path(story_tree)
    with raises(ValueError):
        path.go_back()


def test_Path_compute_karma(sample_data_file: str) -> None:
    """Test that the karma can be computed."""
    story_tree = StoryTreeFactory.from_json(sample_data_file)
    path = Path(story_tree)
    path.take_action("action1")
    path.take_action("action2")
    assert path.compute_karma() == KarmaPoints(
        technology=1.0, happiness=1.0, safety=0.0, control=0.0
    )


def test_Path_get_pages(sample_data_file: str) -> None:
    """Test that the pages can be retrieved."""
    story_tree = StoryTreeFactory.from_json(sample_data_file)
    path = Path(story_tree)
    path.take_action("action1")
    path.take_action("action2")
    pages = path.get_pages()
    assert len(pages) == 3
    assert isinstance(pages, list)
    assert all(isinstance(page, Page) for page in pages)
    assert pages[0].uuid == "0"
    assert pages[1].uuid == "1"
    assert pages[2].uuid == "2"


def test_Path_get_actions(sample_data_file: str) -> None:
    """Test that the pages can be retrieved."""
    story_tree = StoryTreeFactory.from_json(sample_data_file)
    path = Path(story_tree)
    path.take_action("action1")
    path.take_action("action2")
    actions = path.get_actions_taken()
    assert len(actions) == 3
    assert isinstance(actions, list)
    assert all(isinstance(action, str) for action in actions)
    assert actions[0] == "start"
    assert actions[1] == "action1"
    assert actions[2] == "action2"
