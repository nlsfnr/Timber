from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Union, Optional, Type


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
    Var = auto()

    @classmethod
    def from_str(cls, s: str) -> Optional['Keyword']:
        return {
            'def': cls.FnDef,
            'while': cls.While,
            'var': cls.Var,
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
