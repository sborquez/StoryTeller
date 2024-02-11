from __future__ import annotations
from configparser import ConfigParser
import random
from typing import Any

from story_teller.teller.chains import ChainBuilder, RunnableSequence
from story_teller.story.path import Path
from story_teller.story.page import Page, PageType, Image, Description, KarmaPoints
from story_teller.story.tree import StoryTree, TreeNode


class Teller:
    """Entry point for the story teller."""

    def __init__(self, chain: RunnableSequence, learner: Any,
                 max_tries: int = 3,
                 new_start_probability: float = 0.5,
                 new_page_probability: float = 0.5,
                 ) -> None:
        """Initialize the story teller.

        Args:
            chain (RunnableSequence): A Chain for writing pages, audio and images
                with a generative model.
            learner (Any): Best story path generator, learns from user
                feedback how to generate the best story.
            max_tries (int): The maximum tries for generating a new page.
        """
        self._chain = chain
        self._learner = learner
        # Start new page probability
        self._new_start_probability = new_start_probability
        # Generate new page probability
        self._new_page_probability = new_page_probability
        # Max tries for generating a new page
        self._max_tries = max_tries

    def _invoke_chain(self, context: str, page_number: int, pages: list[dict[str, Any]], karma_points: list[float], action: str) -> None:
        """Invoke the chain to generate a new page.

        Args:
            context (str): The context of the story.
            page_number (int): The page number.
            pages (list[dict[str, Any]]): The pages of the story.
            karma_points (list[float]): The karma points of the story.
            action (str): The action of the page.
        """
        self._chain.invoke({
            "context": context,
            "page_number": page_number,
            "pages": pages,
            "karma_points": karma_points,
            "action": action,
        })

    def _generate_starting_page(self, story_tree: StoryTree) -> Page:
        """Generate a new starting page.

        Args:
            story_tree (StoryTree): The story tree instance.

        Returns:
            str: The uuid of the new starting page.
        """
        context_page = story_tree.get_context_page()
        context = context_page.description.page
        karma = context_page.karma.to_list()
        for _ in range(self._max_tries):
            try:
                response = self._chain.invoke({
                    "context": context,
                    "page_number": 1,
                    "pages": [],
                    "karma_points": karma,
                    "action": "start",
                })
            except Exception as e:
                print(f"Error generating starting page: {e}")
                continue
            else:
                break
        page_type = PageType.START
        # Extract the generated image
        image_content = response["image"]
        if image_content is not None:
            image = Image(url=image_content["url"])
            image_description = image_content["description"]
        else:
            image = Image()
            image_description = None
        # TODO: Add support for the audio
        # # Extract the generated audio
        # audio_content = response["audio"]
        # if audio_content is not None:
        #     pass
        # else:
        #     pass
        page_content = response["page"]
        description = Description(
            page=page_content["description"],
            image=image_description,
        )
        karma = KarmaPoints(
            technology=page_content["karma_points"][0],
            happiness=page_content["karma_points"][1],
            safety=page_content["karma_points"][2],
            control=page_content["karma_points"][3],
        )
        new_start_page = Page(
            page_type=page_type,
            action="start",
            karma=karma,
            description=description,
            # TODO: Move the image to a MediaRepository and use the uuid to reference the page
            image=image,
        )

        children = []
        for action in page_content["next_actions"]:
            child_page = Page(
                page_type=PageType.ACTION,
                action=action,
            )
            children.append(child_page)
        # TODO: Handle media storage with a MediaRepository class
        return new_start_page, children

    def starting_page(self, path: Path, story_tree: StoryTree) -> tuple[Page, list[Page]]:
        """Get the starting page of the story.

        Returns:
            tuple[Page, list[Page]]: The starting page and its children.
        """
        # Select one starting page
        actions = list(path.view_action_options().keys())
        # Add the probability of select a previously action or a new one
        if len(actions) > 0:
            weights = [(1.0 - self._new_start_probability) / len(actions)] * len(actions)
            weights.append(self._new_start_probability)
        else:
            weights = [1.0]
        # Add a "generate new start" option
        actions.append("Generate new start")
        # Select an start action
        selected = random.choices(actions, weights)[0]
        if selected == "Generate new start":
            # Generate a new Page, and add it to the story tree
            starting_page, children = self._generate_starting_page(story_tree)
            starting_page_node = story_tree.add_page(starting_page, parent_node=path.root_page_node)
            for child in children:
                story_tree.add_page(child, parent_node=starting_page_node)
            # Then return the new action
            selected = "Start " + starting_page.uuid
        # Take the action
        path.take_action(selected)
        return path

    def select_next_action_options(self, path: Path, story_tree: StoryTree) -> dict[str, TreeNode]:
        """Select the next actions for the story.

        Args:
            path (Path): The current path of the story.
            story_tree (StoryTree): The story tree instance.

        Returns:
            Any: The next actions for the story.
        """
        current_page = path.get_current_page()
        if current_page.page_type == PageType.END:
            return {}
        options = path.view_action_options()
        empty_pages = []
        written_pages = []
        for action, node in options.items():
            page = story_tree.get_page(node.page_uuid)
            if page.description is None:
                empty_pages.append(action)
            else:
                written_pages.append(action)
        random.shuffle(empty_pages)
        random.shuffle(written_pages)
        new_options = empty_pages + written_pages
        # Sample two actions
        if len(written_pages) == 0:
            first, second = empty_pages[:2]
        else:
            first = new_options[0] if random.random() < self._new_page_probability else new_options[-1]
            second = new_options[1] if random.random() < self._new_page_probability else new_options[-2]
        return {
            first: options[first],
            second: options[second],
        }

    def generate_current_page(self, current_page: Page, path: Path, story_tree: StoryTree) -> tuple[Page, list[Page]]:
        """Generate a new action page.

        Args:
            path (Path): The current path of the story.

        Returns:
            tuple[Page, list[Page]]: The new action page and its children.
        """
        context_page = story_tree.get_context_page()
        context = context_page.description.page
        karma = path.compute_karma().to_list()
        action = current_page.action
        pages = [
            f"{p.action}: {p.description.page}"
            for p in path if p.page_type != PageType.CONTEXT and p is not current_page
        ]
        for _ in range(self._max_tries):
            try:
                response = self._chain.invoke({
                    "context": context,
                    "page_number": len(path) + 1,
                    "pages": pages,
                    "karma_points": karma,
                    "action": action,
                })
            except Exception as e:
                print(f"Error generating action page: {e}")
                continue
            else:
                break
        # Extract the generated image
        image_content = response["image"]
        if image_content is not None:
            image = Image(url=image_content["url"])
            image_description = image_content["description"]
        else:
            image = Image()
            image_description = None
        page_content = response["page"]
        description = Description(
            page=page_content["description"],
            image=image_description,
        )
        karma = KarmaPoints(
            technology=page_content["karma_points"][0],
            happiness=page_content["karma_points"][1],
            safety=page_content["karma_points"][2],
            control=page_content["karma_points"][3],
        )
        current_page.karma = karma
        current_page.description = description
        current_page.image = image
        children = []
        if "END" in list(map(str.upper, page_content["next_actions"])):
            page_type = PageType.END
            current_page.page_type = page_type
        else:
            for action in page_content["next_actions"]:
                page_type = PageType.ACTION
                child_page = Page(
                    page_type=PageType.ACTION,
                    action=action,
                )
                children.append(child_page)
        # TODO: Handle media storage with a MediaRepository class
        return current_page, children

    @classmethod
    def from_config(cls, config: ConfigParser) -> Teller:
        """Create a new teller.

        Args:
            config (ConfigParser): The configuration parser instance.

        Returns:
            Teller: A new teller instance.
        """

        return Teller(
            chain=ChainBuilder.from_config(config),
            learner=None,
            # media=None,
            max_tries=config.getint("teller", "max_tries", fallback=3),
            new_start_probability=config.getfloat("teller", "new_start_probability", fallback=0.5),
            new_page_probability=config.getfloat("teller", "new_page_probability", fallback=0.5),
        )
