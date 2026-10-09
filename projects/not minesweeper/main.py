import pygame as pg
import asyncio  # 1. Import asyncio

async def main():
    pg.init()
    screen = pg.display.set_mode((640, 480))
    clock = pg.time.Clock()
    running = True

    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        screen.fill((30, 30, 30))
        pg.display.flip()
        pg.draw.rect(screen, (230, 230, 230), (100,100,200,200))

        await asyncio.sleep(0)  # 2. Yield control back to browser context
        clock.tick(60)

    pg.quit()

# 3. Entry point
asyncio.run(main())