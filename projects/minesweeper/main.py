import pygame
import asyncio

async def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((30, 30, 30))
        pygame.display.flip()

        await asyncio.sleep(0)  # 2. Yield control back to browser context
        clock.tick(60)

    pygame.quit()

# 3. Entry point
asyncio.run(main())
