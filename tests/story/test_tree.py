from typing import Any, Dict

from story_teller.story.tree import TreeNode


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
