class Chip8:
    """
    This class should handle everything related to the CPU and memory and stuff.
    Main will actually call this class, and handle key inputs and graphics/sound display.


    main memory (array)
    function (constructor) to init initial memory stuff (font data)

    current opcode
    array of registers
    index register I - e.g. a pointer to a particular memory address that instructions can manipulate
    pc
    2d array that represents the screen
    stack pointer
    """

    ROWS = 32
    COLS = 64

    def __init__(self,rom_name):
        self.memory = [0] * 0x1000
        self.pc = 0x200
        self.I = 0
        self.stack = [0] * 16
        self.sp = -1 # !!! index of the stack
        self.registers = [0] * 16
        self.display = [[0] * self.COLS for i in range(self.ROWS)] # display is 32 rows by 64 columns

        # timers...

        self._init_fontset()
        self._load_rom(rom_name)

    # store the font data from 0 to F in memory 0x50 - 0x9f
    def _init_fontset(self):
        self.memory[0x50:0x55] = [0xF0, 0x90, 0x90, 0x90, 0xF0]  # 0
        self.memory[0x55:0x5a] = [0x20, 0x60, 0x20, 0x20, 0x70]  # 1
        self.memory[0x5a:0x5f] = [0xF0, 0x10, 0xF0, 0x80, 0xF0]  # 2
        self.memory[0x5f:0x64] = [0xF0, 0x10, 0xF0, 0x10, 0xF0]  # 3
        self.memory[0x64:0x69] = [0x90, 0x90, 0xF0, 0x10, 0x10]  # 4
        self.memory[0x69:0x6e] = [0xF0, 0x80, 0xF0, 0x10, 0xF0]  # 5
        self.memory[0x6e:0x73] = [0xF0, 0x80, 0xF0, 0x90, 0xF0]  # 6
        self.memory[0x73:0x78] = [0xF0, 0x10, 0x20, 0x40, 0x40]  # 7
        self.memory[0x78:0x7d] = [0xF0, 0x90, 0xF0, 0x90, 0xF0]  # 8
        self.memory[0x7d:0x82] = [0xF0, 0x90, 0xF0, 0x10, 0xF0]  # 9
        self.memory[0x82:0x87] = [0xF0, 0x90, 0xF0, 0x90, 0x90]  # A
        self.memory[0x87:0x8c] = [0xE0, 0x90, 0xE0, 0x90, 0xE0]  # B
        self.memory[0x8c:0x91] = [0xF0, 0x80, 0x80, 0x80, 0xF0]  # C
        self.memory[0x91:0x96] = [0xE0, 0x90, 0x90, 0x90, 0xE0]  # D
        self.memory[0x96:0x9b] = [0xF0, 0x80, 0xF0, 0x80, 0xF0]  # E
        self.memory[0x9b:0xA0] = [0xF0, 0x80, 0xF0, 0x80, 0x80]  # F

    def _load_rom(self, rom_name):

        address = 0x200
        # rb+ to read in binary mode. DON'T OPEN IN ANY OTHER WAY, OR RISK CORRUPTING DATA
        with open(f"ROMS/{rom_name}", "rb") as rom:
            byte = rom.read(1)
            while byte != b"":
                self.memory[address] = int(byte.hex(),16)
                address += 0x1
                byte = rom.read(1)

    def do_CPU_cycle(self):
        instruction = self._fetch()
        self._decode_execute(instruction)

    def _fetch(self):
        instruction = (self.memory[self.pc] << 8) + self.memory[self.pc + 1]
        self.pc += 2
        return instruction

    def _decode_execute(self, instruction):
        first_nibble = instruction >> 12
        second_nibble = (instruction & 0x0f00) >> 8
        third_nibble = (instruction & 0x00f0) >> 4
        fourth_nibble = instruction & 0x000f

        match first_nibble:
            case 0x0:  # ignoring the 0nnn SYS address instruction
                if fourth_nibble == 0x0:
                    for row in range(0, self.ROWS):
                        for col in range(0, self.COLS):
                            self.display[row][col] = 0
                else:
                    self.pc = self.stack[self.sp]
                    self.sp -= 1
            case 0x1:
                self.pc = (second_nibble << 8) + (third_nibble << 4) + fourth_nibble
            case 0x2:
                self.sp += 1
                self.stack[self.sp] = self.pc
                self.pc = (second_nibble << 8) + (third_nibble << 4) + fourth_nibble
            case 0x3:
                comp_to = (third_nibble << 4) + fourth_nibble
                if comp_to == self.registers[second_nibble]:
                    self.pc += 2
            case 0x4:
                comp_to = (third_nibble << 4) + fourth_nibble
                if comp_to != self.registers[second_nibble]:
                    self.pc += 2
            case 0x5:
                if self.registers[second_nibble] == self.registers[third_nibble]:
                    self.pc += 2
            case 0x6:
                self.registers[second_nibble] = (third_nibble << 4) + fourth_nibble
            case 0x7:
                self.registers[second_nibble] += (third_nibble << 4) + fourth_nibble
            case 0x8:
                match fourth_nibble:
                    case 0x0:
                        self.registers[second_nibble] = self.registers[third_nibble]
                    case 0x1:
                        self.registers[second_nibble] = self.registers[second_nibble] | self.registers[third_nibble]
                    case 0x2:
                        self.registers[second_nibble] = self.registers[second_nibble] & self.registers[third_nibble]
                    case 0x3:
                        self.registers[second_nibble] = self.registers[second_nibble] ^ self.registers[third_nibble]
                    case 0x4:
                        res = self.registers[second_nibble] + self.registers[third_nibble]
                        if res > 255:
                            self.registers[0xf] = 1
                            self.registers[second_nibble] = res & 0x0ff
                        else:
                            self.registers[0xf] = 0
                            self.registers[second_nibble] = res
                    case 0x5:
                        if self.registers[second_nibble] > self.registers[third_nibble]:
                            self.registers[0xf] == 1
                        else:
                            self.registers[0xf] == 0
                        self.registers[second_nibble] = (self.registers[second_nibble] - self.registers[third_nibble] + 0x100) & 0x0ff
                    case 0x6:
                    case 0x7:
                    case 0xe:
                    case _:
            case 0x9:
            case 0xa:
            case 0xb:
            case 0xc:
            case 0xd:
            case 0xe:
            case 0xf:
            case _:
                # throw exception ...