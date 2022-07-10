from Chip8 import Chip8
import pygame
import time

# todo
"""
test with more roms
Implement sound
Limit the cycles of CPU
"""

SCALE_FACTOR = 16
COLS = 64
ROWS = 32
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
key_map = [pygame.K_x, pygame.K_1, pygame.K_2, pygame.K_3,
           pygame.K_q, pygame.K_w, pygame.K_e, pygame.K_a,
           pygame.K_s, pygame.K_d, pygame.K_z, pygame.K_c,
           pygame.K_4, pygame.K_r, pygame.K_f, pygame.K_v]


def draw(c8, screen):
    for x in range(COLS):
        for y in range(ROWS):
            if c8.display[y][x] == 1:
                pygame.draw.rect(screen, WHITE, (x * SCALE_FACTOR, y * SCALE_FACTOR, SCALE_FACTOR, SCALE_FACTOR))
            else:
                pygame.draw.rect(screen, BLACK, (x * SCALE_FACTOR, y * SCALE_FACTOR, SCALE_FACTOR, SCALE_FACTOR))
    pygame.display.flip()


if __name__ == '__main__':
    rom_name = input("Enter ROM file name: ")
    Chip8 = Chip8(rom_name)
    pygame.init()
    screen = pygame.display.set_mode([COLS * SCALE_FACTOR, ROWS * SCALE_FACTOR])

    accumulator = 0

    while True:

        begin_time = time.perf_counter()

        pygame.event.pump()
        Chip8.do_CPU_cycle()

        end_time = time.perf_counter()
        accumulator += max((end_time - begin_time), 0.1)
        while accumulator >= (1/60):
            if Chip8.sound_timer > 0:
                Chip8.sound_timer -= 1
            if Chip8.delay_timer > 0:
                Chip8.delay_timer -= 1
            accumulator -= (1/60)

        draw(Chip8, screen)
        keys = pygame.key.get_pressed()
        for i in range(0, 16):
            Chip8.keypad[i] = int(keys[key_map[i]])