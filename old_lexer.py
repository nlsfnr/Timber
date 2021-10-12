import string
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Union, Tuple


class TType(Enum):
    Word = auto()
    IntLit = auto()
    Excl = auto()
    LParen = auto()
    RParen = auto()
    LBrack = auto()
    RBrack = auto()
    Plus = auto()

    def __str__(self):
        return self.name


COMMENT_DELIM = '#'
IDENT_CHARS = string.ascii_letters + '_+-*/='
TTYPE_MAP = {
    '!': TType.Excl,
    '(': TType.LParen,
    ')': TType.RParen,
    '{': TType.LBrack,
    '}': TType.RBrack,
}


@dataclass
class Token:
    typ: TType
    val: Optional[Union[str, int]]
    span: slice

    def __str__(self) -> str:
        return f'Token({self.typ}, {self.val})'

    def __repr__(self) -> str:
        return str(self)


def _eat(chars: str, src: str, i: int) -> Tuple[int, int]:
    j = i
    while src[j] in chars:
        j += 1
    return i, j


def lex(src: str) -> List[Token]:
    tokens: List[Token] = []
    i: int = 0
    while i < len(src):
        if src[i] in string.whitespace:
            i += 1
        elif src[i] == COMMENT_DELIM:
            while i < len(src) and src[i] != '\n':
                i += 1
        elif src[i] in IDENT_CHARS:
            s, i = _eat(IDENT_CHARS, src, i)
            token = Token(typ=TType.Word, val=src[s:i], span=slice(s, i))
            tokens.append(token)
        elif src[i] in string.digits:
            s, i = _eat(string.digits, src, i)
            val = int(src[s:i])
            token = Token(typ=TType.IntLit, val=val, span=slice(s, i))
            tokens.append(token)
        elif src[i] in TTYPE_MAP:
            typ = TTYPE_MAP[src[i]]
            token = Token(typ=typ, val=src[i], span=slice(i, i + 1))
            tokens.append(token)
            i += 1
        else:
            raise NotImplementedError(f"Unknown char at {i = }: {src[i]}")
    return tokens


def main():
    from pprint import pprint

    with open('syntax.tr', 'r') as fh:
        src = fh.read()
    tokens = lex(src)
    pprint(tokens)


if __name__ == '__main__':
    main()
