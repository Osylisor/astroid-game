from random import randint
import pygame
from State import State
from player import Bullet, Player, Rock, Explosion
from math import sin, cos, radians
from game import WIDTH, HEIGHT, camera_x, camera_y, BACKGROUND, SPRITE_SHEET,  explosion_sfx, shoot_sfx, high_score
import os


retro_font = pygame.font.Font(os.path.join('Assets', 'Fipps-Regular.otf'), 16)
retro_large = pygame.font.Font(os.path.join('Assets', 'Fipps-Regular.otf'), 32)


#Play State
class Play(State):
    
    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.player = Player(120, 150)
        self.bullets = []
        self.rocks = []
        self.explosions = []
        self.source_rect = pygame.Rect(0, 0,  32, 32)

        #Timer for spawning the rocks
        self.timer = 0
        self.timer_for_player = 0

        #Score for the game
        self.score = 0
        self.is_game_over = False
        self.shake_intesity = 0
        self.cam_osc = 0
        pygame.mixer.music.play(0)

    #User input
    def processInput(self, event):

        #Fire the bullets
        if(not self.is_game_over):
            if(event.type == pygame.KEYDOWN):
                if(event.key == pygame.K_SPACE):
                    self.bullets.append(Bullet(self.player.x - cos(radians(self.player.angle)) * 4,  
                    self.player.y + -sin(radians(self.player.angle))* 2, 
                    self.player.angle))
                    shoot_sfx.play(0)
                  
        else:

            #Go to the menu when the game is over
            if(event.type == pygame.KEYUP):
                if(event.key == pygame.K_SPACE):
                    self.state_manager.set_state(Menu(self.state_manager))
                    pygame.mixer.music.stop()

    #For updating everything
    def update(self, dt):

        if(not self.is_game_over):
            self.handle_bullets(dt)
            self.spawn_rocks(dt)
            self.handle_rocks(dt)
            
            if(self.player.is_active): self.handle_player(dt)

            if(self.player.lives == 0):
                self.is_game_over = True
                self.player.is_active = False


        self.shake_cam(dt)
        #Update all the explosions
        for explosion in self.explosions:
            explosion.update(dt)

            #Remove the explosion once it's done
            if(not explosion.is_active):
                self.explosions.remove(explosion)

    #For rendering everything 
    def render(self, surf):


        #Draw background
        surf.blit(BACKGROUND, (0 - camera_x, 0 - camera_y))

        #Draw all the bullets
        for bullet in self.bullets:
            bullet.draw(surf, camera_x, camera_y)

        #Draw all the rocks
        for rock in self.rocks:
            rock.render(surf, camera_x,  camera_y)

        if(self.player.is_active): self.player.draw(surf, camera_x,  camera_y)

        #Draw all the explosions
        for explosion in self.explosions:
            explosion.draw(surf)

        #Draw the HUD
        self.draw_hud(surf)

        
        if(self.is_game_over):
            s = pygame.Surface((WIDTH, HEIGHT))
            s.fill((0, 0, 0), pygame.Rect(0 , 0,  WIDTH,  HEIGHT))
            s.set_alpha(120)
            surf.blit(s, (0 , 0))

            #Render game over text
            game_over_text = retro_large.render("GAME OVER",  0, (255, 0, 0))
            surf.blit(game_over_text,  (WIDTH/2 -  game_over_text.get_width()/2, 
                                        HEIGHT/2 - game_over_text.get_height()/2))


            score_display = retro_font.render(f"Your score: {self.score}",  0, (255, 255, 0))
            surf.blit(score_display,
                ((WIDTH/2 -  score_display.get_width()/2, 
                 HEIGHT/2 + 50))
            )

    #For handling bullets
    def handle_bullets(self,dt):
        
        for bullet in self.bullets:

            #Update all the bullets
            bullet.update(dt)

            #Delete bullets that are out of bounds
            if(bullet.x <= -32 or bullet.x >= WIDTH + 32 or bullet.y <= -32 or bullet.y >= HEIGHT + 32):
                self.bullets.remove(bullet)

            
            #Check collision between bullet and rock, 
            # then remove both when the is a collision 

            for rock in self.rocks:

                if(rock.hit_box.colliderect(bullet.hit_box)):

                    try:

                        self.explosions.append(Explosion(rock.x + 16 - 100,  rock.y + 16 - 100,  9, 15))
                        if(rock in self.rocks) :self.rocks.remove(rock)
                        if(bullet in self.bullets): self.bullets.remove(bullet)
                        self.score += 10
                        explosion_sfx.play(0)
                        
                    except:
                        print("The bullet is not in the list.")

    #For spawning rocks
    def spawn_rocks(self, dt):

        self.timer = (self.timer + 1) * dt

        if(self.timer > 60 * 0.6):
            if(len(self.rocks) < 10):
                self.rocks.append(Rock(randint(-32,  WIDTH + 32),  
                                  randint(-32,  HEIGHT + 32)))

            self.timer = 0
        
    #For handling the rocks
    def handle_rocks(self, dt):

        for rock in self.rocks:
            rock.update(dt)

            if(rock.x <= -32 or rock.x > WIDTH + 32 or rock.y <= -32 or rock.y >= HEIGHT + 32):
                self.rocks.remove(rock)

    #Handle the player objects
    def handle_player(self, dt):

        #Update the player
        self.player.update(dt)

        #Stop the player from flickering 
        if(self.player.is_flickering):
            self.timer_for_player = (self.timer_for_player + 1)

            if(self.timer_for_player >= 60 * 5):
                self.player.is_flickering = False
                self.timer_for_player = 0

        #Collision between the player and the rocks
        for rock in self.rocks:
            
            if(self.player.hit_box.colliderect(rock.hit_box)):
                #Remove a life from the player
                if(not self.player.is_flickering):
                    if(self.player.lives  > 0) :self.player.lives -= 1
                    self.player.is_flickering = True
                    self.shake_intesity = 6
                    self.explosions.append(Explosion(rock.x + 16 - 100,  rock.y + 16 - 100,  9, 15))
                    if(rock in self.rocks): self.rocks.remove(rock)
                    explosion_sfx.play(0)

    #Get a sub image of a sprite sheet
    def get_sprite_sheet(self, image, x, y, width, height):
        surf = pygame.Surface((width, height))
        surf.set_colorkey((0 , 0, 0))
        self.source_rect.x = x * width
        self.source_rect.y = y * height
        self.source_rect.width = width
        self.source_rect.height = height
        surf.blit(image, (0 ,0), self.source_rect)
        return surf

    #Draw the heads up display
    def draw_hud(self, surf):

        start_x,  start_y = 32, 16
        sprite = self.get_sprite_sheet(SPRITE_SHEET,  0, 1, 32, 32)
        for i in range(self.player.lives):

            surf.blit(pygame.transform.scale(sprite,  (16,  16)), 
                     (start_x + (i * 16), start_y)
            )

    

        text_to_render = retro_font.render(str(self.score), 0, (255, 255, 255))
        score_text_x =  WIDTH/2 - text_to_render.get_width()/2
        score_text_y =  16
        surf.blit(text_to_render, (score_text_x, score_text_y))
   
    #Shake the camera
    def shake_cam(self, dt):
        global camera_x, camera_y
        self.cam_osc += 26.1 * dt

        if(self.cam_osc > 359):
            self.cam_osc = 0
        
        camera_x = cos(radians(self.cam_osc)) * self.shake_intesity *dt
        camera_y = -sin(radians(self.cam_osc)) * self.shake_intesity * dt

        self.shake_intesity = self.player.lerp(self.shake_intesity, 0, 0.08)
        


