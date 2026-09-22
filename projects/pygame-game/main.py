import pygame as pg
import sys
import numpy as np
import math
import random
import asyncio

async def main():
    pg.init()
    pg.font.init()
    running = True
    screen_width = 600
    screen_height = 600
    screen = pg.display.set_mode((screen_width, screen_height))
    clock = pg.time.Clock()
    lose = False

    #master parameters
    board_size = 10      #length and width
    mine_density = 20   #percent of tiles that are mines
    font = pg.font.Font(None, int(tile_width*1.1))

    #calculated from master
    tile_width = int((screen_width - 50) / board_size)
    mine_count = int(board_size ** 2 * mine_density / 100)

    def id_from_idx(idx):
        id = [0,0]
        id[0] = idx % (board_size + 2)
        id[1] = idx // (board_size + 2)
        return id

    def idx_from_id(id):
            ix = 0
            ix += id[1] * (board_size + 2)
            ix += id[0]
            return int(ix)

    class Gamestate:
        def __init__(self):
            self.lose = False
            self.flags_left = mine_count
    gamestate = Gamestate()

    class Tile:
        def __init__(self, id, status, mine=False):
            self.index = idx_from_id(id) #index is its location in the 1-d array
            self.id = id
            self.status = status
            self.mine = mine
            self.pos =  (np.array(self.id)-1) * tile_width + 25
        def rect(self):
            return [(self.id[0]-1) * tile_width + 25, (self.id[1]-1) * tile_width + 25, tile_width, tile_width]
        def left_click(self):
            print(f'click received by tile {self.id}')
            if self.status == 'unclicked':
                self.status = 'clicked'
                if self.mine:
                    gamestate.lose = True
        def right_click(self):
            if self.status == 'unclicked':
                self.status = 'flagged'
                gamestate.flags_left -= 1
            else:
                self.status = 'unclicked'
                gamestate.flags_left += 1
        def calc_number(self):
            if self.mine:
                return 0
            k = self.index - board_size - 2
            m = self.index
            l = self.index + board_size + 2
            relevant_indices = (m-1, m+1, k+1, k-1, l+1, l-1, k, l)
            number = 0
            for n in relevant_indices:
                if tiles[n].mine:
                    number += 1
            self.number = number


    def render_tile(tile):
        if tile.status == 'unclicked' or tile.status == 'flagged':
            pg.draw.rect(screen, (230,230,230), tile.rect())
        if tile.status == 'clicked':
            pg.draw.rect(screen, (180,180,180), tile.rect())
            if tile.number > 0:
                text = font.render(f"{tile.number}", True,color_num(tile.number))
                screen.blit(text, tile.pos + tile_width/6)
        if tile.status == 'flagged':
            pg.draw.polygon(screen, 'red', (tile.pos + (tile_width/4), (tile.pos[0]+tile_width*0.75,tile.pos[1]+tile_width/2), (tile.pos[0]+tile_width*0.25, tile.pos[1]+tile_width*0.75)))
        if tile.mine and gamestate.lose:
            print(gamestate.lose)
            pg.draw.ellipse(screen, (30,30,30), (tile.pos[0] + (tile_width*0.3),tile.pos[1] + (tile_width*0.3),tile_width*0.4, tile_width*0.4))
            pg.draw.polygon(screen, (30,30,30), (tile.pos + (tile_width/4) + np.array((tile_width*0.1,0)), (tile.pos[0]+tile_width*0.80,tile.pos[1]+tile_width/2), (tile.pos[0]+tile_width*0.35, tile.pos[1]+tile_width*0.75)))
        pg.draw.rect(screen, "black", tile.rect(), int(tile_width/10))

    def color_num(num):
        colors = np.array([(0,0,255),(0, 128, 0),(255,0,0),(0, 0, 139),(128, 0, 0),(0, 255, 255),(0,0,0),(128, 128, 128)])
        return colors[num-1]



    def find_current_tile():
        for tile in tiles:
            if mouse_pos[0] > tile.pos[0] and mouse_pos[0] < tile.pos[0] + tile_width:
                if mouse_pos[1] > tile.pos[1] and mouse_pos[1] < tile.pos[1] + tile_width:
                    print(tile.id)
                    return tile.index

    def iterate_playable_tiles(fun):
        for tile in tiles:
            if tile.id[0] != 0 and tile.id[0] != board_size+1:
                if tile.id[1] != 0 and tile.id[1] != board_size+1:
                    fun(tile)
    tiles = []
    for y in range(0,board_size+2):
        for x in range(0,board_size+2):
            tiles.append(Tile([x,y], 'unclicked'))

    def reset_tile(x):
        x.mine = False
        x.number = 0
        x.status = 'unclicked'

    def reset():
        #create a bunch of blank tiles
        iterate_playable_tiles(reset_tile)
        #make a bunch of mines
        mines_created = 0
        while mines_created < mine_count:
            tile = tiles[random.randint(0,len(tiles)-1)]
            if not tile.mine:
                if tile.id[0] != 0 and tile.id[0] != board_size+1:
                    if tile.id[1] != 0 and tile.id[1] != board_size+1:
                        tile.mine = True
                        mines_created += 1
        iterate_playable_tiles(lambda x: x.calc_number())
        gamestate.flags_left = mine_count
        gamestate.lose = False

    reset()



    while(running):
        events = pg.event.get()
        mouse_pos = np.array(pg.mouse.get_pos())
        for event in events:
            if event.type == pg.QUIT:
                running = False
                pg.quit()
                sys.exit()
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1 and not gamestate.lose:
                    if find_current_tile() != None:
                        tiles[find_current_tile()].left_click()
                elif event.button == 1 and gamestate.lose:
                    reset()
                if event.button == 3:
                    if find_current_tile() != None:
                        tiles[find_current_tile()].right_click()
        
        screen.fill("white")

        iterate_playable_tiles(render_tile)

        pg.display.update()
        
    
        await asyncio.sleep(0)
        clock.tick(60)
    pg.quit()

#entry point
asyncio.run(main())