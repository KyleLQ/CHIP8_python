from Chip8 import Chip8

# Best Resources:
# http://devernay.free.fr/hacks/chip8/C8TECH10.HTM#2.1
# https://tobiasvl.github.io/blog/write-a-chip-8-emulator/
# https://multigesture.net/articles/how-to-write-an-emulator-chip-8-interpreter/
# https://en.wikipedia.org/wiki/CHIP-8


if __name__ == '__main__':
    Chip8 = Chip8("test_opcode.ch8")
    """
    print(len(Chip8.memory))
    print(Chip8.memory[0x9f])
    print(Chip8.memory[102])
    print(Chip8.pc)

    for i in range(0,len(Chip8.memory)):
        if i % 0x100 == 0:
            print("i\n")
        print(r'{0:#x}'.format(Chip8.memory[i]), end=' ')

    print("\n\n")
    print(type(Chip8.memory[0x50]))
    print(type(Chip8.memory[0x200]))

    # !!!
    print(str(r'{0:#x}'.format(Chip8.memory[0x200]))[2] == '1')
    """

    #print(str(r'{0:#x}'.format(Chip8._fetch())))  #4686

    print((123 - 17 + 0x100) & 0x0ff)

    #Chip8.do_CPU_cycle()


    # b'\x12N\xea\xac\xaa\xea\xce\xaa\xaa\xae\xe0\xa0\xa0\xe0\xc0@@\xe0\xe0 \xc0\xe0\xe0` \xe0\xa0\xe0  `@
    # what's up with this?
    # https://stackoverflow.com/questions/8710456/reading-a-binary-file-with-python

    # https://stackoverflow.com/questions/56523036/i-read-image-file-as-binary-strange-symbols-appear
    # for i in open(f"ROMS/{rom_name}", 'rb').read():
    # print(r'{0:#x}'.format(i), end=' ')


    # negative values???
    # left bit shift???

    # https://www.emutalk.net/threads/chip-8.19894/page-26
    # look at #505 for subtraction !!!!