from common import Token, fmt_node
from lexer import lex
from parser import parse


def main():
    with open('sample.timber', 'r') as fh:
        src = fh.read()
    tokens = lex(src)
    print(Token.fmt_many(tokens))
    node = parse(tokens)
    print(fmt_node(node))


if __name__ == '__main__':
    main()
