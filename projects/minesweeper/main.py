import pygame as pg
import sys
import random
import asyncio

async def main():
    pg.init()
    pg.font.init()  # Explicit font initialization for WASM compatibility
    await asyncio.sleep(0.5)
    import numpy as np 
    screen_width = 600
    screen_height = 600
    
    screen = pg.display.set_mode((screen_width, screen_height))
    clock = pg.time.Clock()
    running = True

    # Master parameters
    board_size = 10      # Length and width
    mine_density = 20   # Percent of tiles that are mines

    # Calculated parameters
    tile_width = int((screen_width - 50) / board_size)
    mine_count = int(board_size ** 2 * mine_density / 100)
    
    # Pre-initialize font once to avoid WASM memory thrashing
    font_size = max(12, int(tile_width * 0.8))
    tile_font = pg.font.Font(None, font_size)

    def idx_from_id(tile_id):
        return int(tile_id[1] * (board_size + 2) + tile_id[0])

    class Gamestate:
        def __init__(self):
            self.lose = False
            self.flags_left = mine_count

    gamestate = Gamestate()

    class Tile:
        def __init__(self, tile_id, status, mine=False):
            self.index = idx_from_id(tile_id)
            self.id = tile_id
            self.status = status
            self.mine = mine
            self.pos = (np.array(self.id) - 1) * tile_width + 25
            self.number = 0

        def rect(self):
            return [(self.id[0] - 1) * tile_width + 25, (self.id[1] - 1) * tile_width + 25, tile_width, tile_width]

        def left_click(self):
            if self.status == 'unclicked':
                self.status = 'clicked'
                if self.mine:
                    gamestate.lose = True

        def right_click(self):
            if self.status == 'unclicked':
                self.status = 'flagged'
                gamestate.flags_left -= 1
            elif self.status == 'flagged':
                self.status = 'unclicked'
                gamestate.flags_left += 1

        def calc_number(self):
            if self.mine:
                self.number = 0
                return
            k = self.index - board_size - 2
            m = self.index
            l = self.index + board_size + 2
            relevant_indices = (m - 1, m + 1, k + 1, k - 1, l + 1, l - 1, k, l)
            
            number = 0
            for n in relevant_indices:
                if 0 <= n < len(tiles) and tiles[n].mine:
                    number += 1
            self.number = number

    def color_num(num):
        colors = [(0, 0, 255), (0, 128, 0), (255, 0, 0), (0, 0, 139), 
                  (128, 0, 0), (0, 255, 255), (0, 0, 0), (128, 128, 128)]
        return colors[min(num - 1, len(colors) - 1)]

    def render_tile(tile):
        if tile.status in ('unclicked', 'flagged'):
            pg.draw.rect(screen, (230, 230, 230), tile.rect())
        elif tile.status == 'clicked':
            pg.draw.rect(screen, (180, 180, 180), tile.rect())
            if tile.number > 0:
                text = tile_font.render(f"{tile.number}", True, color_num(tile.number))
                screen.blit(text, tile.pos + tile_width / 4)

        if tile.status == 'flagged':
            pg.draw.polygon(screen, (255, 0, 0), (
                tile.pos + (tile_width / 4),
                (tile.pos[0] + tile_width * 0.75, tile.pos[1] + tile_width / 2),
                (tile.pos[0] + tile_width * 0.25, tile.pos[1] + tile_width * 0.75)
            ))

        if tile.mine and gamestate.lose:
            pg.draw.ellipse(screen, (30, 30, 30), (
                tile.pos[0] + (tile_width * 0.3),
                tile.pos[1] + (tile_width * 0.3),
                tile_width * 0.4, tile_width * 0.4
            ))

        pg.draw.rect(screen, (0, 0, 0), tile.rect(), max(1, int(tile_width / 10)))

    def find_current_tile(mouse_pos):
        for tile in tiles:
            if tile.id[0] not in (0, board_size + 1) and tile.id[1] not in (0, board_size + 1):
                if tile.pos[0] <= mouse_pos[0] < tile.pos[0] + tile_width:
                    if tile.pos[1] <= mouse_pos[1] < tile.pos[1] + tile_width:
                        return tile.index
        return None

    def iterate_playable_tiles(fun):
        for tile in tiles:
            if tile.id[0] not in (0, board_size + 1) and tile.id[1] not in (0, board_size + 1):
                fun(tile)

    tiles = []
    for y in range(0, board_size + 2):
        for x in range(0, board_size + 2):
            tiles.append(Tile([x, y], 'unclicked'))

    def reset_tile(x):
        x.mine = False
        x.number = 0
        x.status = 'unclicked'

    def reset():
        iterate_playable_tiles(reset_tile)
        mines_created = 0
        while mines_created < mine_count:
            tile = tiles[random.randint(0, len(tiles) - 1)]
            if not tile.mine and tile.id[0] not in (0, board_size + 1) and tile.id[1] not in (0, board_size + 1):
                tile.mine = True
                mines_created += 1
        iterate_playable_tiles(lambda x: x.calc_number())
        gamestate.flags_left = mine_count
        gamestate.lose = False

    reset()

    # Main Render Loop
    while running:
        screen.fill((255, 255, 255))
        
        mouse_pos = np.array(pg.mouse.get_pos())
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
                pg.quit()
                sys.exit()

            if event.type == pg.MOUSEBUTTONDOWN:
                clicked_idx = find_current_tile(mouse_pos)
                if event.button == 1:
                    if not gamestate.lose and clicked_idx is not None:
                        tiles[clicked_idx].left_click()
                    elif gamestate.lose:
                        reset()
                elif event.button == 3 and clicked_idx is not None:
                    tiles[clicked_idx].right_click()

        iterate_playable_tiles(render_tile)
        pg.display.update()
        
        clock.tick(60)
        await asyncio.sleep(0)

    pg.quit()

asyncio.run(main())