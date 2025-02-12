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

WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")

MAIN_FONT = pygame.font.SysFont("comicsans", 44)

FPS = 60
PATH = [(175, 119),
        (110, 70), (56, 133), (70, 481), (318, 731), (404, 680), (418, 521), (507, 475), (600, 551),
        (613, 715),
        (736, 713), (734, 399), (611, 357), (409, 343), (433, 257), (697, 258), (738, 123), (581, 71), (303, 78),
        (275, 377),
        (176, 388), (178, 260)]


class Collectible:
    def __init__(self, x, y, is_boost):
        self.x = x
        self.y = y
        self.is_boost = is_boost
        self.collected = False
        self.radius = 15
        self.effect_duration = 3
        self.speed_multiplier = 1.5 if is_boost else 0.5

    def draw(self, win):
        if not self.collected:
            img_path = "imgs/booster-green.svg" if self.is_boost else "imgs/slower.png"
            image = pygame.image.load(img_path)
            win.blit(image, (self.x, self.y))

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

class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 100),action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.font = pygame.font.SysFont("comicsans", 30)
        self.action = action

    def draw(self, win):
        pygame.draw.rect(win, self.color, self.rect)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        win.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)
class GameInfo:
    LEVELS = 10

    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_start_time = 0
        self.collectibles = []
        # self.generate_collectibles()
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

        random_positions = random.sample(PATH, 6)

        self.collectibles = [
            Collectible(random_positions[0][0], random_positions[0][1], True),
            Collectible(random_positions[1][0], random_positions[1][1], False),
            Collectible(random_positions[2][0], random_positions[2][1], True),
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


    def game_finished(self):
        return self.level > self.LEVELS

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.level_start_time)


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
        self.power_up_end_time = 0
        self.speed_multiplier = 1.0

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

    def update_speed_effects(self, current_time):
        if current_time >= self.power_up_end_time:
            self.speed_multiplier = 1.0
            self.max_vel = self.base_max_vel

    def apply_speed_effect(self, multiplier, duration):
        self.speed_multiplier = multiplier
        self.max_vel = self.base_max_vel * multiplier
        self.power_up_end_time = time.time() + duration


class PlayerCar(AbstractCar):
    IMG = RED_CAR
    START_POS = (180, 200)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0
        self.speed_multiplier = 1.0
        self.max_vel = self.base_max_vel


class ComputerCar(AbstractCar):
    IMG = GREEN_CAR
    START_POS = (150, 200)

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel

    def draw_points(self, win):
        for point in self.path:
            pygame.draw.circle(win, (255, 0, 0), point, 5)

    def draw(self, win):
        super().draw(win)

    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            desired_radian_angle = math.pi / 2
        else:
            desired_radian_angle = math.atan(x_diff / y_diff)

        if target_y > self.y:
            desired_radian_angle += math.pi

        difference_in_angle = self.angle - math.degrees(desired_radian_angle)
        if difference_in_angle >= 180:
            difference_in_angle -= 360

        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))
        else:
            self.angle += min(self.rotation_vel, abs(difference_in_angle))

    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0
        self.speed_multiplier = 1.0
        self.max_vel = self.base_max_vel
        self.current_point = 0

    def move(self):
        if self.current_point >= len(self.path):
            return

        self.calculate_angle()
        self.update_path_point()
        super().move()

    def next_level(self, level):
        self.reset()
        self.vel = self.max_vel + (level - 1) * 0.4
        self.current_point = 0


