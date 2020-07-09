import arcade
import math

class Tank(object):
    def __init__(self):
        self.texture_list = arcade.load_spritesheet("res/tank_spritesheet_v2.png", 120, 120, 3, 3)
        self.wheel_sprite = arcade.Sprite()
        self.wheel_sprite.append_texture(self.texture_list[0])
        self.wheel_sprite.set_texture(0)
        self.wheel_sprite.center_x = 0
        self.wheel_sprite.center_y = 0
        self.wheel_sprite.set_hit_box([[-50, -50], [50, -50], [50, 50], [-50, 50]])
        
        
        self.body_sprite = arcade.Sprite()
        self.body_sprite.append_texture(self.texture_list[1])
        self.body_sprite.set_texture(0)
        self.body_sprite.center_x = 0
        self.body_sprite.center_y = 0
        
        self.turret_sprite = arcade.Sprite()
        self.turret_sprite.append_texture(self.texture_list[2])
        self.turret_sprite.set_texture(0)
        self.turret_sprite.center_x = 0
        self.turret_sprite.center_y = 0

        self.movement_speed = 5
        self.rotation_speed = math.radians(3)
        self.rotation = math.radians(90)

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


    def rotate_body(self, radian):
        self.rotation += radian
        self.wheel_sprite.radians = self.rotation - math.radians(90)
        self.body_sprite.radians = self.rotation - math.radians(90)