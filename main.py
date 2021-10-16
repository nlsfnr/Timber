#!/usr/bin/env python3
import argparse
from pathlib import Path

from timber import vm, parser, lexer, codegen


def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('cmd', metavar='CMD', type=str,
                        choices=['run', 'dbg', 'asm', 'ast', 'lex', 'tmp'])
    arg_parser.add_argument('file', metavar='FILE', type=Path)
    args = arg_parser.parse_args()

    file = args.file
    assert file.exists()

    with open(file, 'r') as fh:
        src = fh.read()

    if args.cmd == 'ast':
        tokens = lexer.lex(src)
        ast = parser.parse_program(tokens)
        print(parser.fmt_node(ast))

    if args.cmd == 'lex':
        tokens = lexer.lex(src)
        print(lexer.Token.fmt_many(tokens))

    if args.cmd == 'asm':
        tokens = lexer.lex(src)
        ast = parser.parse_program(tokens)
        unit = codegen.gen_program(ast).link()
        print(unit)

    if args.cmd == 'dbg':
        tokens = lexer.lex(src)
        ast = parser.parse_program(tokens)
        unit = (codegen
                .gen_program(ast)
                .runnable()
                .builtins()
                .link())
        m = vm.VM(unit.ops)
        m.dbg()

    if args.cmd == 'tmp':
        from timber.codegen import codegen as cg

        tokens = lexer.lex(src)
        ast = parser.parse_program(tokens)

        fn_def = ast.fn_defs[0]
        unit = cg.gen_fn_def(fn_def, dict())
        print(fn_def)
        print(cg.stack_required(fn_def))

if __name__ == '__main__':
    main()
