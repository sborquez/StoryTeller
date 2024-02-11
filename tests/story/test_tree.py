import os
from typing import Any, Dict

from story_teller.story.page import Page, PageType, KarmaPoints
from story_teller.story.tree import (
    TreeNode, StoryTree
)


def test_TreeNode_init() -> None:
    node = TreeNode(page_uuid="page_uuid")
    assert node.page_uuid == "page_uuid"
    assert node.parent is None
    assert len(node.children) == 0


def test_TreeNode_from_dict() -> None:
    """Test that a tree node can be created from a dictionary."""
    node_data = {
        "page_uuid": "page_uuid",
        "children": [
            {
                "page_uuid": "child_uuid",
                "children": []
            }
        ]
    }
    node = TreeNode.from_dict(node_data)
    assert node.page_uuid == "page_uuid"
    assert node.parent is None
    assert len(node.children) == 1
    assert node.children[0].page_uuid == "child_uuid"
    assert len(node.children[0].children) == 0
    assert node.children[0].parent is node


def test_TreeNode_to_dict() -> None:
    node_data = {
        "page_uuid": "page_uuid",
        "children": [
            {
                "page_uuid": "child_uuid",
                "children": [
                    {
                        "page_uuid": "grandchild_uuid",
                        "children": []
                    }
                ]
            }
        ]
    }
    node = TreeNode.from_dict(node_data)
    assert TreeNode.to_dict(node) == node_data


def test_TreeNode_from_json(node_data: Dict[str, Any]) -> None:
    """Test that a tree node can be created from a JSON string."""
    node = TreeNode.from_dict(node_data)
    assert node.page_uuid == "0"
    assert node.parent is None
    assert len(node.children) == 2
    assert node.children[0].page_uuid == "1"
    assert len(node.children[0].children) == 2
    assert node.children[0].parent is node
    assert node.children[1].page_uuid == "4"
    assert len(node.children[1].children) == 0
    assert node.children[1].parent is node


def test_TreeNode_add_node() -> None:
    """Test that a page can be added to a tree node."""
    node = TreeNode(page_uuid="page_uuid")
    assert len(node.children) == 0
    node.add_node(TreeNode(page_uuid="child_uuid"))
    assert len(node.children) == 1
    assert node.children[0].parent is node


def test_TreeNode_remove_node() -> None:
    """Test that a page can be removed from a tree node."""
    node_data = {
        "page_uuid": "page_uuid",
        "children": [
            {
                "page_uuid": "child_uuid",
                "children": [
                    {
                        "page_uuid": "grandchild_uuid",
                        "children": []
                    }
                ]
            }
        ]
    }
    node = TreeNode.from_dict(node_data)
    removed_uuids = node.remove_node("child_uuid")
    assert len(node.children) == 0
    assert set(removed_uuids) == set(["child_uuid", "grandchild_uuid"])


def test_StoryTree_add_page(sample_data_file: str) -> None:
    """Test that a page can be added to a tree."""
    tree = StoryTree.from_json(sample_data_file)
    assert len(tree.root.children) == 2
    assert len(tree.root.children[1].children) == 0
    assert len(tree.pages) == 5
    new_page = Page(
        action="test",
        page_type=PageType.ACTION,
        karma=KarmaPoints(
            technology=0.0, happiness=0.0, safety=0.0, control=0.0
        )
    )
    tree.add_page(new_page, parent_node=tree.root.children[1])
    assert len(tree.root.children) == 2
    assert len(tree.root.children[1].children) == 1
    assert tree.root.children[1].children[0].page_uuid == new_page.uuid
    assert len(tree.pages) == 6
    assert new_page.uuid in tree.pages


def test_StoryTree_get_root(sample_data_file: str) -> None:
    """Test that the root of a tree can be retrieved."""
    tree = StoryTree.from_json(sample_data_file)
    assert tree.get_root() is tree.root


def test_StoryTree_get_page(sample_data_file: str) -> None:
    """Test that a page can be retrieved from a tree."""
    tree = StoryTree.from_json(sample_data_file)
    assert tree.get_page("0") is tree.pages["0"]
    assert tree.get_page("1") is tree.pages["1"]
    assert tree.get_page("2") is tree.pages["2"]
    assert tree.get_page("3") is tree.pages["3"]
    assert tree.get_page("4") is tree.pages["4"]


def test_StoryTree_search_page_node(sample_data_file: str) -> None:
    """Test that a page node can be retrieved from a tree."""
    tree = StoryTree.from_json(sample_data_file)
    assert tree.search_page_node("0") is tree.root
    assert tree.search_page_node("1") is tree.root.children[0]
    assert tree.search_page_node("2") is tree.root.children[0].children[0]
    assert tree.search_page_node("3") is tree.root.children[0].children[1]
    assert tree.search_page_node("4") is tree.root.children[1]
    assert tree.search_page_node("5") is None


def test_StoryTree_remove_page(sample_data_file: str) -> None:
    """Test that a page can be removed from a tree."""
    tree = StoryTree.from_json(sample_data_file)
    assert len(tree.root.children) == 2
    assert len(tree.root.children[0].children) == 2
    assert len(tree.pages) == 5
    tree.remove_page("1")
    assert tree.search_page_node("1") is None
    assert len(tree.root.children) == 1
    assert "1" not in tree.pages
    assert "2" not in tree.pages
    assert "3" not in tree.pages
    assert len(tree.pages) == 2


def test_StoryTree_from_scratch() -> None:
    """Test that an empty tree can be created."""
    tree = StoryTree.from_scratch()
    assert tree.root is None
    print(tree.pages)
    assert len(tree.pages) == 0


def test_StoryTree_from_json(sample_data_file: str) -> None:
    """Test that a tree can be created from a JSON string."""
    tree = StoryTree.from_json(sample_data_file)
    assert isinstance(tree, StoryTree)
    assert tree.root.page_uuid == "0"
    assert len(tree.root.children) == 2
    assert tree.pages["0"].page_type == PageType.START
    assert tree.pages["1"].page_type == PageType.ACTION
    assert tree.pages["2"].page_type == PageType.END


def test_StoryTree_to_json(sample_data_file: str) -> None:
    """Test that a tree can be written to a JSON string."""
    tree = StoryTree.from_json(sample_data_file)
    StoryTree.to_json(tree, 'test.json')
    tree_2 = StoryTree.from_json('test.json')
    assert isinstance(tree_2, StoryTree)
    assert tree_2.root.page_uuid == "0"
    assert len(tree_2.root.children) == 2
    assert tree_2.pages["0"].page_type == PageType.START
    assert tree_2.pages["1"].page_type == PageType.ACTION
    assert tree_2.pages["2"].page_type == PageType.END
    os.remove('test.json')
