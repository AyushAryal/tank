import arcade
import math

class Tank(object):
    def __init__(self):
        self.texture_list = arcade.load_spritesheet("res/tank_spritesheet_v1.png", 800, 800, 3, 3)
        self.wheel_sprite = arcade.Sprite(scale = 0.15)
        self.wheel_sprite.append_texture(self.texture_list[0])
        self.wheel_sprite.set_texture(0)
        self.wheel_sprite.center_x = 0
        self.wheel_sprite.center_y = 0
        
        self.body_sprite = arcade.Sprite(scale = 0.15)
        self.body_sprite.append_texture(self.texture_list[1])
        self.body_sprite.set_texture(0)
        self.body_sprite.center_x = 0
        self.body_sprite.center_y = 0
        
        self.turret_sprite = arcade.Sprite(scale = 0.15)
        self.turret_sprite.append_texture(self.texture_list[2])
        self.turret_sprite.set_texture(0)
        self.turret_sprite.center_x = 0
        self.turret_sprite.center_y = 0

        self.movement_speed = 5

    def set_position(self, x, y):
        self.wheel_sprite.center_x = x
        self.wheel_sprite.center_y = y 

        self.body_sprite.center_x = x
        self.body_sprite.center_y = y 

        self.turret_sprite.center_x = x
        self.turret_sprite.center_y = y

    def change_position(self, x, y):

        if x is not None:
            self.wheel_sprite.change_x = x        
            self.body_sprite.change_x = x
            self.turret_sprite.change_x = x

        if y is not None:
            self.wheel_sprite.change_y = y 
            self.body_sprite.change_y = y 
            self.turret_sprite.change_y = y

    def rotate_turret(self, radian):
            self.turret_sprite.radians = radian

class GameWindow(arcade.Window):
    def __init__(self, width, height, title, key_mappings):
        super().__init__(width, height, title)
        self.key_mappings = key_mappings
        self.key_state = {key: None for key in self.key_mappings.keys()}
        self.tank_list = None
        self.wall_list = None
        self.player_speed = None
        self.mouse_position = (0,0)
        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self):
        self.tank_list = arcade.SpriteList()
        self.tank = Tank()
        self.tank_list.append(self.tank.wheel_sprite)
        self.tank_list.append(self.tank.body_sprite)
        self.tank_list.append(self.tank.turret_sprite)
        self.tank.set_position(100, 100)        

        self.wall_list = arcade.SpriteList()

        self.physics_engines = []
        self.physics_engines.append(arcade.PhysicsEngineSimple(self.tank.wheel_sprite, self.wall_list))
        self.physics_engines.append(arcade.PhysicsEngineSimple(self.tank.body_sprite, self.wall_list))
        self.physics_engines.append(arcade.PhysicsEngineSimple(self.tank.turret_sprite, self.wall_list))

    def on_key_press(self, key, modifiers):
        for key_k in self.key_state.keys():
            if self.key_mappings[key_k] == key:
                self.key_state[key_k] = True
    
    def on_key_release(self, key, modifiers):
        for key_k in self.key_state.keys():
            if self.key_mappings[key_k] == key:
                self.key_state[key_k] = False

    def movement(self):
        self.tank.change_position(0,0)
        if self.key_state["UP"] and not self.key_state["DOWN"]:
            self.tank.change_position(None, self.tank.movement_speed)
        elif self.key_state["DOWN"] and not self.key_state["UP"]:
            self.tank.change_position(None, -self.tank.movement_speed)
        if self.key_state["LEFT"] and not self.key_state["RIGHT"]:
            self.tank.change_position(-self.tank.movement_speed,None)
        elif self.key_state["RIGHT"] and not self.key_state["LEFT"]:
            self.tank.change_position(self.tank.movement_speed,None)

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
        for engine in self.physics_engines:
            engine.update()
        self.rotate_turret()

    def on_draw(self):
        arcade.start_render()
        self.tank_list.draw()
        # Code to draw the screen goes here


def main():

    key_mappings = {
        "UP" : arcade.key.W,
        "DOWN": arcade.key.S,
        "LEFT": arcade.key.A,
        "RIGHT": arcade.key.D,
    }

    window = GameWindow(800, 600, "My Arcade game", key_mappings)
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()
