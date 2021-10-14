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


@dataclass
class LeafNode:
    token: Token


@dataclass
class Var(LeafNode):
    name: str


@dataclass
class Int(LeafNode):
    value: int


@dataclass
class Lit:
    child: Union[Int]


@dataclass
class FnCall:
    name: str
    args: List['Expr']


@dataclass
class FnDef:
    name: str
    arg_names: List[str]
    stmt: 'Stmt'


@dataclass
class Assign:
    name: str
    expr: 'Expr'


@dataclass
class VarDecl:
    name: str


@dataclass
class Expr:
    child: Union[Lit, Var, FnCall]


@dataclass
class WhileLoop:
    guard: 'Expr'
    body: 'Stmt'


@dataclass
class Block:
    children: List['Stmt']


@dataclass
class Stmt:
    # TODO: Create Node that contains Union[Stmt, FnDef, VarDecl]
    child: Union[Block, Expr, FnDef, WhileLoop, VarDecl, Var, Assign]


Node = Union[Stmt, Block, Expr, Lit, Int, Var, FnCall, FnDef, WhileLoop,
             VarDecl, Assign]
