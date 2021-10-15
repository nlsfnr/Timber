import string
from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Optional, Union


class TokenKind(Enum):
    Whitespace = auto()
    Comma = auto()
    Eq = auto()
    Plus = auto()
    LParen = auto()
    RParen = auto()
    LBrack = auto()
    RBrack = auto()
    LBrace = auto()
    RBrace = auto()
    Excl = auto()
    Semi = auto()
    Word = auto()
    Keyword = auto()
    Int = auto()

    def __str__(self) -> str:
        return self.name


class Keyword(Enum):
    FnDef = auto()
    While = auto()
    If = auto()
    Var = auto()
    Return = auto()

    @classmethod
    def from_str(cls, s: str) -> Optional['Keyword']:
        return {
            'def': cls.FnDef,
            'while': cls.While,
            'if': cls.If,
            'var': cls.Var,
            'return': cls.Return,
        }.get(s, None)

    def __str__(self) -> str:
        return self.name


TokenValue = Optional[Union[int, str, Keyword]]


@dataclass
class Token:
    kind: TokenKind
    index: int
    value: TokenValue

    def __str__(self) -> str:
        return f'Token({self.index} {self.kind} {self.value})'

    def __repr__(self) -> str:
        return str(self)

    @staticmethod
    def fmt_many(tokens: List['Token']) -> str:
        return '\n'.join([f'{token.index:03} {token.kind:7} {token.value}'
                          for addr, token in enumerate(tokens)])


SINGLE_CHAR_TOKENS = {
    ',': TokenKind.Comma,
    '(': TokenKind.LParen,
    ')': TokenKind.RParen,
    '[': TokenKind.LBrack,
    ']': TokenKind.RBrack,
    '{': TokenKind.LBrace,
    '}': TokenKind.RBrace,
    ';': TokenKind.Semi,
}

MULTI_CHAR_TOKENS = (
    (string.ascii_letters + '_+-=*/<>%!', TokenKind.Word, str),
    (string.digits, TokenKind.Int, int),
)


class LexingError(Exception):
    pass


def peek(src: str, i: int, d: int) -> Optional[str]:
    return src[i + d] if i + d < len(src) else None


def consume(src: str, i: int, chars: str) -> int:
    j = i
    while j < len(src) and src[j] in chars:
        j += 1
    return j - i


def lex(src: str) -> List[Token]:
    i = 0
    tokens: List[Token] = []
    while i < len(src):
        c = peek(src, i, 0)
        if c is None:
            break
        elif c == '#':
            while src[i] != '\n' and i < len(src):
                i += 1
        elif c in string.whitespace:
            i += 1
            continue
        elif c in SINGLE_CHAR_TOKENS:
            token_kind = SINGLE_CHAR_TOKENS[c]
            tokens.append(Token(token_kind, i, None))
            i += 1
        else:
            for chars, token_kind, post_processor in MULTI_CHAR_TOKENS:
                if c not in chars:
                    continue
                length = consume(src, i, chars)
                value = post_processor(src[i:i + length])
                tokens.append(Token(token_kind, i, value))
                i += length
                break
            else:
                raise LexingError(f'Unknown symbol: {c}')
    for token in tokens:
        if token.kind == TokenKind.Word:
            assert isinstance(token.value, str)
            kw = Keyword.from_str(token.value)
            if kw is None:
                continue
            token.kind = TokenKind.Keyword
            token.value = kw
    return tokens
