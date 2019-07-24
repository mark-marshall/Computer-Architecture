"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = 8 * [0]
        self.reg[7] = 0xFF
        self.ram = 256 * [0]
        self.pc = 0
        self.fl = 0
        self.running = True
        self.opcodes = {
            "LDI": 0b10000010,
            "PRN": 0b01000111,
            "MUL": 0b10100010,
            "HLT": 0b00000001,
        }
        self.branch_table = {}
        self.branch_table[self.opcodes['LDI']] = self.ldi
        self.branch_table[self.opcodes['PRN']] = self.prn
        self.branch_table[self.opcodes['MUL']] = self.mul
        self.branch_table[self.opcodes['HLT']] = self.hlt
        
    
    def ram_read(self, address):
        """Return a value from memory at a given address."""
        return self.ram[address]

    def ram_write(self, value, address):
        """Write a value into memory at a given address."""
        self.ram[address] = value

    def load(self, program):
        """Load a program into memory."""
        # initialize a value for the address
        address = 0
        # try and open the program
        try:
            with open(program) as program:
                for line in program:
                    # split on comment symbols
                    line_split = line.split('#')
                    # store pre-comments to a value and trim whitespace
                    value = line_split[0].strip()
                    # check for any lines that are purely comments
                    if value == "":
                        continue
                    formatted_value = int(value, 2)
                    # store it in memory
                    self.ram[address] = formatted_value
                    # increment the address
                    address += 1
        # sys exit and erroring if file can't be found
        except FileNotFoundError:
            print(f"{program} not found")
            sys.exit(2)

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        if op == "INC":
            self.reg[reg_a] += 1
        elif op == "DEC":
            self.reg[reg_a] -= 1
        elif op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
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
    
    def ldi(self):
        """Run LDI."""
        reg_idx = self.ram[self.pc+1]
        reg_val = self.ram[self.pc+2]
        self.reg[reg_idx] = reg_val
    
    def prn(self):
        """Run PRN."""
        reg_idx = self.ram[self.pc+1]
        print(self.reg[reg_idx])

    def mul(self):
        """Run MUL."""
        self.alu('MUL', self.ram[self.pc+1], self.ram[self.pc+2])
    
    def hlt(self):
        """Run HLT."""
        self.running = False
        sys.exit(1)

    def run(self):
        """Run the CPU."""
        while self.running:
            # fetch the instruction
            instruction = self.ram[self.pc]
            # access branch table
            self.branch_table[instruction]()
            # get the num args from the two high bits and increment pc
            self.pc += (instruction >> 6) + 1
