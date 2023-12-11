from __future__ import annotations
import json
from typing import Any, Dict, List, Optional

from story_teller.story.page import Page, PageRepository


class TreeNode:
    """A node in the story tree."""

    def __init__(self,
                 page_uuid: str, parent: Optional[TreeNode] = None) -> None:
        self.page_uuid = page_uuid
        self.parent = parent
        self.children: List[TreeNode] = []

    @classmethod
    def from_dict(cls,
                  node_data: Dict[str, Any], parent: Optional[TreeNode] = None
                  ) -> TreeNode:
        """Create a tree node from a dictionary."""
        node = cls(page_uuid=node_data["page_uuid"], parent=parent)
        for child in node_data["children"]:
            node.add_node(cls.from_dict(child, parent=node))
        return node

    @classmethod
    def to_dict(cls, node: TreeNode) -> Dict[str, Any]:
        """Create a dictionary from a tree node."""
        return {
            "page_uuid": node.page_uuid,
            "children": [cls.to_dict(child) for child in node.children]
        }

    def add_node(self, child: TreeNode) -> None:
        """Add a child to the node."""
        child.parent = self
        self.children.append(child)

    def _cascade_remove(self, node: TreeNode) -> List[str]:
        """Remove a node and all its children. Return the moved uuids."""
        removed_uuids = []
        for child in node.children:
            removed_uuids += self._cascade_remove(child)
            del child
        node.parent = None
        removed_uuids.append(node.page_uuid)
        return removed_uuids

    def remove_node(self, child_uuid: str) -> List[str]:
        """Remove a child from the node."""
        removed_child = None
        new_children = []
        for child in self.children:
            if child.page_uuid == child_uuid:
                removed_child = child
            else:
                new_children.append(child)
        self.children = new_children

        if removed_child is not None:
            removed_uuids = self._cascade_remove(removed_child)
            del removed_child
        else:
            removed_uuids = []
        return removed_uuids

    def __repr__(self) -> str:
        if len(self.children) == 0:
            return f"TreeNode(page={self.page_uuid})"
        return f"TreeNode(page={self.page_uuid}, children={self.children})"

    def __str__(self):
        return self.__repr__()


class StoryTree:
    """A tree of pages. This is the interface for the handle the story data."""

    def __init__(self,
                 pages_repository: PageRepository,
                 root: Optional[TreeNode] = None,
                 tree_source: Optional[str] = None) -> None:
        self.tree_source = tree_source
        self.root = root
        self.pages = pages_repository

    def add_page(self,
                 page: Page, parent_node: Optional[TreeNode] = None
                 ) -> None:
        self.pages.add_page(page)
        new_node = TreeNode(page.uuid, parent=parent_node)
        if parent_node is None:
            self.root = new_node
        else:
            parent_node.add_node(new_node)

    def get_root(self) -> Optional[TreeNode]:
        return self.root

    def get_page(self, uuid: str) -> Optional[Page]:
        return self.pages.get_page(uuid)

    def search_page_node(self,
                         uuid: str, node: Optional[TreeNode] = None
                         ) -> Optional[TreeNode]:
        """Get the node of a page."""
        node = node or self.root
        if node is None:
            return None
        elif node.page_uuid == uuid:
            return node
        else:
            for child in node.children:
                result = self.search_page_node(uuid, node=child)
                if result is not None:
                    return result
            return None

    def remove_page(self, uuid: str, node: Optional[TreeNode] = None) -> None:
        """Remove a page from the tree."""
        node = node or self.search_page_node(uuid)
        if node is None:
            raise ValueError(f"Page with uuid {uuid} does not exist.")
        # Remove the node from the tree nodes
        if node.parent is None:
            self.root = None
        else:
            # Remove the node from the parent recursively
            removed_uuids = node.parent.remove_node(uuid)
        # Remove the page and its children from the repository
        for removed_uuid in removed_uuids:
            self.pages.remove_page(removed_uuid)


class StoryTreeFactory:
    """A factory for creating story trees."""

    @classmethod
    def from_json(cls, json_file: str) -> StoryTree:
        """Create a tree from a JSON file."""
        with open(json_file, "r") as f:
            tree_data = json.load(f)
        tree_source = json_file
        root = TreeNode.from_dict(tree_data["root"])
        pages = PageRepository.from_dict(tree_data["pages"])
        tree = StoryTree(
            root=root, pages_repository=pages, tree_source=tree_source
        )
        return tree


class StoryTreeWriter:
    """Save a tree to persistent storage."""

    @classmethod
    def to_json(cls, tree: StoryTree, json_file: str) -> None:
        """Write a tree to a JSON file."""
        tree_data = {
            "root": TreeNode.to_dict(tree.root),
            "pages": PageRepository.to_dict(tree.pages)
        }
        with open(json_file, "w") as f:
            json.dump(tree_data, f, indent=4)
