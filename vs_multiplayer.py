import pygame
import time
import math
import random
from utils import scale_image, blit_rotate_center, blit_text_center
import game_selection_menu

pygame.font.init()

GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)
TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.9)

TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"), 0.9)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)

FINISH = pygame.image.load("imgs/finish.png")
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (130, 250)

RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.55)
GREEN_CAR = scale_image(pygame.image.load("imgs/green-car.png"), 0.55)
WHITE_CAR = scale_image(pygame.image.load("imgs/white-car.png"), 0.55)

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

MAIN_FONT = pygame.font.SysFont("comicsans", 44)

FPS = 60
PATH = [(175, 119), (110, 70),
        (56, 133), (70, 481), (318, 731), (404, 680), (418, 521), (507, 475), (600, 551), (613, 715), (736, 713),
        (734, 399), (611, 357), (409, 343), (433, 257), (697, 258), (738, 123), (581, 71), (303, 78), (275, 377),
        (176, 388), (178, 260)
        ]


class GameInfo:
    LEVELS = 10

    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0

        random_positions = random.sample(PATH, 6)

        self.collectibles = [
            Collectible(random_positions[0][0], random_positions[0][1], True),  # Boost
            Collectible(random_positions[1][0], random_positions[1][1], False),  # Slower
            Collectible(random_positions[2][0], random_positions[2][1], True),  # Boost
            Collectible(random_positions[3][0], random_positions[3][1], False),  # Slower
            Collectible(random_positions[4][0], random_positions[4][1], True),  # Boost
            Collectible(random_positions[5][0], random_positions[5][1], False)  # Slower
        ]

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0

        random_positions = random.sample(PATH, 6)
        self.collectibles = [
            Collectible(random_positions[0][0], random_positions[0][1], True),  # Boost
            Collectible(random_positions[1][0], random_positions[1][1], False),  # Slower
            Collectible(random_positions[2][0], random_positions[2][1], True),  # Boost
            Collectible(random_positions[3][0], random_positions[3][1], False),  # Slower
            Collectible(random_positions[4][0], random_positions[4][1], True),  # Boost
            Collectible(random_positions[5][0], random_positions[5][1], False)  # Slower
        ]

    def next_level(self):
        self.level += 1
        self.started = False

    def game_finished(self):
        return self.level > self.LEVELS

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.level_start_time)


class Collectible:
    def __init__(self, x, y, is_boost):
        self.x = x
        self.y = y
        self.is_boost = is_boost
        self.collected = False
        self.radius = 15
        self.effect_duration = 3
        self.speed_multiplier = 2.0 if is_boost else 0.5

    def collect(self, car):
        if not self.collected:
            car_rect = pygame.Rect(car.x - car.img.get_width() / 2,
                                   car.y - car.img.get_height() / 2,
                                   car.img.get_width(),
                                   car.img.get_height())
            collectible_rect = pygame.Rect(self.x - self.radius,
                                           self.y - self.radius,
                                           self.radius * 2,
                                           self.radius * 2)
            if car_rect.colliderect(collectible_rect):
                self.collected = True
                return True
        return False

    def draw(self, win):
        if not self.collected:
            img_path = "imgs/booster-green.svg" if self.is_boost else "imgs/slower.png"
            image = pygame.image.load(img_path)
            win.blit(image, (self.x, self.y))


class AbstractCar:
    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.base_max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1
        self.base_max_vel = max_vel
        self.rect = self.img.get_rect(center=(self.x, self.y))
        self.previous_pos = (self.x, self.y)

        self.speed_multiplier = 1.0
        self.effect_end_time = 0

    def apply_speed_effect(self, multiplier, duration):
        self.speed_multiplier = multiplier
        self.max_vel = self.base_max_vel * multiplier
        self.effect_end_time = time.time() + duration

    def update_speed_effects(self, current_time):
        if current_time > self.effect_end_time:
            self.speed_multiplier = 1.0
            self.max_vel = self.base_max_vel

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
        self.vel = max(self.vel - self.acceleration, -self.max_vel / 2)
        self.move()

    def move(self):
        self.previous_pos = (self.x, self.y)
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.vel = min(self.vel, self.max_vel)

        self.y -= vertical
        self.x -= horizontal

        self.rect.center = (self.x, self.y)

    def restore_position(self):
        self.x, self.y = self.previous_pos
        self.rect.center = (self.x, self.y)

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0
        self.max_vel = self.base_max_vel
        self.speed_multiplier = 1.0


class PlayerCar1(AbstractCar):
    IMG = RED_CAR
    START_POS = (180, 200)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()


class PlayerCar2(AbstractCar):
    IMG = WHITE_CAR
    START_POS = (150, 200)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()


class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 100)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.SysFont("comicsans", 30)

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.rect)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        win.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


def draw(win, images, player1, player2, game_info):
    for img, pos in images:
        win.blit(img, pos)

    for collectible in game_info.collectibles:
        collectible.draw(win)

    time_text = MAIN_FONT.render(
        f"Time: {game_info.get_level_time()}s", 1, (255, 255, 255))
    win.blit(time_text, (10, HEIGHT - time_text.get_height() - 110))

    vel_text = MAIN_FONT.render(
        f"Player1: {round(player1.vel, 1)}px/s", 1, (255, 255, 255))
    win.blit(vel_text, (10, HEIGHT - vel_text.get_height() - 60))
    vel_text = MAIN_FONT.render(
        f"Player2: {round(player2.vel, 1)}px/s", 1, (255, 255, 255))
    win.blit(vel_text, (10, HEIGHT - vel_text.get_height() - 10))

    player1.draw(win)
    player2.draw(win)
    pygame.display.update()


