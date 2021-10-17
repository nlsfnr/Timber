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
        unit = (codegen
                .gen_program(ast)
                .entrypoint()
                .builtins()
                .link())
        print(unit)

    if args.cmd == 'dbg':
        tokens = lexer.lex(src)
        ast = parser.parse_program(tokens)
        runnable = (codegen
                    .gen_program(ast)
                    .entrypoint()
                    .builtins()
                    .link()
                    .runnable())
        m = runnable.vm()
        m.dbg()

    if args.cmd == 'run':
        tokens = lexer.lex(src)
        ast = parser.parse_program(tokens)
        runnable = (codegen
                    .gen_program(ast)
                    .entrypoint()
                    .builtins()
                    .link()
                    .runnable())
        m = runnable.vm()
        m.run()

    if args.cmd == 'tmp':
        c = codegen.codegen.Context(100)
        c.str_lit('asas')
        c.str_lit('sdsjd  sjsjs   sjsjsjsj')
        c.str_lit('asd')
        print(c._str_addr_offset)
        print(c._str_addrs)
        mem = c.build_mem(1024)
        print(mem[0:40])

if __name__ == '__main__':
    main()
