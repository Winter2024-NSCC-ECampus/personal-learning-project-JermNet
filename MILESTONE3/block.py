import pygame
from colours import Colours
from position import Position

class Block:
    """A base class to be inherited by all the block classes."""
    def __init__(self, id):
        """Initializes the block with an id, cells (the squares that make up the block), cell_zize, row_offset, column_offset, rotation_state, and colours."""
        self.id = id
        self.cells = {}
        self.cell_size = 30
        self.row_offset = 0
        self.column_offset = 0
        self.rotation_state = 0
        self.colours = Colours.get_cell_colors()

    def move(self, rows, columns):
        """Moves the block by the specified number of rows and columns by adding to the offsets."""
        self.row_offset += rows
        self.column_offset += columns

    def rotate(self):
       """Rotates the block by increasing the rotation state, and if it reaches the end of the cells list, it resets it. Having the if statement be based on the length of the cells is very important since all but the OBlock have 4 rotations."""
       self.rotation_state += 1
       if self.rotation_state == len(self.cells):
           self.rotation_state = 0

    def undo_rotation(self):
        """Undoes the rotation, basically the reverse of the rotate method."""
        self.rotation_state -= 1
        if self.rotation_state == len(self.cells):
            self.rotation_state  

    def get_cell_positions(self):
        """Get the positions of the cells in the block by adding the offsets to the positions of the cells in the cells list."""
        tiles = self.cells[self.rotation_state]
        moved_tiles = []
        for position in tiles:
            position = Position(position.row + self.row_offset, position.column + self.column_offset)
            moved_tiles.append(position)
        return moved_tiles

    def draw(self, screen, offset_x, offset_y):
        """Draws the block by getting the positions of the cells and drawing them on the screen."""
        tiles = self.get_cell_positions()
        for tile in tiles:
            tile_rect = pygame.Rect(offset_x + tile.column * self.cell_size, offset_y + tile.row * self.cell_size, self.cell_size-1, self.cell_size-1)
            pygame.draw.rect(screen, self.colours[self.id], tile_rect)