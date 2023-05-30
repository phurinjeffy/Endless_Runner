import abc
import pygame as pg
import random
from os import path

pg.init()
pg.display.set_caption('Endless Runner')

SCREEN_WIDTH = 1100
SCREEN_HEIGHT = 600
SCREEN = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

RUNNING = [pg.image.load("images/Runner/PlayerRun1.png"),
           pg.image.load("images/Runner/PlayerRun2.png")]
JUMPING = pg.image.load("images/Runner/PlayerJump.png")
DUCKING = [pg.image.load("images/Runner/PlayerDuck1.png"),
           pg.image.load("images/Runner/PlayerDuck2.png")]

SMALL_OBSTACLE = [pg.image.load("images/Obstacles/SmallBuildings1.png"),
                pg.image.load("images/Obstacles/SmallBuildings2.png"),
                pg.image.load("images/Obstacles/SmallBuildings3.png")]
LARGE_OBSTACLE = [pg.image.load("images/Obstacles/LargeBuildings1.png"),
                pg.image.load("images/Obstacles/LargeBuildings2.png"),
                pg.image.load("images/Obstacles/LargeBuildings3.png")]

PLANE = [pg.image.load("images/Obstacles/Plane1.png"), 
        pg.image.load("images/Obstacles/Plane2.png")]

BG = pg.image.load(("images/Other/Track.png"))
JUMP_SOUND = pg.mixer.Sound('images/Other/jump.wav')
DIE_SOUND = pg.mixer.Sound('images/Other/die.wav')
POINT_SOUND = pg.mixer.Sound('images/Other/point.wav')


class Runner:
    def __init__(self):
        self.X_POS = 80
        self.Y_POS = 310
        self.Y_POS_DUCK = 340
        self.JUMP_VEL = 8.5
        
        self.run_img = RUNNING
        self.jump_img = JUMPING
        self.duck_img = DUCKING

        self.player_run = True
        self.player_jump = False
        self.player_duck = False  

        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.player_rect = self.image.get_rect()
        self.player_rect.x = self.X_POS
        self.player_rect.y = self.Y_POS

    def update(self, userInput):
        if self.player_duck:
            self.duck()
        if self.player_run:
            self.run()
        if self.player_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        if (userInput[pg.K_UP] or userInput[pg.K_SPACE] or userInput[pg.K_w]) and not self.player_jump:
            self.player_duck = False
            self.player_run = False
            self.player_jump = True
            JUMP_SOUND.play()
        elif (userInput[pg.K_DOWN] or userInput[pg.K_s]) and not self.player_jump:
            self.player_duck = True
            self.player_run = False
            self.player_jump = False
        elif not (self.player_jump or (userInput[pg.K_DOWN] or userInput[pg.K_s])):
            self.player_duck = False
            self.player_run = True
            self.player_jump = False

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.player_rect = self.image.get_rect()
        self.player_rect.x = self.X_POS
        self.player_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.player_rect = self.image.get_rect()
        self.player_rect.x = self.X_POS
        self.player_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.player_jump:
            self.player_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < -self.JUMP_VEL:
            self.player_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.player_rect.x, self.player_rect.y))

class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = pg.image.load("images/Other/Cloud.png")
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))

class Obstacle(abc.ABC):
    @abc.abstractmethod
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)

class SmallBuilding(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325

class LargeBuilding(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300

class Plane(Obstacle):
    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = 250
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 10:
            self.index = 0
        SCREEN.blit(self.image[self.index // 5], self.rect)
        self.index += 1  


def main():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles
    run = True
    clock = pg.time.Clock()
    player = Runner()
    cloud = Cloud()
    game_speed = 20
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    font = pg.font.Font('freesansbold.ttf', 20)
    obstacles = []
    death_count = 0

    def score():
        global points, game_speed, highscore
        points += 1
        if points % 100 == 0:
            game_speed += 1
        if points % 1000 == 0:
            POINT_SOUND.play()

        hs = font.render(f"Highscore: {highscore}", True, (105, 105, 105))
        hsRect = hs.get_rect()
        hsRect.center = (1000, 40)
        SCREEN.blit(hs, hsRect)
        text = font.render(f"Points: {points}", True, (105, 105, 105))
        textRect = text.get_rect()
        textRect.center = (1000, 80)
        SCREEN.blit(text, textRect)

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed

    while run:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                exit()

        SCREEN.fill((255, 255, 255))
        userInput = pg.key.get_pressed()

        player.draw(SCREEN)
        player.update(userInput)

        if len(obstacles) == 0:
            if random.randint(0, 2) == 0:
                obstacles.append(SmallBuilding(SMALL_OBSTACLE))
            elif random.randint(0, 2) == 1:
                obstacles.append(LargeBuilding(LARGE_OBSTACLE))
            elif random.randint(0, 2) == 2:
                obstacles.append(Plane(PLANE))

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            if player.player_rect.colliderect(obstacle.rect):
                DIE_SOUND.play()
                pg.time.delay(200)
                death_count = 1
                menu(death_count)

        background()

        cloud.draw(SCREEN)
        cloud.update()

        score()
        
        clock.tick(30)
        pg.display.update()
            
def menu(death_count=0):
    global points, highscore
    run = True

    dir = path.dirname(__file__)
    with open(path.join(dir, 'highscore.txt'), 'r') as f:
        try:
            highscore = int(f.read())
        except:
            highscore = 0

    while run:
        SCREEN.fill((255, 255, 255))
        font = pg.font.Font('freesansbold.ttf', 30)

        if death_count == 0:
            text = font.render("Press any key to Start", True, (105, 105, 105))
            welcome = font.render("Welcome to Endless Runner", True, (105, 105, 105))
            welcomeRect = welcome.get_rect()
            welcomeRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 190)
            SCREEN.blit(welcome, welcomeRect)

        elif death_count > 0:
            SCREEN.blit(pg.image.load("images/Other/GameOver.png"), (SCREEN_WIDTH / 2 - 180, SCREEN_HEIGHT / 2 - 200))
            text = font.render("Continue?", True, (105, 105, 105))
            score = font.render(f"Your Score: {points}", True, (105, 105, 105))
            scoreRect = score.get_rect()
            scoreRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)
            SCREEN.blit(score, scoreRect)
            if int(points) > int(highscore):
                hs = font.render("NEW HIGH SCORE!", True, (105, 105, 105))
                hsRect = hs.get_rect()
                hsRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
                SCREEN.blit(hs, hsRect)
                with open(path.join(dir, 'highscore.txt'), 'w') as f:
                    f.write(str(points))
            else:
                hs = font.render(f"High Score: {highscore}", True, (105, 105, 105))
                hsRect = hs.get_rect()
                hsRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)
                SCREEN.blit(hs, hsRect)

        textRect = text.get_rect()
        textRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        SCREEN.blit(text, textRect)
        SCREEN.blit(pg.image.load("images/Runner/PlayerStart.png"), (SCREEN_WIDTH / 2 - 45, SCREEN_HEIGHT / 2 - 140))
        pg.display.update()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
                exit()
            if event.type == pg.KEYDOWN:
                main()

menu()
