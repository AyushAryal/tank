import arcade
import math
from tank import Tank, CustomAStarBarrierList
import sys
import pytiled_parser


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
        self.tank = Tank(self.tank_list)
        self.tank.set_position(100, 100)

        self.bullet_list = arcade.SpriteList()

        level_map = arcade.tilemap.read_tmx(map_source)
        self.level_boundary = ((0, 0), (level_map.map_size.width * level_map.tile_size.width,
                                        level_map.map_size.height * level_map.tile_size.height))
        enemies_position = self.get_enemies_position(level_map)
        self.layers = {key: None for key in (
            "boundary", "background", "terrain", "box")}

        if level_map.background_color:
            arcade.set_background_color(level_map.background_color)
        for layer_name in self.layers.keys():
            self.layers[layer_name] = arcade.tilemap.process_layer(map_object=level_map,
                                                                   layer_name=layer_name)
        for sprite in self.layers["box"]:
            sprite.health = 20

        self.physics_engines = []
        self.physics_engines.append(arcade.PhysicsEngineSimple(
            self.tank.wheel_sprite, self.layers["boundary"]))
        self.physics_engines.append(arcade.PhysicsEngineSimple(
            self.tank.wheel_sprite, self.layers["box"]))

        self.ai_sprite_list = arcade.SpriteList()
        self.ai_objects = []
        for position in enemies_position:
            ai_obj = Tank(self.ai_sprite_list, "res/ai.png")
            ai_obj.set_position(*position)
            self.ai_objects.append(ai_obj)
            self.physics_engines.append(arcade.PhysicsEngineSimple(
                ai_obj.wheel_sprite, self.tank_list))
            self.physics_engines.append(arcade.PhysicsEngineSimple(
                self.tank.wheel_sprite, self.ai_sprite_list))
            self.physics_engines.append(arcade.PhysicsEngineSimple(
                ai_obj.wheel_sprite, self.layers["boundary"]))
            self.physics_engines.append(arcade.PhysicsEngineSimple(
                ai_obj.wheel_sprite, self.layers["box"]))

        self.path = None
        self.create_barriers()

    def create_barriers(self):
        grid_size = 64

        playing_field_left_boundary = self.level_boundary[0][0] + 64
        playing_field_right_boundary = self.level_boundary[1][0] - 64
        playing_field_top_boundary = self.level_boundary[1][1] - 64
        playing_field_bottom_boundary = self.level_boundary[0][1] + 64
        self.ai_barriers = []
        sp_list = arcade.SpriteList()
        sp_list.extend(self.layers["box"])
        sp_list.extend(self.layers["boundary"])
        barrier_list = CustomAStarBarrierList(None, sp_list, grid_size,
                                              playing_field_left_boundary,
                                              playing_field_right_boundary,
                                              playing_field_bottom_boundary,
                                              playing_field_top_boundary)
        for ai in self.ai_objects:
            barrier_list.moving_sprite = self.ai_objects[0].wheel_sprite
            self.ai_barriers.append(barrier_list)

    def get_enemies_position(self, level_map):
        object_layers = filter(lambda x: isinstance(
            x, pytiled_parser.objects.ObjectLayer), level_map.layers)
        location = []
        for layer in object_layers:
            if layer.name == "enemies":
                for obj in layer.tiled_objects:
                    location.append(
                        (obj.location.x, self.level_boundary[1][1] - obj.location.y))
        return location

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
        self.tank.movement(self.key_state, delta_time)

        for engine in self.physics_engines:
            engine.update()

        self.bullet_list.update()
        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(
                bullet, self.layers["boundary"])
            hit_list.extend(arcade.check_for_collision_with_list(
                bullet, self.layers["box"]))

            items = arcade.check_for_collision_with_list(
                bullet, self.layers["box"])
            removed = False
            for item in items:
                if hasattr(item, "health"):
                    item.health -= bullet.damage
                    if item.health <= 0:
                        item.remove_from_sprite_lists()
                        removed = True
            if removed:
                self.create_barriers()
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()

        self.tank.update()
        self.ai_objects[0].update()
        self.tank.rotate_turret(self.mouse_position,
                                (self.view_left, self.view_bottom))

        enemy = self.ai_objects[0].wheel_sprite
        enemy_x,enemy_y=enemy.position
        tank_x,tank_y=self.tank.wheel_sprite.position
        distance_between_ai_and_tank= ((tank_x-enemy_x)**2 +(tank_y-enemy_y)**2)**(0.5)
        if distance_between_ai_and_tank<1000:
            self.path = arcade.astar_calculate_path(enemy.position,
                                                    self.tank_list[0].position,
                                                    self.ai_barriers[0],
                                                    diagonal_movement=True)
            if self.path and len(self.path) > 1:
                x1, y1 = self.path[1]
                x2, y2 = self.ai_objects[0].wheel_sprite.position
                direction = (x1-x2), (y1-y2)
                x, y = direction
                magnitude = (x**2 + y**2)**0.5
                unit_vector = x/magnitude, y/magnitude
                velocity = self.ai_objects[0].movement_speed
                req_vector = unit_vector[0]*velocity, unit_vector[1]*velocity
                delta_position = req_vector[0] * \
                    delta_time, req_vector[1] * delta_time

                angle = math.atan2(*unit_vector[::-1])-self.ai_objects[0].rotation
                self.ai_objects[0].rotate_body(angle)
                #ai turret roatation
                x, y = self.tank.body_sprite.position
                turret_x, turret_y = self.ai_objects[0].turret_sprite.position
                if (turret_y-y) != 0:
                    rad = math.atan2((turret_x-x), (y-turret_y))
                    self.ai_objects[0].turret_sprite.radians = rad

                #ai bullet firing
                self.ai_objects[0].change_position(*delta_position)
                self.ai_objects[0].ai_fire_dt += delta_time
                if (self.ai_objects[0].ai_fire_dt > (1/self.ai_objects[0].ai_fire_rate)):
                    self.bullet_list.append(self.ai_objects[0].fire())
                    self.ai_objects[0].ai_fire_dt -= (1 /
                                                    self.ai_objects[0].ai_fire_rate)
        self.scroll(self.tank.body_sprite)

    def draw_health(self):
        height_offset = 15
        healthbar_width = 70
        healthbar_height = 10
        if hasattr(self.tank, "health"):
            sprite = self.tank.body_sprite
            if self.tank.health != 100:
                arcade.draw_rectangle_filled(sprite.center_x, sprite.center_y + sprite.height +
                                             height_offset, healthbar_width, healthbar_height, arcade.csscolor.WHITE)
                width = healthbar_width * self.tank.health / 100
                width_reduced = healthbar_width - width
                arcade.draw_rectangle_filled(sprite.center_x - width_reduced / 2, sprite.center_y +
                                             sprite.height + height_offset, width, healthbar_height, arcade.csscolor.GREEN)

    def scroll(self, follow_sprite):
        left_viewport_margin = 250
        right_viewport_margin = 250
        bottom_viewport_margin = 250
        top_viewport_margin = 250

        changed = False

        # Scroll left
        left_boundary = self.view_left + left_viewport_margin
        if self.tank.body_sprite.left < left_boundary and self.view_left > self.level_boundary[0][0]:
            self.view_left -= left_boundary - self.tank.body_sprite.left
            changed = True

        # Scroll right
        right_boundary = self.view_left + \
            self.window_size[0] - right_viewport_margin
        if self.tank.body_sprite.right > right_boundary and self.view_left + self.window_size[0] < self.level_boundary[1][0]:
            self.view_left += self.tank.body_sprite.right - right_boundary
            changed = True

        # Scroll up
        top_boundary = self.view_bottom + \
            self.window_size[1] - top_viewport_margin
        if self.tank.body_sprite.top > top_boundary and self.view_bottom + self.window_size[1] < self.level_boundary[1][1]:
            self.view_bottom += self.tank.body_sprite.top - top_boundary
            changed = True

        # Scroll down
        bottom_boundary = self.view_bottom + bottom_viewport_margin
        if self.tank.body_sprite.bottom < bottom_boundary and self.view_bottom > self.level_boundary[0][1]:
            self.view_bottom -= bottom_boundary - self.tank.body_sprite.bottom
            changed = True

        if changed:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)
            arcade.set_viewport(self.view_left,
                                int(self.window_size[0] + self.view_left),
                                self.view_bottom,
                                self.window_size[1] + self.view_bottom)

    def on_draw(self):
        arcade.start_render()

        for value in self.layers.values():
            value.draw()
        self.bullet_list.draw()
        self.ai_sprite_list.draw()
        self.tank_list.draw()
        self.draw_health()

        if self.path:
            arcade.draw_line_strip(self.path, arcade.color.BLUE, 2)


def main():

    key_mappings = {
        "UP": arcade.key.W,
        "DOWN": arcade.key.S,
        "LEFT": arcade.key.A,
        "RIGHT": arcade.key.D,
    }

    window = GameWindow(1024, 700, "Fun with Tanks", key_mappings)
    window.setup_level()
    arcade.run()


if __name__ == "__main__":
    main()
