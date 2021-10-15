#!/usr/bin/env python3
# flake8: noqa
import argparse
from pathlib import Path

from common import Token
from lexer import lex
from parser import parse
from gen import gen
from util import fmt_node
from vm import VM, Program, Instr, InstrKind


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', metavar='CMD', type=str,
                        choices=['run', 'dbg', 'asm', 'ast', 'lex'])
    parser.add_argument('file', metavar='FILE', type=Path)
    args = parser.parse_args()

    file = args.file
    assert file.exists()

    with open(file, 'r') as fh:
        src = fh.read()

    if args.cmd == 'run':
        tokens = lex(src)
        node = parse(tokens)
        unit = gen(node)
        prog = unit.to_program()
        vm = VM(prog)
        vm.loop()

    elif args.cmd == 'dbg':
        tokens = lex(src)
        node = parse(tokens)
        unit = gen(node)
        prog = unit.to_program()
        vm = VM(prog)
        vm.dbg()

    elif args.cmd == 'asm':
        tokens = lex(src)
        node = parse(tokens)
        unit = gen(node)
        print(unit)

    elif args.cmd == 'ast':
        tokens = lex(src)
        node = parse(tokens)
        print(fmt_node(node))

    elif args.cmd == 'lex':
        tokens = lex(src)
        print(Token.fmt_many(tokens))


if __name__ == '__main__':
    main()
