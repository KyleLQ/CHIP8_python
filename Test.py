from Chip8 import Chip8

# Best Resources:
# http://devernay.free.fr/hacks/chip8/C8TECH10.HTM#2.1
# https://tobiasvl.github.io/blog/write-a-chip-8-emulator/
# https://multigesture.net/articles/how-to-write-an-emulator-chip-8-interpreter/
# https://en.wikipedia.org/wiki/CHIP-8


if __name__ == '__main__':
    Chip8 = Chip8("test_opcode.80")
    print(len(Chip8.memory))
    print(Chip8.memory[0x9f])
    print(Chip8.memory[102])
    print(Chip8.pc)
    print(Chip8.rom)