import arcade
import math
from tank import Tank

class GameWindow(arcade.Window):
    def __init__(self, width, height, title, key_mappings):
        super().__init__(width, height, title)
        self.key_mappings = key_mappings
        self.key_state = {key: None for key in self.key_mappings.keys()}
        self.mouse_position = (0,0)
        arcade.set_background_color(arcade.csscolor.BLACK)

    def setup(self):
        self.tank_list = arcade.SpriteList()
        self.tank = Tank()
        self.tank_list.append(self.tank.wheel_sprite)
        self.tank_list.append(self.tank.body_sprite)
        self.tank_list.append(self.tank.turret_sprite)
        self.tank.set_position(100, 100)        

        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        box_sprite = arcade.Sprite("res/box.png")
        box_sprite.center_x = 200
        box_sprite.center_y = 200
        self.wall_list.append(box_sprite)

        self.bullet_list = arcade.SpriteList()
       
        self.physics_engines = []
        self.physics_engines.append(arcade.PhysicsEngineSimple(self.tank.wheel_sprite, self.wall_list))


    def setup_level(self):
        self.tank_list = arcade.SpriteList()
        self.tank = Tank()
        self.tank_list.append(self.tank.wheel_sprite)
        self.tank_list.append(self.tank.body_sprite)
        self.tank_list.append(self.tank.turret_sprite)
        self.tank.set_position(100, 100)        

        self.bullet_list = arcade.SpriteList()

        map_name = "res/level.tmx"
        my_map = arcade.tilemap.read_tmx(map_name)
        self.wall_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name="boundary")
        self.box_list = arcade.tilemap.process_layer(my_map,"box")
        self.foreground_list =  arcade.tilemap.process_layer(my_map,"foreground")
        self.background_list =  arcade.tilemap.process_layer(my_map,"background")
        self.terrain_list =  arcade.tilemap.process_layer(my_map,"terrain")

        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)
        self.physics_engines = []
        self.physics_engines.append(arcade.PhysicsEngineSimple(self.tank.wheel_sprite, self.wall_list))


    def on_key_press(self, key, modifiers):
        for key_k in self.key_state.keys():
            if self.key_mappings[key_k] == key:
                self.key_state[key_k] = True
    
    def on_key_release(self, key, modifiers):
        for key_k in self.key_state.keys():
            if self.key_mappings[key_k] == key:
                self.key_state[key_k] = False
    
    def on_mouse_press(self, x, y, button, modifiers):
        bullet = self.tank.fire()
        self.bullet_list.append(bullet)

    def movement(self):
        self.tank.change_position(0,0)

        if self.key_state["LEFT"] and not self.key_state["RIGHT"]:
            self.tank.rotate_body(self.tank.rotation_speed)
        elif self.key_state["RIGHT"] and not self.key_state["LEFT"]:
            self.tank.rotate_body(-self.tank.rotation_speed)
        if self.key_state["UP"] and not self.key_state["DOWN"]:
            r = self.tank.rotation
            y = math.sin(r) * self.tank.movement_speed
            x = math.cos(r) * self.tank.movement_speed
            self.tank.change_position(x,y)
        elif self.key_state["DOWN"] and not self.key_state["UP"]:
            r = self.tank.rotation
            y = -math.sin(r) * self.tank.movement_speed
            x = -math.cos(r) * self.tank.movement_speed
            self.tank.change_position(x,y)

    def rotate_turret(self):
        turret_x, turret_y = self.tank.turret_sprite.position

        x,y = self.mouse_position
        if (turret_y-y) != 0:
            rad = math.atan2((turret_x-x),(y-turret_y))
            self.tank.rotate_turret(rad)

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_position = (x+dx, y+dy)
        self.rotate_turret()

    def on_update(self, delta_time):
        """ Movement and game logic """
        self.movement()
        self.bullet_list.update()

        for bullet in self.bullet_list:
            hit_list = arcade.check_for_collision_with_list(bullet, self.wall_list)
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()

        for engine in self.physics_engines:
            engine.update()
        self.tank.body_sprite.position = self.tank.wheel_sprite.position
        self.tank.turret_sprite.position = self.tank.wheel_sprite.position
        self.rotate_turret()

    def on_draw(self):
        arcade.start_render()
        self.box_list.draw()
        self.background_list.draw()
        self.terrain_list.draw()
        self.foreground_list.draw()
        self.wall_list.draw()
        self.bullet_list.draw()
        self.tank_list.draw()


def main():

    key_mappings = {
        "UP" : arcade.key.W,
        "DOWN": arcade.key.S,
        "LEFT": arcade.key.A,
        "RIGHT": arcade.key.D,
    }

    window = GameWindow(800, 600, "My Arcade game", key_mappings)
    window.setup_level()
    arcade.run()


if __name__ == "__main__":
    main()