def draw(win, images, player_car, computer_car, game_info):
    for img, pos in images:
        win.blit(img, pos)

    for collectible in game_info.collectibles:
        collectible.draw(win)

    level_text = MAIN_FONT.render(f"Level {game_info.level}", 1, (255, 255, 255))
    win.blit(level_text, (10, HEIGHT - level_text.get_height() - 70))

    time_text = MAIN_FONT.render(f"Time: {game_info.get_level_time()}s", 1, (255, 255, 255))
    win.blit(time_text, (10, HEIGHT - time_text.get_height() - 40))

    vel_text = MAIN_FONT.render(f"Vel: {round(player_car.vel, 1)}px/s", 1, (255, 255, 255))
    win.blit(vel_text, (10, HEIGHT - vel_text.get_height() - 10))

    multiplier_text = MAIN_FONT.render(f"Speed: x{round(player_car.speed_multiplier, 1)}", 1, (255, 255, 255))
    win.blit(multiplier_text, (10, HEIGHT - multiplier_text.get_height() - 100))

    player_car.draw(win)
    computer_car.draw(win)
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


def handle_collision(player_car, computer_car, game_info):
    if player_car.collide(TRACK_BORDER_MASK) != None:
        player_car.bounce()

    computer_finish_poi_collide = computer_car.collide(FINISH_MASK, *FINISH_POSITION)
    if computer_finish_poi_collide != None:
        return end_game_screen("You Lost!", WIN, MAIN_FONT, game_info, player_car, computer_car)  # Show end game screen and return action

    player_finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi_collide != None:
        if player_finish_poi_collide[1] == 0:
            player_car.bounce()
        else:
            game_info.next_level()
            player_car.reset()
            computer_car.next_level(game_info.level)
            return "continue"


def handle_collectibles(player_car, computer_car, game_info):
    current_time = time.time()
    player_car.update_speed_effects(current_time)
    computer_car.update_speed_effects(current_time)

    for collectible in game_info.collectibles:
        if collectible.collect(player_car):
            player_car.apply_speed_effect(collectible.speed_multiplier, collectible.effect_duration)
        if collectible.collect(computer_car):
            computer_car.apply_speed_effect(collectible.speed_multiplier, collectible.effect_duration)


def end_game_screen(message, win, font, game_info, player_car, computer_car):
    win.fill((0, 0, 0))

    text = font.render(message, True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    win.blit(text, text_rect)

    button_width, button_height = 200, 50
    button_x = WIDTH // 2 - button_width // 2

    restart_button = Button(button_x, HEIGHT // 2 - 60, button_width, button_height, "Restart")
    game_menu_button = Button(button_x, HEIGHT // 2, button_width, button_height, "Game Menu")
    quit_button = Button(button_x, HEIGHT // 2 + 60, button_width, button_height, "Quit")

    restart_button.draw(win)
    game_menu_button.draw(win)
    quit_button.draw(win)

    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if restart_button.is_clicked(mouse_pos):
                    game_info.reset()
                    player_car.reset()
                    computer_car.reset()
                    return "restart"

                elif quit_button.is_clicked(mouse_pos):

                    pygame.quit()
                    return "quit"
                elif game_menu_button.is_clicked(mouse_pos):
                    game_selection_menu.main()


def run():
    pygame.init()
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Racing Game - VS Computer")

    clock = pygame.time.Clock()
    images = [(GRASS, (0, 0)), (TRACK, (0, 0)), (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]
    player_car = PlayerCar(4, 4)
    computer_car = ComputerCar(2, 4, PATH)
    game_info = GameInfo()

    run = True
    while run:
        clock.tick(FPS)

        draw(WIN, images, player_car, computer_car, game_info)

        while not game_info.started:
            blit_text_center(WIN, MAIN_FONT, f"Press any key to start level {game_info.level}!")
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

        move_player(player_car)
        computer_car.move()

        handle_collectibles(player_car, computer_car, game_info)
        result = handle_collision(player_car, computer_car, game_info)
        if result == "quit":
            run = False
        elif result == "restart":
            run = True
            player_car = PlayerCar(4, 4)
            computer_car = ComputerCar(2, 4, PATH)
            game_info = GameInfo()

        if game_info.game_finished():
            end_game_screen("You Won!", WIN, MAIN_FONT, game_info, player_car, computer_car)
            run = False

    pygame.quit()


if __name__ == "__main__":
    run()