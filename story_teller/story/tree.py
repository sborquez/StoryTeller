from __future__ import annotations
import json
from typing import Any, Dict, List, Optional

from story_teller.story.page import PageRepository


class TreeNode:
    """A node in the story tree."""

    def __init__(self,
                 page_uuid: str, parent: Optional[TreeNode] = None) -> None:
        self.page_uuid = page_uuid
        self.parent = parent
        self.children: List[TreeNode] = []

    @classmethod
    def from_dict(cls, node_data: Dict[str, Any], parent: Optional[TreeNode] = None) -> TreeNode:
        """Create a tree node from a dictionary."""
        node = cls(page_uuid=node_data["page_uuid"], parent=parent)
        for child in node_data["children"]:
            node.add_child(cls.from_dict(child, parent=node))
        return node

    @classmethod
    def to_dict(cls, node: TreeNode) -> Dict[str, Any]:
        """Create a dictionary from a tree node."""
        return {
            "page_uuid": node.page_uuid,
            "children": [cls.to_dict(child) for child in node.children]
        }

    def add_child(self, child: TreeNode) -> None:
        """Add a child to the node."""
        self.children.append(child)

    def remove_child(self, child_uuid: str) -> None:
        """Remove a child from the node."""
        self.children = [
            child for child in self.children if child.page_uuid != child_uuid
        ]

    def __repr__(self) -> str:
        return f"TreeNode(page={self.page_uuid}, children={self.children})"

    def __str__(self):
        return self.__repr__()


class Tree:
    """A tree of pages."""

    def __init__(self,
                 root: Optional[TreeNode] = None,
                 pages_repository: Optional[PageRepository] = None,
                 tree_source: Optional[str] = None) -> None:
        self.tree_source = tree_source
        self.root = root
        self.pages = pages_repository

    @classmethod
    def from_json(cls, tree_source: str) -> Tree:
        """Create a tree from a JSON string."""
        tree_data = json.loads(tree_source)
        root = tree_data["root"]
        pages = PageRepository.from_dict(tree_data["pages"])
        tree = cls(root=root, pages=pages, tree_source=tree_source)
        return tree

    def __repr__(self) -> str:
        return f"Tree(root={self.root}, pages={self.pages})"

    def __str__(self):
        return self.__repr__()

    def add_page():
        pass

    def get_page():
        pass

    def remove_page():
        pass
