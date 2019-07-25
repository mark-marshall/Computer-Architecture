"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = 8 * [0]
        self.reg[7] = 0xF4
        self.ram = 256 * [0]
        self.pc = 0
        self.ir = self.ram[self.pc]
        # fl = 0b00000LGE
        self.fl = 0b00000000   
        self.running = True 
        self.opcodes = {
            "NOP":  0b00000000,
            "LDI":  0b10000010,
            "PRN":  0b01000111,
            "ADD":  0b10100000,
            "MUL":  0b10100010,
            "HLT":  0b00000001,
            "PUSH": 0b01000101,
            "POP":  0b01000110,
            "CALL": 0b01010000,
            "RET":  0b00010001,
            "CMP":  0b10100111,
        }
        self.branch_table = {}
        self.branch_table[self.opcodes['NOP']] = self.nop
        self.branch_table[self.opcodes['LDI']] = self.ldi
        self.branch_table[self.opcodes['PRN']] = self.prn
        self.branch_table[self.opcodes['ADD']] = self.add
        self.branch_table[self.opcodes['MUL']] = self.mul
        self.branch_table[self.opcodes['HLT']] = self.hlt
        self.branch_table[self.opcodes['PUSH']] = self.push
        self.branch_table[self.opcodes['POP']] = self.pop
        self.branch_table[self.opcodes['CALL']] = self.call
        self.branch_table[self.opcodes['RET']] = self.ret
        self.branch_table[self.opcodes['CMP']] = self.cmp
    
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
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] //= self.reg[reg_b]
        elif op == "MOD":
            self.reg[reg_a] %= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] > self.reg[reg_b]:
                return "G"
            elif self.reg[reg_b] > self.reg[reg_a]:
                return "L"
            else:
                return "E"
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()
    
    def nop(self):
        """Run NOP."""
        pass
    
    def ldi(self):
        """Run LDI."""
        reg_idx = self.ram[self.pc+1]
        reg_val = self.ram[self.pc+2]
        self.reg[reg_idx] = reg_val
    
    def prn(self):
        """Run PRN."""
        reg_idx = self.ram[self.pc+1]
        print(self.reg[reg_idx])
    
    def add(self):
        """Run ADD."""
        self.alu('ADD', self.ram[self.pc+1], self.ram[self.pc+2])

    def mul(self):
        """Run MUL."""
        self.alu('MUL', self.ram[self.pc+1], self.ram[self.pc+2])
    
    def hlt(self):
        """Run HLT."""
        self.running = False
        sys.exit(1)

    def push(self):
        """Run push onto the stack."""
        # grab the target reg idx
        reg_idx = self.ram[self.pc+1]
        # grab the value to be pushed from the reg idx
        push_val = self.reg[reg_idx]
        # grab the stack pointer
        sp = self.reg[7]
        # push the value onto the stack
        self.ram[sp] = push_val
        # decremment the sp by 1
        self.reg[7] -= 1
    
    def pop(self):
        """Run pop off the stack."""
        # grab the target reg idx
        reg_idx = self.ram[self.pc+1]
        # return the sp to the last value in stack
        self.reg[7] += 1
        # grab the new stack pointer
        sp = self.reg[7]
        # grab the value to be popped from the stack
        pop_val = self.ram[sp]
        # set the last stack value to 0
        self.ram[sp] = 0
        # add the popped value to the reg idx
        self.reg[reg_idx] = pop_val
    
    def call(self):
        """Make a function call."""
        # get address instruction to hold on stack
        push_val = (self.pc + 2)
        # push the address onto the stack
        sp = self.reg[7]
        self.ram[sp] = push_val
        self.reg[7] -= 1
        # set the pc to the call address
        reg_idx = self.ram[self.pc+1]
        call_address = self.reg[reg_idx]
        self.pc = call_address

    def ret(self):
        """Return after a function call."""
        # pop the value from the top of the stack
        self.reg[7] += 1
        sp = self.reg[7]
        ret_address = self.ram[sp]
        self.ram[sp] = 0
        # set the pc to the ret address
        self.pc = ret_address

    def cmp(self):
        """Compare values in two registers."""
        # do comparison via the ALU
        flag = self.alu('CMP', self.ram[self.pc+1], self.ram[self.pc+2])
        if flag == 'G':
            self.flag = 0b00000010
        elif flag == 'L':
            self.flag = 0b00000100
        else:
            self.flag = 0b00000001

    def run(self):
        """Run the CPU."""
        while self.running:
            # fetch the instruction
            instruction = self.ram[self.pc]
            # access branch table
            self.branch_table[instruction]()
            # check to see if the instruction sets pc directly
            if instruction in {self.opcodes['CALL'], self.opcodes['RET']}:
                continue
            # get the num args from the two high bits and increment pc
            self.pc += (instruction >> 6) + 1
