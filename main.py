import pygame
import time
import math
from utils import scale_image, blit_rotate_center

pygame.mixer.init()

GRASS = scale_image(pygame.image.load("imgs/mygrass.jpg"), 2.5)
TRACK = scale_image(pygame.image.load("imgs/mytrack.png"), 0.9)

TRACK_BORDER = scale_image(pygame.image.load("imgs/myborder.png"), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

FINISH = pygame.image.load("imgs/finish.png")
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (10, 235)

FIRST_CAR = scale_image(pygame.image.load("imgs/purple-car.png"), 0.35)
SECOND_CAR = scale_image(pygame.image.load("imgs/red_car_new.png"), 0.35)

RACE_SOUND = pygame.mixer.Sound("sound/car_sound.mp3")

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

FPS = 60


class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel
        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0


class PlayerCar(AbstractCar):
    IMG = FIRST_CAR
    START_POS = (60, 200)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.vel = -0.5*self.vel
        self.move()

class SecondPlayerCar(AbstractCar):
    IMG = SECOND_CAR
    START_POS = (30, 200)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.vel = -0.5*self.vel
        self.move()


def draw(win, images, player_car, second_player_car):
    for img, pos in images:
        win.blit(img, pos)

    player_car.draw(win)
    second_player_car.draw(win)
    pygame.display.update()


def move_player(player_car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_car.rotate(right=True)
    if keys[pygame.K_w]: 
        RACE_SOUND.play()
        moved = True
        player_car.move_forward()
    if keys[pygame.K_s]:
        moved = True
        player_car.move_backward()

    if not moved:
        player_car.reduce_speed()

def move_second_player(second_player_car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_LEFT]:
        second_player_car.rotate(left=True)
    if keys[pygame.K_RIGHT]:
        second_player_car.rotate(right=True)
    if keys[pygame.K_UP]:
        moved = True
        second_player_car.move_forward()
    if keys[pygame.K_DOWN]:
        moved = True
        second_player_car.move_backward()

    if not moved:
        second_player_car.reduce_speed()


run = True
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0, 0)),
          (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]
player_car = PlayerCar(8, 8)
second_player_car = SecondPlayerCar(8, 8)

while run:
    clock.tick(FPS)

    draw(WIN, images, player_car, second_player_car)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

    move_player(player_car)
    move_second_player(second_player_car)

    if player_car.collide(TRACK_BORDER_MASK) != None:
        player_car.bounce()
    elif second_player_car.collide(TRACK_BORDER_MASK) != None:
        second_player_car.bounce()

    finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION) or second_player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if finish_poi_collide != None:
        if finish_poi_collide[1] == 0:
            player_car.bounce()
        elif finish_poi_collide[1] == 0:
            second_player_car.bounce()
        else:
            player_car.reset()
            second_player_car.reset()
            print("finish")


pygame.quit()