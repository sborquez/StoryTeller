from typing import Dict, List

from story_teller.story.page import KarmaPoints, Page, PageType
from story_teller.story.tree import StoryTree, TreeNode


class Path:
    """A path is a dinamically generated list of pages.

    Contains the starting page and the list of pages that are selected
    by the user actions.

    It works like a StoryTree view, it won't modify the tree.
    """

    def __init__(self, story_tree: StoryTree) -> None:
        if story_tree.get_root() is None:
            raise ValueError("The story tree has no root.")
        self.starting_page_node = story_tree.get_root()
        self._current_page_node = self.starting_page_node
        self._story_tree = story_tree
        self._is_finished = False

        self._pages_uuid = [
            self.starting_page_node.page_uuid
        ]
        self._actions_taken = [
            self._story_tree.get_page(self.starting_page_node.page_uuid).action
        ]

    def is_finished(self) -> bool:
        """Return True if the path is finished."""
        return self._is_finished

    def get_current_page(self) -> Page:
        """Return the current page."""
        return self._story_tree.get_page(self._current_page_node.page_uuid)

    def view_action_options(self) -> Dict[str, TreeNode]:
        """Return the possible actions for the current page."""
        actions = {}
        for child in self._current_page_node.children:
            child_page = self._story_tree.get_page(child.page_uuid)
            if child_page.page_type == PageType.START:
                child_action = f"Start {child_page.uuid}"
            else:
                child_action = child_page.action
            actions[child_action] = child
        return actions

    def take_action(self, action: str) -> bool:
        """Move to the next page."""
        actions = self.view_action_options()
        if action not in actions:
            raise ValueError(f"Action {action} not available.")
        next_page_node = actions[action]
        self._current_page_node = next_page_node
        self._pages_uuid.append(next_page_node.page_uuid)
        self._actions_taken.append(action)
        next_page = self._story_tree.get_page(next_page_node.page_uuid)
        if next_page.page_type == PageType.END:
            self._is_finished = True
        return self._is_finished

    def go_back(self) -> None:
        """Go back to the previous page."""
        if len(self._pages_uuid) == 2:
            raise ValueError("Cannot go back from the starting page.")
        self._pages_uuid.pop()
        self._actions_taken.pop()
        self._current_page_node = self._current_page_node.parent
        self._is_finished = False

    def compute_karma(self) -> KarmaPoints:
        """Compute the karma of the path."""
        karma_points = KarmaPoints()
        for page_uuid in self._pages_uuid:
            page = self._story_tree.get_page(page_uuid)
            if page is None:
                raise ValueError(f"Page {page_uuid} not found.")
            karma_points += page.karma
        return karma_points

    def get_pages(self) -> List[Page]:
        """Return the list of pages in the path."""
        return [self._story_tree.get_page(uuid) for uuid in self._pages_uuid]

    def get_actions_taken(self) -> List[str]:
        """Return the list of actions in the path."""
        return list(self._actions_taken)