#Menu State
class Menu(State):

    def __init__(self, state_manager):
        super().__init__(state_manager)
        self.alpha = 255
        self.angle = 0

    def processInput(self, event):
        
        if(event.type == pygame.KEYUP):
            if(event.key == pygame.K_SPACE):
                self.state_manager.set_state(Play(self.state_manager))

    def update(self, dt):
        self.alpha -= 10 * dt

        self.angle +=  1.2 * dt

        if(self.alpha <= 0):
            self.alpha = 255

    def render(self, surf):

        #Draw background
        surf.blit(BACKGROUND, (0 , 0))

        #Draw the title

        high_score_text = retro_font.render(f'High Score {high_score}', 0, (255, 0,  255))
        surf.blit(high_score_text,
        
                (WIDTH/2  - high_score_text.get_width()/2, 8)
        )
       
        y_osc= sin(radians(self.angle)) * 8

        title_text = retro_large.render("Astroids", 0,  (0, 255,  255))
        surf.blit(title_text, (WIDTH/2 - title_text.get_width()/2,
                                32 + y_osc))

        #Play text
     
        play_text = retro_font.render("space to start", 0,  (255, 255, 255))
        play_text.set_alpha(self.alpha)
        surf.blit(play_text,  
                 (WIDTH/2 - title_text.get_width()/2 + 32,  HEIGHT - 48)
        )
