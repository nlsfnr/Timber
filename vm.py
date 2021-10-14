from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Callable, Union


MEM_CAPACITY = 64_000
# The equivalent to a machine word, e.g. 32 Bits
Val = int


class VMError(Exception):

    def __init__(self, vm: 'VM', msg: str) -> None:
        self.vm = vm
        self.msg = msg

    def __str__(self) -> str:
        return f'[@{self.vm.pc}] {self.msg}'


class InstrKind(Enum):
    Noop = auto()
    Halt = auto()
    Push = auto()
    Pop = auto()
    Rot = auto()
    Dup = auto()
    Load = auto()
    Store = auto()
    Add = auto()
    Sub = auto()
    Shl = auto()
    Shr = auto()
    And = auto()
    Or = auto()
    Call = auto()
    Ret = auto()
    St = auto()
    Jmp = auto()
    JmpF = auto()


@dataclass
class Instr:
    kind: InstrKind
    arg: Optional[Val] = None


class Program(list):

    def push(self, instr: Instr) -> 'Program':
        self.append(instr)
        return self

    @property
    def here(self) -> int:
        return len(self)

    def __str__(self) -> str:
        return '\n'.join([f'{i:03} {x.kind.name:6} '
                          f'{x.arg if x.arg is not None else ""}'
                          for i, x in enumerate(self)])


@dataclass
class VM:
    program: Program
    pc: int = 0
    halted: bool = False
    stack: List[Val] = field(default_factory=list)
    mem: bytearray = field(default_factory=lambda: bytearray(MEM_CAPACITY))

    def step(self) -> None:
        self._check_running()
        self._check_pc()
        instr = self.program[self.pc]
        kind = instr.kind
        arg = instr.arg
        if kind == InstrKind.Noop:
            pass
        elif kind == InstrKind.Halt:
            self._check_stack_depth(1)
            self.halted = True
        elif kind == InstrKind.Push:
            assert arg is not None
            self._push(arg)
        elif kind == InstrKind.Pop:
            self._check_stack_depth(1)
            self._pop()
        elif kind == InstrKind.Rot:
            self._check_stack_depth(2)
            self.stack[-1], self.stack[-2] = self.stack[-2], self.stack[-1]
        elif kind == InstrKind.Dup:
            self._check_stack_depth(1)
            self._push(self.stack[-1])
        elif kind == InstrKind.Load:
            self._check_stack_depth(1)
            addr = self._pop()
            self._check_mem_addr(addr)
            val = self.mem[addr]
            self._push(val)
        elif kind == InstrKind.Store:
            self._check_stack_depth(2)
            addr = self._pop()
            self._check_mem_addr(addr)
            val = self._pop()
            self._check_mem_val(val)
            self.mem[addr] = val
        elif kind == InstrKind.Add:
            self._check_stack_depth(2)
            a = self._pop()
            b = self._pop()
            self._push(b + a)
        elif kind == InstrKind.Sub:
            self._check_stack_depth(2)
            a = self._pop()
            b = self._pop()
            self._push(b - a)
        elif kind == InstrKind.Shl:
            self._check_stack_depth(2)
            i = self._pop()
            val = self._pop()
            self._push(val << i)
        elif kind == InstrKind.Shr:
            self._check_stack_depth(2)
            i = self._pop()
            val = self._pop()
            self._push(val >> i)
        elif kind == InstrKind.And:
            self._check_stack_depth(2)
            val_a = self._pop()
            val_b = self._pop()
            self._push(val_a & val_b)
        elif kind == InstrKind.Or:
            self._check_stack_depth(2)
            val_a = self._pop()
            val_b = self._pop()
            self._push(val_a | val_b)
        elif kind == InstrKind.Call:
            self._check_pc(arg)
            self._push(self.pc)
            self.pc = arg
        elif kind == InstrKind.Ret:
            self._check_stack_depth(1)
            addr = self._pop()
            self._check_pc(addr)
            self.pc = addr
        elif kind == InstrKind.St:
            self._check_stack_depth(2)
            a = self._pop()
            b = self._pop()
            self._push(int(b < a))
        elif kind == InstrKind.Jmp:
            self._check_pc(arg)
            self.pc = arg
        elif kind == InstrKind.JmpF:
            self._check_stack_depth(1)
            guard = self._pop()
            if guard == 0:
                self._check_pc(arg)
                self.pc = arg
        else:
            raise NotImplementedError
        self.pc += 1

    def loop(self) -> Val:
        while not self.halted:
            self.step()
        return self._pop()

    def dbg(self, fmt: Callable[[Optional[int]],
            Union[str, int]] = str) -> Val:
        while not self.halted:
            instr = self.program[self.pc]
            pc_s = f'{fmt(self.pc):5} '
            instr_s = f'{instr.kind.name:6} '
            arg_s = f'{fmt(instr.arg) if instr.arg is not None else ""}'
            vals_s = [f"{fmt(v):3}" for v in self.stack]
            stack_s = f'      |{" ".join(vals_s)}\n'
            print(stack_s + pc_s + instr_s + arg_s)
            while True:
                inp = input()
                if not inp:
                    break
                else:
                    addr = int(inp)
                    print(f'mem[{addr}] = {self.mem[addr]}')
            self.step()
        return self._pop()

    def _check_pc(self, pc: Optional[int] = None) -> None:
        pc = pc if pc is not None else self.pc
        if not 0 <= pc < len(self.program):
            raise VMError(self, f'Invalid pc value: {pc}')

    def _check_mem_addr(self, addr: Val) -> None:
        if not 0 <= addr < len(self.mem):
            raise VMError(self, f'Invalid mem addr: {addr}')

    def _check_mem_val(self, val: Val) -> None:
        if not 0 <= val <= 0xFF:
            raise VMError(self, f'Invalid mem val: {val}')

    def _check_running(self) -> None:
        if self.halted:
            raise VMError(self, 'VM is halted')

    def _check_stack_depth(self, n: int) -> None:
        if len(self.stack) < n:
            raise VMError(self, f'Expected at least {n} items on stack, found '
                          f'{len(self.stack)}')

    def _push(self, val: Val) -> 'VM':
        self.stack.append(val)
        return self

    def _pop(self) -> Val:
        return self.stack.pop()
