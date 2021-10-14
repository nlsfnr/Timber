# flake8: noqa
from common import Token
from lexer import lex
from parser import parse
from gen import gen
from util import fmt_node
from vm import VM, Program, Instr, InstrKind


def main_1():
    with open('sample.timber', 'r') as fh:
        src = fh.read()
    tokens = lex(src)
    node = parse(tokens)
    print(fmt_node(node))
    unit = gen(node)
    print(unit)
    prog = unit.to_program()
    vm = VM(prog)
    vm.dbg()


def main_2():
    program = Program()
    (program
        # n
        .push(Instr(InstrKind.Push, 10))  # 0
        .push(Instr(InstrKind.Push, 0))
        .push(Instr(InstrKind.Store))

        # a
        .push(Instr(InstrKind.Push, 0))  # 3
        .push(Instr(InstrKind.Push, 1))
        .push(Instr(InstrKind.Store))

        # b
        .push(Instr(InstrKind.Push, 1))  # 6
        .push(Instr(InstrKind.Push, 2))
        .push(Instr(InstrKind.Store))

        .push(Instr(InstrKind.Call, 11)) # 9
        .push(Instr(InstrKind.Push, 0))
        .push(Instr(InstrKind.Halt))

        # Fib
        .push(Instr(InstrKind.Push, 0))  # 12
        .push(Instr(InstrKind.Load))
        .push(Instr(InstrKind.Dup))
        .push(Instr(InstrKind.Push, 1))
        .push(Instr(InstrKind.St))
        .push(Instr(InstrKind.JmpF, program.here + 3))
        .push(Instr(InstrKind.Pop))
        .push(Instr(InstrKind.Pop))
        .push(Instr(InstrKind.Ret))
        .push(Instr(InstrKind.Push, 1))
        .push(Instr(InstrKind.Load))
        .push(Instr(InstrKind.Dup))
        .push(Instr(InstrKind.Push, 2))
        .push(Instr(InstrKind.Load))
        .push(Instr(InstrKind.Add))
        .push(Instr(InstrKind.Push, 1))
        .push(Instr(InstrKind.Store))
        .push(Instr(InstrKind.Push, 2))
        .push(Instr(InstrKind.Store))
        .push(Instr(InstrKind.Push, 1))
        .push(Instr(InstrKind.Sub))
        .push(Instr(InstrKind.Push, 0))
        .push(Instr(InstrKind.Store))
        .push(Instr(InstrKind.Call, 11))
        .push(Instr(InstrKind.Ret))
    )
    vm = VM(program)
    vm.loop()
    print(vm.mem[0], vm.mem[1], vm.mem[2])


if __name__ == '__main__':
    main_1()
