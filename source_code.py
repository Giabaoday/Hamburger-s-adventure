import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path



pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
FPS = 60

screen_width = 800
screen_height = 800

screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Hamburger`s adventure')

font3 = pygame.font.Font("Pixeboy-z8XGD.ttf", 50)
font2 = pygame.font.Font("Pixeboy-z8XGD.ttf", 80)
font = pygame.font.Font("Pixeboy-z8XGD.ttf", 30, )

#bien cua game
tile_size = 40
white = (0,0,0)
game_over = 0
main_menu = True
level = 1
max_level = 2
score = 0

pygame.mixer.music.load('Cloud Country - ConcernedApe.mp3')
pygame.mixer.music.play(-1, 0.0, 5000)
strawberry_fx = pygame.mixer.Sound('super-mario-coin-sound.mp3')
strawberry_fx.set_volume(0.6)
jump_fx = pygame.mixer.Sound('maro-jump-sound-effect_1.mp3')
jump_fx.set_volume(0.4)
gameover_fx = pygame.mixer.Sound('8d82b5_new_super_mario_bros_death_sound_effect.mp3')
gameover_fx.set_volume(0.5)


#load images


sky_img = pygame.image.load('sky1.png')
ham_img = pygame.image.load('ham.png')
restart = pygame.image.load('restart.png')
restart_img = pygame.transform.scale(restart,(4*tile_size,2*tile_size))
start_img = pygame.image.load('start.png')
exit_img = pygame.image.load('exit.png')
portal_img = pygame.image.load('portal.png')
strawberry_img = pygame.image.load('strawberry.png')

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img ,(x, y))

#reset level
def reset_level(level):
    player.reset(100, screen_height - 80)
    slime_group.empty()
    spike_group.empty()
    portal_group.empty()
    if path.exists(f'level{level}_data.pkl'):
        pickle_in = open(f'level{level}_data.pkl','rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world


class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False

        #get mouse postition
        pos = pygame.mouse.get_pos()

        #check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                
                action = True
                self.clicked = True

            if pygame.mouse.get_pressed()[0] == 0:
                
                self.clicked = False

        #draw button
        screen.blit(self.image, self.rect)

        return action

class Player():
    def __init__(self, x, y):
        self.reset(x,y)

    def update(self, game_over):
        dx = 0
        dy = 0

        if game_over == 0:

            # Get key pressed
            key = pygame.key.get_pressed()

            if key[pygame.K_SPACE] and self.on_ground:  # Check if the player is on the ground
                jump_fx.play()
                self.vel_y = -14
                self.on_ground = False  # Player is no longer on the ground after jumping

            if key[pygame.K_a]:
                dx -= 4
            if key[pygame.K_d]:
                dx += 4

            # Add gravity
            self.vel_y += 1
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

            # Check for collision
            for tile in world.tile_list:
                # Check for collision in x direction
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0

                # Check for collision in y direction
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # Check if below the ground (i.e., jumping)
                    if self.vel_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.vel_y = 0
                        self.on_ground = False  # Player is on the ground after landing
                    # Check if above the ground (i.e., falling)
                    elif self.vel_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.vel_y = 0
                        self.on_ground = True

                # Check for collision with enemies
                if pygame.sprite.spritecollide(self, slime_group, False):
                    game_over = -1
                    gameover_fx.play()

                # Check for collision with spikes
                if pygame.sprite.spritecollide(self, spike_group, False):
                    game_over = -1
                    gameover_fx.play()
                    
                # Check for collision with portal
                if pygame.sprite.spritecollide(self, portal_group, False):
                    game_over = 1


            # Update player coordinates
            self.rect.x += dx
            self.rect.y += dy

        elif game_over == -1:
            self.image = self.dead_image
            draw_text('GAME OVER',font2,white,screen_width // 2 - 160 , screen_height // 2 - 100)
            if self.rect.y > 200:
                self.rect.y -= 5


        # Draw player
        screen.blit(self.image, self.rect)
        #pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
        return game_over

    def reset(self, x, y):
        img = pygame.image.load('ham.png')
        self.image = pygame.transform.scale(img, (40, 40))
        self.dead_image = pygame.image.load('dead.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.vel_y = 0
        self.on_ground = True  # New attribute to track whether the player is on the ground

class World():
    def __init__(self, data):
        self.tile_list = []

        #load image
        dirt_img = pygame.image.load('bigdirt1.png')
        dirtlong_img = pygame.image.load('longdirt.png')
        smalldirt_img = pygame.image.load('dirt1.png')
        bush_img = pygame.image.load('Blue.png')
        
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (4*tile_size,4*tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 2:
                    img = pygame.transform.scale(dirtlong_img, (4*tile_size,tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    img = pygame.transform.scale(smalldirt_img, (tile_size,tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 4:
                    img = pygame.transform.scale(bush_img, (tile_size,tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 5:
                    slime = Enemy(col_count * tile_size, row_count * tile_size+15)
                    slime_group.add(slime)
                if tile == 6:
                    spike = Spike(col_count * tile_size, row_count * tile_size)
                    spike_group.add(spike)
                if tile == 7:
                    strawberry = Strawberry(col_count * tile_size + (tile_size//2), row_count * tile_size + (tile_size//2))
                    strawberry_group.add(strawberry)
                if tile == 8:
                    portal = Portal(col_count * tile_size, row_count * tile_size - 20)
                    portal_group.add(portal)
                col_count += 1
            row_count += 1
    
    def draw(self):
         for tile in self.tile_list:
              screen.blit(tile[0], tile[1])
              #pygame.draw.rect(screen, (255,255,255), tile[1], 2)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('slime.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter +=1
        if abs(self.move_counter) > 40:
            self.move_direction *= -1
            self.move_counter *= -1


class Spike(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('spike.png')
        self.image = pygame.transform.scale(img,(tile_size, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Strawberry(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('strawberry.png')
        self.image = pygame.transform.scale(img,(tile_size//2, tile_size//2))
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        
        
class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        img = pygame.image.load('portal.png')
        self.image = pygame.transform.scale(img,(tile_size, tile_size * 1.5))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y




player = Player(100,screen_height - 80)
slime_group = pygame.sprite.Group()
spike_group = pygame.sprite.Group()
portal_group = pygame.sprite.Group()
strawberry_group = pygame.sprite.Group()

#strawberry to show the score
score_strawberry = Strawberry(10,10)
strawberry_group.add(score_strawberry)

#load in level data and create world
if path.exists(f'level{level}_data.pkl'):
    pickle_in = open(f'level{level}_data.pkl','rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)

#create buttons
restart_button = Button(screen_width // 2 - 80 , screen_height // 2 , restart_img)
start_button = Button(screen_width // 2 - 150, screen_height // 2 - 100 , start_img)
exit_button = Button(screen_width // 2 - 130, screen_height // 2 + 150, exit_img)

run = True
while run:

    clock.tick(FPS)

    screen.blit(sky_img,(0,0))
    screen.blit(ham_img,(0,0))

    if main_menu == True:
        if exit_button.draw() == True:
            run = False
        if start_button.draw() == True:
            main_menu = False

    else:
        world.draw()

    
        if game_over == 0:
            slime_group.update()
            #update score
            #check if a strawberry has been collected
            if pygame.sprite.spritecollide(player, strawberry_group, True):
                strawberry_fx.play()
                score += 1
            draw_text('x'+str(score),font,white,20,4)



        slime_group.draw(screen)
        spike_group.draw(screen)
        strawberry_group.draw(screen)
        portal_group.draw(screen)

        game_over = player.update(game_over)
        
        #if player die
        if game_over == -1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                game_over = 0
                score = 0
                

        #if player completed the level
        if game_over == 1:
            level += 1
            if level <= max_level:
                world_data = []
                world = reset_level(level)
                game_over = 0
            else:
                draw_text('YOU WIN!!!', font2 ,white,screen_width // 2 - 160 , screen_height // 2 - 100)
                draw_text('Score: ' + str(score), font3, white, screen_width // 2 - 120, screen_height // 2 - 50 )
                if restart_button.draw():
                    level = 1
                    world_data = []
                    world = reset_level(level)
                    game_over = 0
                    score = 0


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        
    pygame.display.update()

pygame.quit()



