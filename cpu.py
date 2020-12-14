import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MULT = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110


class CPU:
    def __init__(self):
        self.running = False
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.sp = 7
        self.reg[self.sp] = 0xF4
        self.l = 0
        self.g = 0
        self.pc = 0
        self.e = 0
        self.ir_methods = {
            HLT: self.hlt,
            PRN: self.prn,
            MULT: self.mult,
            LDI: self.ldi,
            RET: self.ret,
            ADD: self.add,
            CMP: self.compare,
            JMP: self.jmp,
            JEQ: self.jeq,
            JNE: self.jne,
            PUSH: self.push,
            POP: self.pop,
            CALL: self.call
        }

    def load(self, file_path):
        address = 0

        with open(file_path) as program:
            for line in program:
                line = line.strip().split()

                if len(line) == 0 or line[0] == "#":
                    continue

                try:
                    self.ram[address] = int(line[0], 2)

                except ValueError:
                    print(f"Invalid number: {line[0]}")

                address += 1

    def alu(self, op, reg_a, reg_b):
        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]

        elif op == "MULT":
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == "CMP":

            if self.reg[reg_a] == self.reg[reg_b]:
                self.e = 1
            else:
                self.e = 0

            if self.reg[reg_a] < self.reg[reg_b]:
                self.l = 1
            else:
                self.l = 0

            if self.reg[reg_a] > self.reg[reg_b]:
                self.g = 1
            else:
                self.g = 0

        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

    def ram_read(self, MAR):
        print(self.reg[MAR])

    def ram_write(self, MDR, MAR):
        self.reg[MAR] = MDR

    def hlt(self):
        self.running = False
        sys.exit(1)

    def ldi(self):
        reg_num = self.ram[self.pc+1]
        value = self.ram[self.pc+2]

        self.ram_write(value, reg_num)
        self.pc += 3

    def prn(self):
        reg_num = self.ram[self.pc + 1]

        self.ram_read(reg_num)
        self.pc += 2

    def add(self):
        reg_num_one = self.ram[self.pc + 1]
        reg_num_two = self.ram[self.pc + 2]

        self.alu("ADD", reg_num_one, reg_num_two)
        self.pc += 3

    def mult(self):
        reg_num_one = self.ram[self.pc+1]
        reg_num_two = self.ram[self.pc+2]

        self.alu("MULT", reg_num_one, reg_num_two)
        self.pc += 3

    def push(self):
        self.reg[self.sp] -= 1

        reg_num = self.ram[self.pc + 1]
        value = self.reg[reg_num]
        top_of_stack_addr = self.reg[self.sp]

        self.ram[top_of_stack_addr] = value
        self.pc += 2

    def pop(self):
        top_of_stack_addr = self.reg[self.sp]
        value = self.ram[top_of_stack_addr]
        reg_num = self.ram[self.pc + 1]

        self.reg[reg_num] = value
        self.reg[self.sp] += 1
        self.pc += 2

    def call(self):
        ret_addr = self.pc + 2

        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = ret_addr

        reg_num = self.ram[self.pc + 1]
        self.pc = self.reg[reg_num]

    def ret(self):
        ret_addr = self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1

        self.pc = ret_addr

    def compare(self):
        reg_one = self.ram[self.pc + 1]
        reg_two = self.ram[self.pc + 2]

        self.alu("CMP", reg_one, reg_two)
        self.pc += 3

    def jmp(self):
        reg_num = self.ram[self.pc + 1]
        next_address = self.reg[reg_num]

        self.pc = next_address

    def jeq(self):
        if self.e == 1:
            self.jmp()
        else:
            self.pc += 2

    def jne(self):
        if self.e == 0:
            self.jmp()
        else:
            self.pc += 2

    def run(self):
        self.running = True

        while self.running:
            ir = self.ram[self.pc]

            if ir in self.ir_methods:
                self.ir_methods[ir]()

            else:
                print(f"Invalid instruction {ir} at address {self.pc}")
                self.running = False
                sys.exit(1)