def move_player(player1, player2):
    keys = pygame.key.get_pressed()
    moved_player1 = False
    moved_player2 = False

    # Player 1 Movement
    if keys[pygame.K_a]:
        player1.rotate(left=True)
    if keys[pygame.K_d]:
        player1.rotate(right=True)
    if keys[pygame.K_w]:
        moved_player1 = True
        player1.move_forward()
    if keys[pygame.K_s]:
        moved_player1 = True
        player1.move_backward()

    # Player 2 Movement
    if keys[pygame.K_LEFT]:
        player2.rotate(left=True)
    if keys[pygame.K_RIGHT]:
        player2.rotate(right=True)
    if keys[pygame.K_UP]:
        moved_player2 = True
        player2.move_forward()
    if keys[pygame.K_DOWN]:
        moved_player2 = True
        player2.move_backward()

    if not moved_player1:
        player1.reduce_speed()
    if not moved_player2:
        player2.reduce_speed()



def handle_collectibles(player1, player2, game_info):
    current_time = time.time()
    player1.update_speed_effects(current_time)
    player2.update_speed_effects(current_time)

    for collectible in game_info.collectibles:
        if collectible.collect(player1):
            player1.apply_speed_effect(collectible.speed_multiplier, collectible.effect_duration)
        if collectible.collect(player2):
            player2.apply_speed_effect(collectible.speed_multiplier, collectible.effect_duration)


def handle_collision(player1, player2, game_info):
    if player1.collide(TRACK_BORDER_MASK) is not None:
        player1.bounce()
    if player2.collide(TRACK_BORDER_MASK) is not None:
        player2.bounce()

    player1_finish_poi_collide = player1.collide(FINISH_MASK, *FINISH_POSITION)
    if player1_finish_poi_collide is not None:
        if player1_finish_poi_collide[1] == 0:
            player1.bounce()
        else:
            return show_end_game_screen(WIN, "Player 1", game_info, player1, player2)

    player2_finish_poi_collide = player2.collide(FINISH_MASK, *FINISH_POSITION)
    if player2_finish_poi_collide is not None:
        if player2_finish_poi_collide[1] == 0:
            player2.bounce()
        else:
            return show_end_game_screen(WIN, "Player 2", game_info, player1, player2)
    return "continue"



def show_end_game_screen(win, winner, game_info, player1=None, player2=None, player_car=None, computer_car=None):
    win.fill((0, 0, 0))

    button_width, button_height = 200, 50
    button_x = WIDTH // 2 - button_width // 2

    restart_button = Button(button_x, HEIGHT // 2 - 60, button_width, button_height, "Restart")
    game_selection_button = Button(button_x, HEIGHT // 2, button_width, button_height, "Game Menu")
    quit_button = Button(button_x, HEIGHT // 2 + 60, button_width, button_height, "Quit")

    winner_text = MAIN_FONT.render(f"{winner} Won!", 1, (255, 255, 255))
    win.blit(winner_text, (WIDTH // 2 - winner_text.get_width() // 2, HEIGHT // 2 - 200))

    restart_button.draw(win)
    game_selection_button.draw(win)
    quit_button.draw(win)

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if restart_button.is_clicked(mouse_pos):
                        game_info.reset()
                        if player1 and player2:
                            player1.reset()
                            player2.reset()
                        elif player_car and computer_car:
                            player_car.reset()
                            computer_car.reset()
                        return "restart"

                elif quit_button.is_clicked(mouse_pos):
                    pygame.quit()
                    return "quit"
                elif game_selection_button.is_clicked(mouse_pos):
                    game_selection_menu.main()



def run():
    run = True
    clock = pygame.time.Clock()
    images = [(GRASS, (0, 0)), (TRACK, (0, 0)),
              (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]

    game_info = GameInfo()

    player1 = PlayerCar1(4, 4)
    player2 = PlayerCar2(4, 4)

    while run:
        clock.tick(FPS)
        draw(WIN, images, player1, player2, game_info)

        while not game_info.started:
            blit_text_center(
                WIN, MAIN_FONT, f"Press any key to start the race!")
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    game_info.start_level()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        move_player(player1, player2)

        handle_collectibles(player1, player2, game_info)

        result = handle_collision(player1, player2, game_info)
        if result == "quit":
            run = False
        elif result == "restart":
            game_info = GameInfo()
            player1 = PlayerCar1(4, 4)
            player2 = PlayerCar2(4, 4)
        elif result == "game_selection":
            return "game_selection"


        if game_info.game_finished():
             result = show_end_game_screen(WIN, "No One", game_info, player1, player2)
             if result == "quit":
                 run = False
             elif result == "restart":
                 game_info = GameInfo()
                 player1 = PlayerCar1(4, 4)
                 player2 = PlayerCar2(4, 4)
             elif result == "game_selection":
                 return "game_selection"


    pygame.quit()


if __name__ == "__main__":
    run()