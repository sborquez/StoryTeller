from __future__ import annotations
from configparser import ConfigParser
import time

import arcade

from story_teller.app.base import (
    App, AppFactory, Context,
    Event, AlertSystemEvent, ChoiceInputEvent, TextInputEvent, QuitEvent,
    RenderData, RenderControlsData, RenderSceneLayoutType,
)


class ArcadeApp(App):
    class MainView(arcade.View):
        """ Class that manages the 'main' view. """

        def __init__(self, context: Context, width: int = 800, height: int = 600) -> None:
            super().__init__()
            self.WIDTH = width
            self.HEIGHT = height
            self.context = context

        def on_show_view(self):
            """ Called when switching to this view"""
            arcade.set_background_color(arcade.color.WHITE)

        def on_draw(self):
            """ Draw the menu """
            self.clear()
            arcade.draw_text("Menu Screen - click to advance", self.WIDTH / 2, self.HEIGHT / 2,
                            arcade.color.BLACK, font_size=30, anchor_x="center")

        def on_mouse_press(self, _x, _y, _button, _modifiers):
            """ Use a mouse press to advance to the 'game' view. """
            game_view = ArcadeApp.InteractionView(self.context, self.WIDTH, self.HEIGHT)
            game_view.setup()
            self.window.show_view(game_view)

    class InteractionView(arcade.View):
        """ Manage the 'game' view for our program. """

        def __init__(self, context: Context, width: int = 800, height: int = 600) -> None:
            super().__init__()
            self.WIDTH = width
            self.HEIGHT = height
            self.context = context

        def setup(self):
            """ This should set up your game and get it ready to play """
            # Replace 'pass' with the code to set up your game
            pass

        def on_show_view(self):
            """ Called when switching to this view"""
            arcade.set_background_color(arcade.color.ORANGE_PEEL)

        def on_draw(self):
            """ Draw everything for the game. """
            self.clear()
            arcade.draw_text("Game - press SPACE to advance", self.WIDTH / 2, self.HEIGHT / 2,
                            arcade.color.BLACK, font_size=30, anchor_x="center")

        def on_key_press(self, key, _modifiers):
            """ Handle key presses. In this case, we'll just count a 'space' as
            game over and advance to the game over view. """
            if key == arcade.key.SPACE:
                game_over_view = ArcadeApp.MovieView(self.context, self.WIDTH, self.HEIGHT)
                self.window.show_view(game_over_view)

    class MovieView(arcade.View):
        """ Class to manage the movie view """

        def __init__(self, context: Context, width: int = 800, height: int = 600) -> None:
            super().__init__()
            self.WIDTH = width
            self.HEIGHT = height
            self.context = context

        def on_show_view(self):
            """ Called when switching to this view"""
            arcade.set_background_color(arcade.color.BLACK)

        def on_draw(self):
            """ Draw the game over view """
            self.clear()
            arcade.draw_text("Game Over - press ESCAPE to advance", self.WIDTH / 2, self.HEIGHT / 2,
                            arcade.color.WHITE, 30, anchor_x="center")

        def on_key_press(self, key, _modifiers):
            """ If user hits escape, go back to the main menu view """
            if key == arcade.key.SPACE:
                menu_view = ArcadeApp.MainView(self.context, self.WIDTH, self.HEIGHT)
                self.window.show_view(menu_view)

    def __init__(self, context: Context, width: int = 800, height: int = 600) -> None:
        super().__init__(context)
        self.WIDTH = width
        self.HEIGHT = height
        self._window = arcade.Window(
            self.WIDTH, self.HEIGHT, "Story Teller"
        )

    def _start(self) -> None:
        """Start the app."""
        title_view = ArcadeApp.MainView(self._context, self.WIDTH, self.HEIGHT)
        self._window.show_view(title_view)

    def _loop(self) -> None:
        try:
            arcade.run()
        except KeyboardInterrupt:
            pass

    def _clean_up(self) -> None:
        """Clean up the app."""
        arcade.close_window()


class ArcadeAppFactory(AppFactory):
    """Factory class for creating a new app."""

    DEFAULT_CONFIG = {
        "width": "800",
        "height": "600",
    }

    @classmethod
    def from_config(cls, config: ConfigParser) -> ArcadeApp:
        """Build the Arcade app.

        This method is used to build the CLI app.

        Args:
            config:

        Returns:
            ArcadeApp: The Arcade app.
        """
        context = Context.from_config(config)
        width = config.getint("arcade", "width", fallback=cls.DEFAULT_CONFIG["width"])
        height = config.getint("arcade", "height", fallback=cls.DEFAULT_CONFIG["height"])
        return ArcadeApp(context, width, height)

    @classmethod
    def from_scratch(cls) -> ArcadeApp:
        """Create a new Arcade app from scratch.

        Returns:
            ArcadeApp: A new app instance.
        """
        raise NotImplementedError()


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    # Load configuration
    load_dotenv()
    config = ConfigParser(os.environ)
    if os.path.exists(os.getenv("STORYTELLER_CONFIG_FILE")):
        config.read(os.getenv("STORYTELLER_CONFIG_FILE"))
    else:
        print("No config file found, using default settings")

    app = ArcadeAppFactory.from_config(config)
    app.run()
