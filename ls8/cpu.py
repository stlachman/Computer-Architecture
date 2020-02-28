"""CPU functionality."""

import sys
import re

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0, 0, 0, 0, 0, 0, 0, 0xF4]
        self.ram = [0] * 256
        self.pc = 0
        self.halted = False
        self.instructions = { 
          0b10000010 : self.ldi, 
          0b01000111 : self.prn, 
          0b00000001 : self.hlt, 
          0b10100010 : self.mult,
          0b01000110 : self.pop,
          0b01000101 : self.push,
          0b00011000 : self.mult2print,
          0b00010001 : self.ret,
          0b01010000 : self.call,
          0b10100000 : self.add,
          0b10100111 : self._cmp,
          0b01010100 : self.jmp,
          0b01010101 : self.jeq,
          0b01010110 : self.jne
        }

        self.fl = [0] * 8
        self.sp = 7
        self.equal = 7
        self.greater_than = 6
        self.less_than = 5

        # self.reg_a = self.ram[self.pc+1]

    def _cmp(self):
      self.alu("CMP", self.ram[self.pc+1], self.ram[self.pc+2])

    def add(self):
      self.alu("ADD", self.ram[self.pc+1], self.ram[self.pc+2])


    def jeq(self):
      # go to register number provided
      register_num = self.ram[self.pc+1]
      if self.fl[self.equal] == 1:
        self.pc = self.reg[register_num ]
      # skip past register number
      else: 
        self.pc += 2

    def jne(self): 
      # go to register number provided
      register_num = self.ram[self.pc+1]
      if self.fl[self.equal] == 0:
        self.pc = self.reg[register_num]
      # skip past register number
      else: 
        self.pc += 2

    def jmp(self): 
      register_num = self.ram[self.pc+1]
      self.pc = self.reg[register_num]

    def call(self):
      # Get value from register, i.e. next instruction
      next_instruction = self.reg[self.ram[self.pc+1]]
      
      if next_instruction in self.instructions: 
        # Setting top of stack equal to instruction when we return from call
        self.ram[self.reg[self.sp]] = self.pc + 2

        # move program counter to function in ram
        self.pc = next_instruction
        # call function
        self.instructions[next_instruction]()

    def mult2print(self):
      op = self.ram[self.pc]
      first_register = self.ram[self.pc+1] 
      second_register = self.ram[self.pc+2]
      
      if op in self.instructions:
        self.instructions[op]()

      self.pc += 3
      self.prn()
      self.ret()

    def ret(self):
      # Get last pc from stack by popping
      self.pc = self.ram[self.reg[self.sp]]
      # Set new pc

    # python ls8.py stack
    def push(self):
      register_num = self.ram[self.pc+1]
      # prevent sp and pc form crossing over
      if self.reg[self.sp] > 0 and self.reg[self.sp] > self.pc + 3:
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = self.reg[register_num]
        self.pc += 2
      else: 
        print("error")
      

    def pop(self):
      register_num = self.ram[self.pc+1]
      if self.reg[self.sp] < 256: 
        # get value from top of stack
        value = self.ram[self.reg[self.sp]]
        # assigns to value current register number
        self.reg[register_num] = value
        self.reg[self.sp] += 1
        self.pc += 2
      else: 
        print("Nothing in that stack")


    def ldi(self):
      value = self.ram[self.pc+2]
      register_num = self.ram[self.pc+1]
      self.reg[register_num] = value
      self.pc += 3
    
    def prn(self):
      register_num = self.ram[self.pc+1]
      print(self.reg[register_num])
      self.pc += 2

    def hlt(self):
      self.halted = True
      self.pc += 1

    def mult(self):
      first_register_num = self.ram[self.pc+1]
      second_register_num = self.ram[self.pc+2]

      first_num = self.reg[first_register_num]
      second_num = self.reg[second_register_num]

      product = first_num * second_num

      self.reg[first_register_num] = product 
      
      self.pc += 3

    def ram_read(self, address):
      print(self.ram[address])
    
    def ram_write(self, address, value):
      self.ram[address] = value

    def load(self, file):
        """Load a program into memory."""

        address = 0

        program = []

        f = open(file)
        list_of_lines = f.read().split('\n')
        
        for line in list_of_lines:
          sliced_string = line[:8]
          if re.search(r"[0-1]{8}", sliced_string) is not None:
            program.append(int(sliced_string, 2))

        for instruction in program:
            self.ram[address] = instruction
            address += 1
        f.close()


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
            self.pc += 3
        elif op == "CMP": 
          self.fl[-3:] = [0,0,0]
          if self.reg[reg_a] == self.reg[reg_b]:
            self.fl[self.equal] = 1
          elif self.reg[reg_a] > self.reg[reg_b]:
            self.fl[self.greater_than] = 1
          else:
            self.fl[self.less_than] = 1
          self.pc += 3
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
        while not self.halted:
          instruction = self.ram[self.pc]
          if instruction in self.instructions:  
            # LDI store a value in register
            self.instructions[instruction]()
          else: 
            print(f"Unknown instruction at index {self.pc}")
            sys.exit(1)
