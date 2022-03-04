import pygame
from math import sin, cos, radians
from pygame.constants import K_LEFT, K_RIGHT, K_UP

import game 
from game import  SPRITE_SHEET, EXPLOSION
from random import randint, random

#from play import Play



#Player class
class Player:


    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.angular_vel = 1.7
        self.thrust = 0
        self.source_rect = pygame.Rect(0 , 32, 32, 32)
        self.origin_x = 16
        self.origin_y  = 16
        self.hit_box = pygame.Rect(self.x,  self.y,  24, 24)
        self.lives = 3
        self.is_flickering = False
        self.timer = 0
        self.image_alpha = 255
        self.is_active = True

    def get_sprite_sheet(self, image, x, y, width, height):
        surf = pygame.Surface((width, height))
        surf.set_colorkey((0 , 0, 0))
        self.source_rect.x = x * width
        self.source_rect.y = y * height
        self.source_rect.width = width
        self.source_rect.height = height
        surf.blit(image, (0 ,0), self.source_rect)
        return surf

    def update(self, dt):
      
       
        self.warp_player()
        self.move_player(dt)

        if(self.is_flickering):
            self.flicker(dt)
        else:
            self.image_alpha = 255
        
    def draw(self, surf, cam_x, cam_y):
       
        sprite_to_draw = self.get_sprite_sheet(SPRITE_SHEET,0, 1, 32, 32)
        sprite_to_draw.set_alpha(self.image_alpha)
        surf.blit(pygame.transform.rotate(sprite_to_draw, 90 + self.angle), 

        ((self.x - sprite_to_draw.get_width()/2) - cam_x,  
        (self.y - sprite_to_draw.get_height()/2) - cam_y))
        
    def lerp(self, start, last, change):

        value = start + (last - start) * change
        return value

    def warp_player(self):

        #Wrap the sprite aroud the x-axis
        if(self.x <= -32): self.x = game.WIDTH
        if(self.x >= game.WIDTH + 32): self.x = -32

        #Wrap the sprite around the y-axis

        if(self.y <= -32): self.y = game.HEIGHT
        if(self.y >= game.HEIGHT + 32):self.y = -32 

    def move_player(self, dt):
        
        key_pressed = pygame.key.get_pressed()
    

        if(key_pressed[K_LEFT]):
            self.angle += self.angular_vel * dt
        
        if(key_pressed[K_RIGHT]):
            self.angle -= self.angular_vel * dt

        if(key_pressed[K_UP]):
            self.thrust = self.lerp(self.thrust, 4, 0.04)
        else:
            if(self.thrust > 0): self.thrust = self.lerp(self.thrust, 0, 0.04)

        self.x += self.thrust * cos(radians(90 + self.angle)) * dt
        self.y += -self.thrust * sin(radians(90 + self.angle)) * dt

        #Update the position of the hit box
        self.hit_box.x = self.x 
        self.hit_box.y = self.y

    def flicker(self, dt):
        self.timer = (self.timer + 1) * dt

        if(self.timer >  60 * 0.07):
            
            if(self.image_alpha == 255):
                self.image_alpha = 0
            else:
                self.image_alpha = 255
            
            self.timer = 0

#Bullet class
class Bullet:

    def __init__(self, x, y ,  angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 9
        self.source_rect = pygame.Rect(0, 0,  32, 32)
        self.hit_box = pygame.Rect(self.x + 16,  self.y + 16,  16, 16)

    def update(self, dt):
        self.x += -self.speed * sin(radians( self.angle)) * dt
        self.y += -self.speed * cos(radians( self.angle)) * dt

        #Update the position of the hit box
        self.hit_box.x = self.x + 16
        self.hit_box.y = self.y + 16
    
    def get_sprite_sheet(self, image, x, y, width, height):
        surf = pygame.Surface((width, height))
        surf.set_colorkey((0 , 0, 0))
        self.source_rect.x = x * width
        self.source_rect.y = y * height
        self.source_rect.width = width
        self.source_rect.height = height
        surf.blit(image, (0 ,0), self.source_rect)
        return surf

    def draw(self, surf, cam_x, cam_y):

        surf.blit(
            pygame.transform.rotate(self.get_sprite_sheet(SPRITE_SHEET, 0, 2, 32, 32 ), 90 + self.angle),
            (self.x - cam_x, self.y - cam_y)
        )

#Rock class
class Rock:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 0.2 + random() * 3
        self.vel_x = cos(radians(random() * 359)) * self.speed
        self.vel_y = -sin(radians(random() * 359)) * self.speed
        self.angle = 0
        self.angular_vel = 0
        self.index = randint(0, 2)
        self.source_rect = pygame.Rect(0, 0,  32, 32)
        self.hit_box =  pygame.Rect(self.x + 16,  self.y + 16,  16, 16)
       

    def update(self, dt):
        self.x +=  self.vel_x * dt
        self.y +=  self.vel_y * dt

        #Update the hit box location

        self.hit_box.x = self.x + 16
        self.hit_box.y =  self.y + 16

        self.angle += self.speed/2

    def get_sprite_sheet(self, image, x, y, width, height):
        surf = pygame.Surface((width, height))
        surf.set_colorkey((0 , 0, 0))
        self.source_rect.x = x * width
        self.source_rect.y = y * height
        self.source_rect.width = width
        self.source_rect.height = height
        surf.blit(image, (0 ,0), self.source_rect)
        return surf


    def render(self, surf, cam_x, cam_y):
        surf.blit(
            pygame.transform.rotate(
                self.get_sprite_sheet(SPRITE_SHEET,  self.index, 0, 32, 32),
                self.angle
            ),

            (self.x - cam_x, self.y - cam_y)
        )


#Explosion animation

class Explosion:

    def __init__(self, x, y, max_frame, frame_rate):
        self.x = x
        self.y = y
        self.source_rect = pygame.Rect(0, 0,  32, 32)
        self.current_frame = 0
        self.timer = 0
        self.max_frame = max_frame
        self.frame_rate = frame_rate

        if(self.frame_rate == 0): self.frame_rate = 1
        self.is_active = True

    def update(self, dt):
        self.animate(dt)

    def get_sprite_sheet(self, image, x, y, width, height):
        surf = pygame.Surface((width, height))
        surf.set_colorkey((0 , 0, 0))
        self.source_rect.x = x * width
        self.source_rect.y = y * height
        self.source_rect.width = width
        self.source_rect.height = height
        surf.blit(image, (0 ,0), self.source_rect)
        return surf

    def draw(self, surf):
        sprite = self.get_sprite_sheet(EXPLOSION, self.current_frame, 0 , 200 ,200)
        surf.blit(sprite, (self.x,  self.y))


    def animate(self, dt):

        self.timer +=  1


        if(self.timer > 60/self.frame_rate):
            self.current_frame += 1
            self.timer = 0


        if(self.current_frame >=  self.max_frame):
            self.current_frame = self.max_frame
            self.is_active = False

