import arcade
import math

class Tank(object):
    
    def __init__(self, tank_list, spritesheet = "res/tank_spritesheet_v2.png"):
        self.texture_list = arcade.load_spritesheet(spritesheet, 120, 120, 3, 3)
        self.wheel_sprite = arcade.Sprite()
        self.wheel_sprite.append_texture(self.texture_list[0])
        self.wheel_sprite.set_texture(0)
        self.wheel_sprite.center_x = 0
        self.wheel_sprite.center_y = 0
        self.wheel_sprite.set_hit_box([[-50, -50], [50, -50], [50, 50], [-50, 50]]) # 120x120 px
        
        
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


        tank_list.append(self.wheel_sprite)
        tank_list.append(self.body_sprite)
        tank_list.append(self.turret_sprite)

        self.movement_speed = 50
        self.rotation_speed = math.radians(150)
        self.rotation = math.radians(90)

        self.health = 100.0

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

    def rotate_turret(self, mouse_position, view_position):
        turret_x, turret_y = self.turret_sprite.position
        x, y = mouse_position
        x += view_position[0]
        y += view_position[1]
        if (turret_y-y) != 0:
            rad = math.atan2((turret_x-x), (y-turret_y))
            self.turret_sprite.radians = rad


    def rotate_body(self, radian):
        self.rotation += radian
        self.wheel_sprite.radians = self.rotation - math.radians(90)
        self.body_sprite.radians = self.rotation - math.radians(90)

    def fire(self):
        x, y = self.body_sprite.position
        x += 60 * math.cos(self.turret_sprite.radians + math.radians(90))
        y += 60 * math.sin(self.turret_sprite.radians + math.radians(90))
        position = (x,y)
        bullet = Bullet(position, self.turret_sprite.radians + math.radians(90), speed = 10)
        return bullet
    
    def movement(self, key_state, delta_time):
        self.change_position(0, 0)
        if key_state["LEFT"] and not key_state["RIGHT"]:
            self.rotate_body(self.rotation_speed * delta_time)
        elif key_state["RIGHT"] and not key_state["LEFT"]:
            self.rotate_body(-self.rotation_speed * delta_time)
        if key_state["UP"] and not key_state["DOWN"]:
            r = self.rotation
            y = math.sin(r) * self.movement_speed * delta_time
            x = math.cos(r) * self.movement_speed * delta_time
            self.change_position(x, y)
        elif key_state["DOWN"] and not key_state["UP"]:
            r = self.rotation
            y = -math.sin(r) * self.movement_speed * delta_time
            x = -math.cos(r) * self.movement_speed * delta_time
            self.change_position(x, y)
    
    def update(self):
        self.body_sprite.position = self.wheel_sprite.position
        self.turret_sprite.position = self.wheel_sprite.position

class Bullet(arcade.Sprite):
    def __init__(self, position, rotation, speed, *args, **kwargs):
        super().__init__("res/bullet.png", *args, **kwargs)        
        self.damage = 10
        self.position = position
        self.radians = rotation
        self.velocity = (speed * math.cos(rotation), speed * math.sin(rotation))
        self.set_hit_box([(0,-6),(14, -6), (14, 6), (0,6)])

