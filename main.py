import pygame
import time
import math
import os
import neat
from utils import scale_image, blit_rotate_center

GRASS = scale_image(pygame.image.load("imgs/grass.png"), 2.5)
TRACK = scale_image(pygame.image.load("imgs/track3.png"), 0.9)

FIRST_CAR = scale_image(pygame.image.load("imgs/purple-car.png"), 0.35)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

FPS = 60

class AbstractCar(pygame.sprite.Sprite):
    def __init__(self, max_vel, rotation_vel, start_pos):
        super().__init__()
        self.img = self.IMG
        self.rect = self.img.get_rect(center=start_pos)
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = start_pos
        self.acceleration = 0.1
        self.radars = []
        self.alive = True
        

    def update(self):
        self.rotate()
        self.collision()
        self.radars.clear()
        self.data()
        for radar_angle in (-60, -30, 0, 30, 60):
            self.radar(radar_angle)

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
        self.rect.center = (self.x + 7 ,self.y+15)

    def radar(self, radar_angle):
        length = 0
        x = int(self.rect.center[0])
        y = int(self.rect.center[1])

        while not WIN.get_at((x, y)) == pygame.Color(3, 105, 32, 255) and length < 150:
            length += 1
            x = int(self.rect.center[0] + math.cos(math.radians(self.angle + radar_angle + 90)) * length)
            y = int(self.rect.center[1] - math.sin(math.radians(self.angle + radar_angle + 90)) * length)

        pygame.draw.line(WIN, (255, 255, 255, 255), self.rect.center, (x, y), 1)
        pygame.draw.circle(WIN, (0, 255, 0, 0), (x, y), 3)

        dist = int(math.sqrt(math.pow(self.rect.center[0] - x, 2) + math.pow(self.rect.center[1] - y, 2)))
        self.radars.append([radar_angle, dist])

    def data(self):
        input = [0, 0, 0, 0, 0]
        for i, radar in enumerate(self.radars):
            input[i] = int(radar[1])
        return input
    
    def collision(self):
            length = 15
            collision_point_right = [int(self.rect.center[0] + math.cos(math.radians(self.angle + 75)) * length),
                                     int(self.rect.center[1] - math.sin(math.radians(self.angle + 75)) * length)]
            collision_point_left = [int(self.rect.center[0] + math.cos(math.radians(self.angle + 105)) * length),
                                    int(self.rect.center[1] - math.sin(math.radians(self.angle + 105)) * length)]

        # Die on Collision
            if WIN.get_at(collision_point_right) == pygame.Color(3, 105, 32, 255) \
                    or WIN.get_at(collision_point_left) == pygame.Color(3, 105, 32, 255):
                self.alive = False

        # Draw Collision Points
            pygame.draw.circle(WIN, (0, 255, 255, 0), collision_point_right, 3)
            pygame.draw.circle(WIN, (0, 255, 255, 0), collision_point_left, 3)


class PlayerCar(AbstractCar):
    IMG = FIRST_CAR
    START_POS = (170, 220)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()


def draw(win, images, player_car):
    for img, pos in images:
        win.blit(img, pos)

    player_car.draw(win)
    player_car.update()
    pygame.display.update()


def move_player(player_car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_car.rotate(right=True)
    if keys[pygame.K_w]: 
        moved = True
        player_car.move_forward()
    if keys[pygame.K_s]:
        moved = True
        player_car.move_backward()

    if not moved:
        player_car.reduce_speed()

# def remove(index):
#     cars.pop(index)
#     ge.pop(index)
#     nets.pop(index)

# def eval_genomes(genomes, config):
    # global cars, ge, nets

    # cars = []
    # ge = []
    # nets = []

    # for genome_id, genome in genomes:
    #     cars.append(pygame.sprite.GroupSingle(PlayerCar()))
    #     ge.append(genome)
    #     net = neat.nn.FeedForwardNetwork.create(genome, config)
    #     nets.append(net)
    #     genome.fitness = 0

run = True
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0, 0))]
player_car = PlayerCar(5, 5, PlayerCar.START_POS)

while run:
    clock.tick(FPS)

    draw(WIN, images, player_car)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break

    move_player(player_car)
    
pygame.quit()
#         if len(cars) == 0:
#             break

#         for i, car in enumerate(cars):
#             ge[i].fitness += 1
#             if not car.sprite.alive:
#                 remove(i)

#         for i, car in enumerate(cars):
#             output = nets[i].activate(car.sprite.data())
#             if output[0] > 0.7:
#                 car.sprite.direction = 1
#             if output[1] > 0.7:
#                 car.sprite.direction = -1
#             if output[0] <= 0.7 and output[1] <= 0.7:
#                 car.sprite.direction = 0

#     # Update
#         for car in cars:
#             car.draw(WIN)
#             car.update()
#         pygame.display.update()

        

# def run(config_path):
#     global pop
#     config = neat.config.Config(
#         neat.DefaultGenome,
#         neat.DefaultReproduction,
#         neat.DefaultSpeciesSet,
#         neat.DefaultStagnation,
#         config_path
#     )

#     pop = neat.Population(config)

#     pop.add_reporter(neat.StdOutReporter(True))
#     stats = neat.StatisticsReporter()
#     pop.add_reporter(stats)

#     pop.run(eval_genomes, 50)


# if __name__ == '__main__':
#     local_dir = os.path.dirname(__file__)
#     config_path = os.path.join(local_dir, 'config.txt')
#     run(config_path)




