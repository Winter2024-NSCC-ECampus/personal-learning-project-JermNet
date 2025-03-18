import pygame, sys
from game import Game
from colours import Colours

# Initialize Pygame
pygame.init()

# Set up the display, this is all for text stuff
title_font = pygame.font.Font(None, 40)
score_surface = title_font.render("Score", True, Colours.white)
score_rect = pygame.Rect(320, 55, 170, 60)
next_surface = title_font.render("Next", True, Colours.white)
next_rect = pygame.Rect(320, 215, 170, 180)
game_over_surface = title_font.render("Game Over", True, Colours.white)

# Set up the window
screen = pygame.display.set_mode((500, 620))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()
game = Game()

# Set up the timer for the game update
GAME_UPDATE = pygame.USEREVENT
pygame.time.set_timer(GAME_UPDATE, 200)

# Main game loop
while True:
    # Check for inputs
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if game.game_over == True:
                game.game_over = False
                game.reset()
            if event.key == pygame.K_LEFT and game.game_over == False:
                game.move_left()
            if event.key == pygame.K_RIGHT and game.game_over == False:
                game.move_right()
            if event.key == pygame.K_DOWN and game.game_over == False:
                game.move_down()
                game.update_score(0, 1)
            if event.key == pygame.K_UP and game.game_over == False:
                game.rotate()
        if event.type == GAME_UPDATE and game.game_over == False:
            game.move_down()

    # Draw the game
    score_value_surface = title_font.render(str(game.score), True, Colours.white)
    screen.fill(Colours.dark_blue)
    screen.blit(score_surface, (365, 20, 50, 50))
    screen.blit(next_surface, (375, 180, 50, 50))
    if game.game_over == True:
        screen.blit(game_over_surface, (320, 450, 50, 50))
    pygame.draw.rect(screen, Colours.light_blue, score_rect, 0, 10)
    pygame.draw.rect(screen, Colours.light_blue, next_rect, 0, 10)
    screen.blit(score_value_surface, score_value_surface.get_rect(centerx = score_rect.centerx, centery = score_rect.centery))
    game.draw(screen)
    pygame.display.update()
    clock.tick(60)