from __future__ import annotations
from configparser import ConfigParser
from typing import Any

import arcade
import arcade.gui

from story_teller.app.base import (
    App, AppFactory, Context, StateMachine,
    Event, AlertSystemEvent, ChoiceInputEvent, TextInputEvent, QuitEvent,
    RenderData, RenderControlsData, RenderSceneLayoutType,
)

FONT = "Kenney Future"

class UIFlatPayloadButton(arcade.gui.UIFlatButton):
    def __init__(self,
                 x: float = 0,
                 y: float = 0,
                 width: float = 100,
                 height: float = 50,
                 text="",
                 payload: Any = None,
                 size_hint=None,
                 size_hint_min=None,
                 size_hint_max=None,
                 style=None,
                 **kwargs):
        super().__init__(x, y, width, height, text, size_hint, size_hint_min, size_hint_max, style, **kwargs)
        self.payload = payload


class ArcadeApp(App):

    class BaseView(arcade.View):

        def __init__(self, context: Context, state_machine: StateMachine, width: int = 800, height: int = 600) -> None:
            super().__init__()
            self.WIDTH = width
            self.HEIGHT = height
            self.context = context
            self.state_machine = state_machine
            self.events = []
            self.last_render_data = None

        def on_update(self, delta_time: float) -> None:
            """ All the logic to move, and the game logic goes here. """
            render_data = self.state_machine.get_render_data()
            match render_data.layout:
                case RenderSceneLayoutType.MAIN:
                    if not isinstance(self, ArcadeApp.MainView):
                        main_view = ArcadeApp.MainView(self.context, self.state_machine, self.WIDTH, self.HEIGHT)
                        main_view.setup()
                        self.window.show_view(main_view)
                        return
                case RenderSceneLayoutType.INTERACTION:
                    if not isinstance(self, ArcadeApp.InteractionView):
                        interaction_view = ArcadeApp.InteractionView(self.context, self.state_machine, self.WIDTH, self.HEIGHT)
                        interaction_view.setup()
                        self.window.show_view(interaction_view)
                        return
                case RenderSceneLayoutType.MOVIE:
                    if not isinstance(self, ArcadeApp.MovieView):
                        movie_view = ArcadeApp.MovieView(self.context, self.state_machine, self.WIDTH, self.HEIGHT)
                        movie_view.setup()
                        self.window.show_view(movie_view)
                        return
            if self.last_render_data is None:
                self.last_render_data = render_data
            elif self.last_render_data != render_data:
                self.setup()
                self.last_render_data = render_data
            else:
                self.state_machine.handle_events(self.events)
                self.events = []

        def on_draw(self):
            """ Draw the View"""
            self.clear()
            self.manager.draw()

        def _on_click_botton(self, event: arcade.gui.events.UIOnClickEvent) -> None:
            """ Start the game """
            botton_payload = event.source.payload
            self.events.append(
                ChoiceInputEvent(choice=botton_payload)
            )

        def _add_buttons(self, controls: RenderControlsData) -> list:
            buttons = []
            for enabled, text, name in zip(controls.choices_enabled, controls.choices_text, controls.choices_name):
                if not enabled:
                    continue
                button = UIFlatPayloadButton(text=text, payload=name, width=200)
                button.on_click = self._on_click_botton
                buttons.append(button)
            return buttons

    class MainView(BaseView):
        """ Class that manages the 'main' view. """

        def setup(self) -> None:
            """ This should set up your game and get it ready to play """
            # --- Required for all code that uses UI element,
            # a UIManager to handle the UI.

            render_data = self.state_machine.get_render_data()

            self.manager = arcade.gui.UIManager()
            self.manager.enable()

            # Set background color
            arcade.set_background_color(arcade.color.DARK_BLUE_GRAY)

            # Create a vertical BoxGroup to align buttons
            self.v_box = arcade.gui.UIBoxLayout()

            # Add the title
            if " - " in render_data.scene.title:
                title_content = render_data.scene.title.split(' - ')
                title_0 = arcade.gui.UITextArea(
                    text=title_content[0],
                    font_size=32,
                    align="center",
                    font_name=FONT,
                )
                title_1 = arcade.gui.UILabel(
                    text=title_content[1],
                    font_size=20,
                    align="center",
                    font_name=FONT,
                )
                self.v_box.add(title_0.with_space_around(bottom=10))
                self.v_box.add(title_1.with_space_around(bottom=50))
            else:
                title = arcade.gui.UILabel(
                    text=render_data.scene.title,
                    font_size=20,
                    align="center",
                    font_name=FONT,
                )
                self.v_box.add(title.with_space_around(bottom=50))

            # Create the buttons
            self.h_box = arcade.gui.UIBoxLayout(vertical=False)
            buttoms = self._add_buttons(render_data.controls)
            # start_button = UIFlatPayloadButton(text="Start Game", payload="start", cwidth=200)
            # start_button.on_click = self._on_click_botton
            # self.h_box.add(start_button.with_space_around(right=20))
            # change_story_button = UIFlatPayloadButton(text="Change Story", payload="change_story", width=200)
            # change_story_button.on_click = self._on_click_botton
            # self.h_box.add(change_story_button.with_space_around(right=20))
            for button in buttoms:
                self.h_box.add(button.with_space_around(right=20))

            self.v_box.add(self.h_box.with_space_around(top=20))

            # Create a widget to hold the v_box widget, that will center the buttons
            self.manager.add(
                arcade.gui.UIAnchorWidget(
                    anchor_x="center_x",
                    anchor_y="center_y",
                    child=self.v_box)
            )

        # def on_draw(self):
        #     """ Draw the view """
        #     self.clear()
        #     self.manager.draw()
            # # Show Title
            # arcade.draw_text(
            #     render_data.scene.title, self.WIDTH / 2, self.HEIGHT / 2,
            #     arcade.color.BLACK, font_size=30, anchor_x="center"
            # )
            # # Alerts UI
            # alert = render_data.hud.alert
            # if alert is not None:
            #     arcade.draw_text(
            #         alert.message, self.WIDTH / 2, self.HEIGHT / 2 - 50,
            #         arcade.color.BLACK, font_size=20, anchor_x="center"
            #     )

            # # Description UI
            # description = render_data.scene.description
            # arcade.draw_text(
            #     description, self.WIDTH / 2, self.HEIGHT / 2 - 100,
            #     arcade.color.BLACK, font_size=20, anchor_x="center"
            # )

            # # Control UI
            # controls = render_data.controls

        def on_mouse_press(self, _x, _y, _button, _modifiers):
            """ Use a mouse press to advance to the 'game' view. """
            # game_view = ArcadeApp.InteractionView(self.context, self.state_machine, self.WIDTH, self.HEIGHT)
            # game_view.setup()
            # self.window.show_view(game_view)
            pass

    class InteractionView(BaseView):
        """ Manage the 'game' view for our program. """

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
                game_over_view = ArcadeApp.MovieView(self.context, self.state_machine, self.WIDTH, self.HEIGHT)
                self.window.show_view(game_over_view)

    class MovieView(BaseView):
        """ Class to manage the movie view """

        def setup(self):
            pass

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
                menu_view = ArcadeApp.MainView(self.context, self.state_machine, self.WIDTH, self.HEIGHT)
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
        title_view = ArcadeApp.MainView(self._context, self._state_machine, self.WIDTH, self.HEIGHT)
        title_view.setup()
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
