import arcade
import math
from tank import Tank


class GameWindow(arcade.Window):
    def __init__(self, width, height, title, key_mappings):
        super().__init__(width, height, title)
        self.window_size = (width, height)
        self.key_mappings = key_mappings
        self.key_state = {key: None for key in self.key_mappings.keys()}
        self.mouse_position = (0, 0)
        self.view_left = 0
        self.view_bottom = 0

    def setup_level(self, map_source="res/level.tmx"):
        self.tank_list = arcade.SpriteList()
        self.tank = Tank()
        self.tank_list.append(self.tank.wheel_sprite)
        self.tank_list.append(self.tank.body_sprite)
        self.tank_list.append(self.tank.turret_sprite)
        self.tank.set_position(100, 100)

        self.bullet_list = arcade.SpriteList()

        my_map = arcade.tilemap.read_tmx(map_source)
        self.layers = {key: None for key in (
            "boundary", "background", "terrain", "box")}

        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

        for layer_name in self.layers.keys():
            self.layers[layer_name] = arcade.tilemap.process_layer(map_object=my_map,
                                                                   layer_name=layer_name)

        def calculate_boundary(boundary_layer):
            x_list = []
            y_list = []
            tile_width = boundary_layer[0].width // 2
            tile_height = boundary_layer[0].height // 2
            for boundary in boundary_layer:
                x_list.append(boundary.center_x)
                y_list.append(boundary.center_y)
            return ((min(x_list)-tile_width, min(y_list)-tile_height), (max(x_list)+tile_width, max(y_list)+tile_height))

        self.level_boundary = calculate_boundary(self.layers["boundary"])
        print(self.level_boundary)

        self.physics_engines = []
        self.physics_engines.append(arcade.PhysicsEngineSimple(
            self.tank.wheel_sprite, self.layers["boundary"]))
        self.physics_engines.append(arcade.PhysicsEngineSimple(
            self.tank.wheel_sprite, self.layers["box"]))

    def on_key_press(self, key, modifiers):
        for key_k in self.key_state.keys():
            if self.key_mappings[key_k] == key:
                self.key_state[key_k] = True

    def on_key_release(self, key, modifiers):
        for key_k in self.key_state.keys():
            if self.key_mappings[key_k] == key:
                self.key_state[key_k] = False

    def on_mouse_press(self, x, y, button, modifiers):
        #print(x, y)
        self.bullet_list.append(self.tank.fire())

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_position = (x+dx, y+dy)
        self.tank.rotate_turret(self.mouse_position,
                                (self.view_left, self.view_bottom))

    def on_update(self, delta_time):
        """ Movement and game logic """
        self.tank.movement(self.key_state)

        for engine in self.physics_engines:
            engine.update()
        
        self.bullet_list.update()
        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(
                bullet, self.layers["boundary"])
            hit_list.extend(arcade.check_for_collision_with_list(
                bullet, self.layers["box"]))
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()

        self.tank.body_sprite.position = self.tank.wheel_sprite.position
        self.tank.turret_sprite.position = self.tank.wheel_sprite.position
        self.tank.rotate_turret(self.mouse_position,
                                (self.view_left, self.view_bottom))

        self.scroll(self.tank.body_sprite)
    
    
    def draw_health(self):
        height_offset = 15
        healthbar_width = 70
        healthbar_height = 10
        if hasattr(self.tank, "health"):
            sprite = self.tank.body_sprite
            arcade.draw_rectangle_filled(sprite.center_x, sprite.center_y + sprite.height + height_offset, healthbar_width, healthbar_height, arcade.csscolor.GREEN)

    def scroll(self, follow_sprite):
        LEFT_VIEWPORT_MARGIN = 250
        RIGHT_VIEWPORT_MARGIN = 250
        BOTTOM_VIEWPORT_MARGIN = 250
        TOP_VIEWPORT_MARGIN = 250

        changed = False

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.tank.body_sprite.left < left_boundary and self.view_left > self.level_boundary[0][0]:
            self.view_left -= left_boundary - self.tank.body_sprite.left
            changed = True

        # Scroll right
        right_boundary = self.view_left + \
            self.window_size[0] - RIGHT_VIEWPORT_MARGIN
        if self.tank.body_sprite.right > right_boundary and self.view_left + self.window_size[0] < self.level_boundary[1][0]:
            self.view_left += self.tank.body_sprite.right - right_boundary
            changed = True

        # Scroll up
        top_boundary = self.view_bottom + \
            self.window_size[1] - TOP_VIEWPORT_MARGIN
        if self.tank.body_sprite.top > top_boundary and self.view_bottom + self.window_size[1] < self.level_boundary[1][1]:
            self.view_bottom += self.tank.body_sprite.top - top_boundary
            changed = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.tank.body_sprite.bottom < bottom_boundary and self.view_bottom > self.level_boundary[0][1]:
            self.view_bottom -= bottom_boundary - self.tank.body_sprite.bottom
            changed = True

        if changed:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                self.window_size[0] + self.view_left,
                                self.view_bottom,
                                self.window_size[1] + self.view_bottom)

    def on_draw(self):
        arcade.start_render()

        for value in self.layers.values():
            value.draw()
        self.bullet_list.draw()
        self.tank_list.draw()
        self.draw_health()


def main():

    key_mappings = {
        "UP": arcade.key.W,
        "DOWN": arcade.key.S,
        "LEFT": arcade.key.A,
        "RIGHT": arcade.key.D,
    }

    window = GameWindow(1024, 700, "My Arcade game", key_mappings)
    window.setup_level()
    arcade.run()


if __name__ == "__main__":
    main()
