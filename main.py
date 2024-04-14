import pygame
import random
import math

pygame.init()

## CONSTANTS
WIDTH = 800
HEIGH = 800
FPS = 60
ROWS = 4
COLS = 4
RECT_HEIGHT = HEIGH / ROWS
RECT_WIDTH = WIDTH / COLS
OUTLINE_COLOR = (187, 173, 160)
OUTLINE_THICKNESS = 10
BACKGROUND_COLOR = (205, 192, 180)
FONT_COLOR = (119, 110, 101)
TITLE = '2048'
FONT = pygame.font.SysFont("comicsans", 60, bold=True)
SCREEN = pygame.display.set_mode((WIDTH, HEIGH))
MOVE_VEL = 20
NEW_TILE_VALUE = 2
COLORS = [
        (237, 229, 218),
        (238, 225, 201),
        (243, 178, 122),
        (246, 150, 101),
        (247, 124, 95),
        (247, 95, 59),
        (237, 208, 115),
        (237, 204, 99),
        (236, 202, 80)
]

class Tile:
    
    def __init__(self ,value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.x_cor = col * RECT_WIDTH
        self.y_cor = row * RECT_WIDTH

    def choose_color(self):
        self.color_lv = int(math.log2(self.value) - 1)
        color = COLORS[self.color_lv] 
        return color 
    
    def draw_tile(self, window):
        self.color = self.choose_color()
        pygame.draw.rect(window, self.color, (self.x_cor, self.y_cor, RECT_WIDTH, RECT_HEIGHT))
        text = FONT.render(str(self.value), 1, FONT_COLOR)
        window.blit(text,
            (
                self.x_cor + (RECT_WIDTH / 2) - (text.get_width() / 2),
                self.y_cor + (RECT_HEIGHT / 2) - (text.get_height() / 2),
            )
        )
    
    def move(self, delta):
        self.x_cor += delta[0]
        self.y_cor += delta[1]
    
    def set_pos(self, ceil=False):
        if ceil:
            self.row = math.ceil(self.y_cor/RECT_HEIGHT)
            self.col = math.ceil(self.x_cor/RECT_WIDTH)
        else:
            self.row = math.floor(self.y_cor/RECT_HEIGHT)
            self.col = math.floor(self.x_cor/RECT_WIDTH)

def draw_background(window):
    window.fill(BACKGROUND_COLOR)
    

def draw_grid(window):
    x_delta = WIDTH / COLS        
    y_delta = HEIGH / ROWS
    for i in range(1, COLS):
            pygame.draw.line(window, OUTLINE_COLOR, (0, i * y_delta), (HEIGH, i * y_delta), OUTLINE_THICKNESS)
    for i in range(1, ROWS):
            pygame.draw.line(window, OUTLINE_COLOR, (i * x_delta, 0), (i * x_delta, WIDTH), OUTLINE_THICKNESS)
    pygame.draw.rect(window, OUTLINE_COLOR, (0,0, WIDTH, HEIGH), OUTLINE_THICKNESS)


def draw(window, tiles):
    draw_background(window)
    for tile in tiles.values():
        tile.draw_tile(SCREEN)
    draw_grid(window)
    pygame.display.update()

def get_random_position(tiles):
    row = None
    col = None
    while True:
        row = random.randrange(0, ROWS)
        col = random.randrange(0, COLS)

        if f'{row}-{col}' not in tiles:
            break

    return row, col

def generate_tiles():
    tiles = {}
    for _ in range(2):
        row, col = get_random_position(tiles)
        tiles[f'{row}-{col}'] = Tile(NEW_TILE_VALUE, row, col)
    return tiles

def move_tiles(window, tiles, clock, direction):
    updated = True
    blocks = set()

    if direction == 'left':
        sort_func = lambda x: x.col
        reverse = False
        delta = (-MOVE_VEL, 0)
        boundary_check = lambda tile: tile.col == 0
        get_next_tile = lambda tile: tiles.get(f'{tile.row}-{tile.col - 1}')
        merge_check = lambda tile, next_tile: tile.x_cor > next_tile.x_cor + MOVE_VEL
        move_check = lambda tile, next_tile: tile.x_cor > next_tile.x_cor + RECT_WIDTH + MOVE_VEL
        ceil = True
    elif direction == 'right':
        sort_func = lambda x: x.col
        reverse = True
        delta = (MOVE_VEL, 0)
        boundary_check = lambda tile: tile.col == COLS - 1
        get_next_tile = lambda tile: tiles.get(f'{tile.row}-{tile.col + 1}')
        merge_check = lambda tile, next_tile: tile.x_cor < next_tile.x_cor - MOVE_VEL
        move_check = lambda tile, next_tile: tile.x_cor + RECT_WIDTH + MOVE_VEL < next_tile.x_cor
        ceil = False
    elif direction == 'up':
        sort_func = lambda x: x.row
        reverse = False
        delta = (0, -MOVE_VEL)
        boundary_check = lambda tile: tile.row == 0
        get_next_tile = lambda tile: tiles.get(f'{tile.row - 1}-{tile.col}')
        merge_check = lambda tile, next_tile: tile.y_cor > next_tile.y_cor + MOVE_VEL
        move_check = lambda tile, next_tile: tile.y_cor > next_tile.y_cor + RECT_HEIGHT + MOVE_VEL
        ceil = True
    elif direction == 'down':
        sort_func = lambda x: x.col
        reverse = True
        delta = (0, MOVE_VEL)
        boundary_check = lambda tile: tile.row == ROWS - 1
        get_next_tile = lambda tile: tiles.get(f'{tile.row + 1}-{tile.col}')
        merge_check = lambda tile, next_tile: tile.y_cor < next_tile.y_cor - MOVE_VEL
        move_check = lambda tile, next_tile: tile.y_cor + RECT_WIDTH + MOVE_VEL < next_tile.y_cor 
        ceil = False
    while updated:
        clock.tick(FPS)
        updated = False
        sorted_tiles = sorted(tiles.values(), key=sort_func, reverse=reverse)

        for i, tile in enumerate(sorted_tiles):
            if boundary_check(tile):
                continue
                
            next_tile = get_next_tile(tile)
            if not next_tile:
                tile.move(delta)
            elif tile.value == next_tile.value and tile not in blocks and next_tile not in blocks:
                if merge_check(tile, next_tile):
                    tile.move(delta)
                else:
                    next_tile.value *= 2
                    sorted_tiles.pop(i)
                    blocks.add(next_tile)
            elif move_check(tile, next_tile):
                tile.move(delta)
            else:
                continue
            
            tile.set_pos(ceil)
            updated = True
    
        update_tiles(window, tiles, sorted_tiles)
    
    end_move(tiles)
    
def end_move(tiles):
    if len(tiles) == 16:
        return 'lost'

    row, col = get_random_position(tiles)
    tiles[f'{row}-{col}'] = Tile(random.choice([2,4]), row, col)
    return 'continue'


def update_tiles(window, tiles, sorted_tiles):
    tiles.clear()
    for tile in sorted_tiles:
        tiles[f'{tile.row}-{tile.col}'] = tile
    draw(window, tiles)

## GAME
def main(window): 

    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    tiles = generate_tiles()

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False


            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    move_tiles(window, tiles, clock, 'left')
                if event.key == pygame.K_RIGHT:
                    move_tiles(window, tiles, clock, 'right')
                if event.key == pygame.K_UP:
                    move_tiles(window, tiles, clock, 'up')
                if event.key == pygame.K_DOWN:
                    move_tiles(window, tiles, clock, 'down')

        draw(window, tiles)

if __name__ == '__main__':
    main(SCREEN)

