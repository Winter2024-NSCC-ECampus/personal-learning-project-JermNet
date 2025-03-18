import pygame
from colours import Colours

class Grid:
    """A class to represent the grid on which the blocks go."""
    def __init__(self):
        """Initializes the grid with a number of rows, columns, cell size, grid, and colours."""
        self.num_rows = 20
        self.num_cols = 10
        self.cell_size = 30
        self.grid = [[0 for j in range(self.num_cols)] for i in range(self.num_rows)]
        self.colors = Colours.get_cell_colors()

    def print_grid(self):
        """Prints the grid to the console, just used for testing."""
        for row in range(self.num_rows):
            for column in range(self.num_cols):
                print(self.grid[row][column], end = " ")
            print()
    
    def draw(self, screen):
        """Draws the grid to the screen."""
        for row in range(self.num_rows):
            for column in range(self.num_cols):
                cell_value = self.grid[row][column]
                cell_rect = pygame.Rect(column*self.cell_size+11, row*self.cell_size+11, self.cell_size-1, self.cell_size-1)
                pygame.draw.rect(screen, self.colors[cell_value], cell_rect)

    def is_inside(self, row, column):
        """Check if a cell is inside the grid."""
        if row >= 0 and row < self.num_rows and column >= 0 and column < self.num_cols:
            return True
        return False
    
    def is_empty(self, row, column):
        """Check if a cell is empty."""
        if self.grid[row][column] == 0:
            return True
        return False
    
    def is_row_full(self, row):
        """Check if a row is full."""
        for column in range(self.num_cols):
            if self.grid[row][column] == 0:
                return False
        return True
    
    def clear_row(self, row):
        """Clear a row."""
        for column in range(self.num_cols):
            self.grid[row][column] = 0

    def move_row_down(self, row, num_rows):
        """Move a row down."""
        for column in range(self.num_cols):
            self.grid[row+num_rows][column] = self.grid[row][column]
            self.grid[row][column] = 0

    def clear_full_rows(self):
        """Clear full rows and move the rows above down."""
        completed = 0
        for row in range(self.num_rows-1, 0, -1):
            if self.is_row_full(row):
                self.clear_row(row)
                completed += 1
            elif completed > 0:
                self.move_row_down(row, completed)
        return completed
    
    def reset(self):
        """Reset the grid."""
        for row in range(self.num_rows):
            for column in range(self.num_cols):
                self.grid[row][column] = 0