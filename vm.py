from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List


MWord = int
MWORD_SIZE = 4


def to_ptr(ptr: MWord) -> MWord:
    return ptr * MWORD_SIZE


MEM_CAPACITY = to_ptr(8)
STACK_PTR = to_ptr(4)

'''
TOS = 0

Push   97
VStore 1
Push   98
VStore 2
Push   99
VStore 3
[_, 97, 98, 99]
Call   fn
[rv, 97, 98, 99]

fn(a, b, c) {
    VIncr 5     vstack = [rv, a, b, c, d, _], vtos = 5
    VLoad -4    a
    VLoad -3
    VLoad -2
    Add
    Add         stack = [a + b + c]
    VDecr 5
    Ret
}
[]
 ^

'''

class VMError(Exception):
    pass


class OpKind(Enum):
    Halt = auto()
    # Stack operations
    Push = auto()
    Pop = auto()
    Rot = auto()
    # VStack operations
    VLoad = auto()      # stack.push(vstack[vtos + arg])
    VStore = auto()     # vstack[vtos + arg] = stack[-1]
    VIncr = auto()      # vtos += arg * MWORD_SIZE
    VDecr = auto()      # vtos -= arg * MWORD_SIZE
    # Control flow
    Call = auto()       # vstack[vtos] = PC; PC = arg
    Ret = auto()        # PC = vstack[vtos]
    Jmp = auto()        # PC = arg
    JmpZ = auto()       # PC = arg if stack[-1] == 0
    # Arithmetic
    Add = auto()
    Sub = auto()
    Shl = auto()
    Shr = auto()
    And = auto()
    Or = auto()
    # Memory
    Load = auto()       # x <- stack[-1]; stack.push(mem[x:x+MWORD_SIZE])
    Store = auto()      # x <- stack[-1]; mem[x:x+MWORD_SIZE] = stack[-2]


@dataclass
class Op:
    kind: OpKind
    arg: MWord


@dataclass
class VM:
    ops: List[Op]
    pc: MWord = 0
    vtos: MWord = STACK_PTR
    stack: List[MWord] = field(default_factory=list)
    mem: bytearray = field(default_factory=lambda: bytearray(MEM_CAPACITY))
    halted: bool = False

    def step(self) -> 'VM':
        assert 0 <= self.pc < len(self.ops)
        op = self.ops[self.pc]
        kind = op.kind
        arg = op.arg

        if kind == OpKind.Halt:
            self.halted = True
            return

        # Stack
        elif kind == OpKind.Push:
            self.stack.append(arg)
        elif kind == OpKind.Pop:
            self._needs_stack_depth(1)
            self.stack.pop()
        elif kind == OpKind.Rot:
            self._needs_stack_depth(2)
            self.stack[-1], self.stack[2] = self.stack[-2], self.stack[-1]

        # Arithmetic
        elif kind == OpKind.Add:
            self._needs_stack_depth(2)
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a + b)
        elif kind == OpKind.Sub:
            self._needs_stack_depth(2)
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a - b)
        elif kind == OpKind.And:
            self._needs_stack_depth(2)
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a & b)
        elif kind == OpKind.Or:
            self._needs_stack_depth(2)
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a | b)
        elif kind == OpKind.Shl:
            self._needs_stack_depth(2)
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a << b)
        elif kind == OpKind.Shr:
            self._needs_stack_depth(2)
            b, a = self.stack.pop(), self.stack.pop()
            self.stack.append(a >> b)

        # VStack
        elif kind == OpKind.VLoad:
            ptr = self.vtos + arg
            val = self._load_mword(ptr)
            self.stack.append(val)
        elif kind == OpKind.VStore:
            self._needs_stack_depth(1)
            ptr = self.vtos + arg
            val = self.stack.pop()
            self._store_mword(ptr, val)
        elif kind == OpKind.VIncr:
            self.vtos += arg
        elif kind == OpKind.VDecr:
            self.vtos -= arg

        # Control flow
        elif kind == OpKind.Call:
            self._check_pc(arg)
            self._store_mword(self.vtos, self.pc)
            self.pc = arg
        elif kind == OpKind.Ret:
            pc = self._load_mword(self.vtos)
            self._check_pc(pc)
            self.pc = pc
        elif kind == OpKind.Jmp:
            self._needs_stack_depth(1)
            self._check_pc(arg)
            self.pc = arg
        elif kind == OpKind.JmpZ:
            self._needs_stack_depth(1)
            self._check_pc(arg)
            guard = self.stack.pop()
            if guard == 0:
                self.pc = arg

        # Memory
        elif kind == OpKind.Load:
            self._needs_stack_depth(1)
            ptr = self.stack.pop()
            val = self._load_mword(ptr)
            self.stack.append(val)
        elif kind == OpKind.Store:
            self._needs_stack_depth(2)
            ptr = self.stack.pop()
            val = self.stack.pop()
            self._store_mword(ptr, val)

        else:
            raise NotImplementedError
        self.pc += 1
        return self

    def run(self) -> 'VM':
        while not self.halted:
            self.step()
        return self

    def dbg(self) -> 'VM':
        while not self.halted:
            stack_items = ' '.join(map(str, self.stack))
            op = self.ops[self.pc]
            print(f'|{stack_items}')
            print(f'{op.kind.name:7} {op.arg:3}{"":6}', end='')
            while True:
                inp = input()
                if not inp:
                    break
                ptr = to_ptr(int(inp))
                print(f'mem[{ptr}] = {self._load_mword(ptr)}')
            self.step()

    def _needs_stack_depth(self, depth: int) -> None:
        if len(self.stack) < depth:
            op = self.ops[self.pc]
            raise VMError(f'{op.kind.name} @ {self.pc} Expected at least '
                          f'{depth} items on stack, got {len(self.stack)}')

    def _load_mword(self, ptr: MWord) -> MWord:
        self._check_ptr(ptr)
        val = 0
        for i in range(MWORD_SIZE):
            byte = self.mem[ptr + i]
            val += byte << (i * 8)
        return val

    def _store_mword(self, ptr: MWord, val: MWord) -> None:
        self._check_ptr(ptr)
        for i in range(MWORD_SIZE):
            sh = i * 8
            byte = (val & (0xFF << sh)) >> sh
            self.mem[ptr + i] = byte

    def _check_ptr(self, ptr: MWord) -> None:
        if ptr == 0:
            raise VMError(f'Tried to dereference a NULL pointer')
        if not 0 <= ptr < len(self.mem) - MWORD_SIZE:
            raise VMError(f'Memory ptress out of bounds: {ptr}')
        if ptr % MWORD_SIZE != 0:
            raise VMError(f'Misaligned memory ptress: {ptr}')

    def _check_pc(self, pc: MWord) -> None:
        if not 0 <= pc < len(self.ops):
            raise VMError(f'Invalid pc value: {pc}')
