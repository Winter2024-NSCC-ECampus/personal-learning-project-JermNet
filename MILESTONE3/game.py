from grid import Grid
from blocks import *
import random
import pygame

class Game:
    """A class for the main aspects of the game."""
    def __init__(self):
        """Initializes the game with a grid, blocks, current block, next block, game over, and score."""
        self.grid = Grid()
        self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
        self.current_block = self.get_random_block()
        self.next_block = self.get_random_block()
        self.game_over = False
        self.score = 0
        self.rotate_sound = pygame.mixer.Sound("sounds/rotate.ogg")
        self.clear_sound = pygame.mixer.Sound("sounds/clear.ogg")

        pygame.mixer.music.load("sounds/music.ogg")
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

    def update_score(self, lines, move_down_points):
        """Update the score based on the number of lines cleared."""
        if lines == 1:
            self.score += 100
        elif lines == 2:
            self.score += 300
        elif lines == 3:
            self.score += 500
        elif lines == 4:
            self.score += 1000
        self.score += move_down_points

    def get_random_block(self):
        """Get a random block from the blocks list."""
        if len(self.blocks) == 0:
            self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
        block = random.choice(self.blocks)
        self.blocks.remove(block)
        return block

    def draw(self, screen):
        """Draw the grid and current block to the screen."""
        self.grid.draw(screen)
        self.current_block.draw(screen, 11, 11)

        if self.next_block.id == 3:
            self.next_block.draw(screen, 255, 290)
        elif self.next_block.id == 4:
            self.next_block.draw(screen, 255, 290)
        else:
            self.next_block.draw(screen, 270, 270)

    def move_left(self):
        """Move the current block left, 'rolling back' the move if the block is outside the grid or collides with another block."""
        self.current_block.move(0, -1)
        if self.block_inside() == False or self.block_fits() == False:
            self.current_block.move(0, 1)

    def move_right(self):
        """Move the current block right, 'rolling back' the move if the block is outside the grid or collides with another block."""
        self.current_block.move(0, 1)
        if self.block_inside() == False or self.block_fits() == False:
            self.current_block.move(0, -1)

    def move_down(self):
        """Move the current block down, 'rolling back' the move if the block is outside the grid or collides with another block."""
        self.current_block.move(1, 0)
        if self.block_inside() == False or self.block_fits() == False:
            self.current_block.move(-1, 0)
            self.lock_block()

    def block_fits(self):
        """Check if the current block fits in the grid."""
        tiles = self.current_block.get_cell_positions()
        for tile in tiles:
            if self.grid.is_empty(tile.row, tile.column) == False:
                return False
        return True

    def lock_block(self):
        """Lock the current block in place, add it to the grid, and check for full rows."""
        tiles = self.current_block.get_cell_positions()
        for position in tiles:
            self.grid.grid[position.row][position.column] = self.current_block.id
        self.current_block = self.next_block
        self.next_block = self.get_random_block()
        rows_cleared = self.grid.clear_full_rows()
        if rows_cleared > 0:
            self.clear_sound.play()
            self.update_score(rows_cleared, 0)
        if self.block_fits() == False:
            self.game_over = True

    def block_inside(self):
        """Check if the current block is inside the grid."""
        tiles = self.current_block.get_cell_positions()
        for tile in tiles:
            if self.grid.is_inside(tile.row, tile.column) == False:
                return False
        return True

    def rotate(self):
        """Rotate the current block, 'rolling back' the rotation if the block is outside the grid or collides with another block."""
        self.current_block.rotate()
        if self.block_inside() == False or self.block_fits() == False:
            self.current_block.undo_rotation()
        else:
            self.rotate_sound.play()

    def reset(self):
        """Reset the game by resetting the grid, blocks, current block, next block, game over, and score."""
        self.grid.reset()
        self.blocks = [IBlock(), JBlock(), LBlock(), OBlock(), SBlock(), TBlock(), ZBlock()]
        self.current_block = self.get_random_block()
        self.next_block = self.get_random_block()
        self.score = 0