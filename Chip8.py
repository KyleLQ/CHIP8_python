from random import randrange


class Chip8:

    ROWS = 32
    COLS = 64

    def __init__(self, rom_name):
        self.memory = [0] * 0x1000
        self.pc = 0x200
        self.I = 0
        self.stack = [0] * 16
        self.sp = -1
        self.registers = [0] * 16
        self.display = [[0] * self.COLS for i in range(self.ROWS)]  # display is 32 rows by 64 columns
        self.delay_timer = 0
        self.sound_timer = 0
        self.keypad = [0] * 16  # 0 = not pressed, 1 = pressed

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
        with open(f"ROMS/{rom_name}", "rb") as rom:
            byte = rom.read(1)
            while byte != b"":
                self.memory[address] = int(byte.hex(), 16)
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
                            self.registers[0xf] = 1
                        else:
                            self.registers[0xf] = 0
                        self.registers[second_nibble] = (self.registers[second_nibble] -
                                                         self.registers[third_nibble] + 0x100) & 0x0ff
                    case 0x6:
                        if self.registers[second_nibble] % 2 == 1:
                            self.registers[0xf] = 1
                        else:
                            self.registers[0xf] = 0
                        self.registers[second_nibble] = self.registers[second_nibble] >> 1
                    case 0x7:
                        if self.registers[third_nibble] > self.registers[second_nibble]:
                            self.registers[0xf] = 1
                        else:
                            self.registers[0xf] = 0
                        self.registers[second_nibble] = (self.registers[third_nibble] -
                                                         self.registers[second_nibble] + 0x100) & 0x0ff
                    case 0xe:
                        if self.registers[second_nibble] >= 0x80:
                            self.registers[0xf] = 1
                        else:
                            self.registers[0xf] = 0
                        self.registers[second_nibble] = (self.registers[second_nibble] << 1) & 0x0ff
                    case _:
                        raise InvalidInstruction(instruction)
            case 0x9:
                if self.registers[second_nibble] != self.registers[third_nibble]:
                    self.pc += 2
            case 0xa:
                self.I = (second_nibble << 8) + (third_nibble << 4) + fourth_nibble
            case 0xb:
                self.pc = (second_nibble << 8) + (third_nibble << 4) + fourth_nibble + self.registers[0]
            case 0xc:
                self.registers[second_nibble] = ((third_nibble << 4) + fourth_nibble) & randrange(0, 256)
            case 0xd:
                erased_pixels = 0
                sprite_data = [0] * fourth_nibble
                for index in range(fourth_nibble):
                    sprite_data[index] = self.memory[self.I + index]

                start_x = self.registers[second_nibble]
                start_y = self.registers[third_nibble]
                for y in range(fourth_nibble):
                    for x in range(8):
                        bit = (sprite_data[y] & (0b00000001 << (7 - x))) >> (7 - x)
                        if (self.display[(start_y + y) % self.ROWS][(start_x + x) % self.COLS] == 1) and (bit == 1):
                            erased_pixels = 1
                        self.display[(start_y + y) % self.ROWS][(start_x + x) % self.COLS] ^= bit
                self.registers[0xf] = erased_pixels
            case 0xe:
                if third_nibble == 0x9:
                    if self.keypad[self.registers[second_nibble]] == 1:
                        self.pc += 2
                else:
                    if self.keypad[self.registers[second_nibble]] != 1:
                        self.pc += 2
            case 0xf:
                second_byte = (third_nibble << 4) + fourth_nibble
                match second_byte:
                    case 0x07:
                        self.registers[second_nibble] = self.delay_timer
                    case 0x0a:
                        pressed_key = -1
                        for key in range(0, 16):
                            if self.keypad[key] == 1:
                                pressed_key = key
                                break
                        if pressed_key == -1:
                            self.pc -= 2
                        else:
                            self.registers[second_nibble] = pressed_key
                    case 0x15:
                        self.delay_timer = self.registers[second_nibble]
                    case 0x18:
                        self.sound_timer = self.registers[second_nibble]
                    case 0x1e:
                        self.I += self.registers[second_nibble]
                    case 0x29:
                        self.I = 0x50 + self.registers[second_nibble] * 0x5
                    case 0x33:
                        self.memory[self.I] = int((self.registers[second_nibble] -
                                                   (self.registers[second_nibble] % 100)) / 100)
                        self.memory[self.I + 1] = int(((self.registers[second_nibble] % 100) -
                                                       (self.registers[second_nibble] % 10)) / 10)
                        self.memory[self.I + 2] = self.registers[second_nibble] % 10
                    case 0x55:
                        for loc in range(0, second_nibble + 1):
                            self.memory[self.I + loc] = self.registers[loc]
                    case 0x65:
                        for loc in range(0, second_nibble + 1):
                            self.registers[loc] = self.memory[self.I + loc]
                    case _:
                        raise InvalidInstruction(instruction)
            case _:
                raise InvalidInstruction(instruction)


class InvalidInstruction(Exception):

    def __init__(self, instruction, *args):
        super().__init__(args)
        self.instruction = instruction

    def __str__(self):
        return f'The instruction {hex(self.instruction)} is not valid'
