import pygame
import sys

WIDTH = 800
HEIGHT = 600


def init_pygame():
    pygame.init()
    pygame.font.init()
    return pygame.display.set_mode((WIDTH, HEIGHT))


def create_main_font():
    return pygame.font.SysFont("comicsans", 44)


def draw_menu(win, font):
    win.fill((0, 0, 0))

    title = font.render("Racing Game", 1, (255, 255, 255))
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    win.blit(title, title_rect)

    vs_computer_text = font.render("Press 1: VS Computer", 1, (255, 255, 255))
    vs_player_text = font.render("Press 2: VS Player", 1, (255, 255, 255))
    quit_text = font.render("Press Q: Quit", 1, (255, 255, 255))

    vs_computer_rect = vs_computer_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    vs_player_rect = vs_player_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
    quit_rect = quit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))

    win.blit(vs_computer_text, vs_computer_rect)
    win.blit(vs_player_text, vs_player_rect)
    win.blit(quit_text, quit_rect)

    pygame.display.update()


def main():
    win = init_pygame()
    pygame.display.set_caption("Racing Game!")
    font = create_main_font()
    clock = pygame.time.Clock()

    running = True
    while running:
        clock.tick(60)
        draw_menu(win, font)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    import vs_computer
                    result = vs_computer.run()
                    if result == "quit":
                         running = False
                    pygame.display.set_mode((WIDTH, HEIGHT))
                elif event.key == pygame.K_2:
                    import vs_multiplayer
                    result = vs_multiplayer.run()
                    if result == "quit":
                         running = False
                    pygame.display.set_mode((WIDTH, HEIGHT))
                elif event.key == pygame.K_q:
                    running = False

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()