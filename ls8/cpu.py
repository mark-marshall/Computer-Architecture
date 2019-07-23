"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = 8 * [0]
        self.ram = 256 * [0]
        self.pc = 0
        self.running = True
        self.opcodes = {
            "LDI": 0b10000010,
            "PRN": 0b01000111,
            "HLT": 0b00000001,
        }
    
    def ram_read(self, address):
        """Return a value from memory at a given address."""
        return self.ram[address]

    def ram_write(self, value, address):
        """Write a value into memory at a given address."""
        self.ram[address] = value

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        program = [
            # From print8.ls8
            0b10000010, # LDI (store a value to the registers)
            0b00000000, # in reg index 0
            0b00001000, # value 8
            0b01000111, # PRN (print a value)
            0b00000000, # at reg index 0
            0b00000001, # HLT --> halt the program
        ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif oop == "DIV":
            self.reg[reg_a] //= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while self.running:
            # fetch the instruction
            instruction = self.ram[self.pc]
            # decode
            if instruction == self.opcodes['LDI']:
                reg_idx = self.ram[self.pc+1]
                reg_val = self.ram[self.pc+2]
                self.reg[reg_idx] = reg_val
            elif instruction == self.opcodes['PRN']:
                reg_idx = self.ram[self.pc+1]
                print(self.reg[reg_idx])
            elif instruction == self.opcodes['HLT']:
                self.running = False
                sys.exit(1)
            # get the num args from the two high bits and increment pc
            self.pc += (instruction >> 6) + 1
