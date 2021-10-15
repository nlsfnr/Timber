#!/usr/bin/env python3
import argparse
from pathlib import Path

from timber import vm, parser, lexer


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



if __name__ == '__main__':
    main()
