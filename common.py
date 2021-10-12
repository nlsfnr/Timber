from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Union, Optional


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

    @classmethod
    def from_str(cls, s: str) -> Optional['Keyword']:
        return {
            'def': cls.FnDef,
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
class Expr:
    child: Union[Lit, Var, FnCall]


@dataclass
class Block:
    children: List['Stmt']


@dataclass
class Stmt:
    child: Union[Block, Expr, FnDef]


Node = Union[Stmt, Block, Expr, Lit, Int, Var, FnCall, FnDef]


def fmt_node(node: Node) -> str:
    return _fmt_node(node, 0)


def _fmt_node(node: Node, lvl: int) -> str:
    padding = '  ' * lvl
    if isinstance(node, Stmt):
        return padding + f'Stmt\n{_fmt_node(node.child, lvl + 1)}'
    if isinstance(node, Block):
        stmts = '\n'.join([_fmt_node(stmt, lvl + 1) for stmt in node.children])
        return padding + f'Block\n{stmts}'
    if isinstance(node, Expr):
        return padding + f'Expr\n{_fmt_node(node.child, lvl + 1)}'
    if isinstance(node, FnDef):
        names = ', '.join(map(str, node.arg_names))
        return padding + (f'FnDef {node.name}({names})\n'
                          f'{_fmt_node(node.stmt, lvl + 1)}')
    if isinstance(node, FnCall):
        exprs = '\n'.join([_fmt_node(expr, lvl + 1)
                           for expr in node.args])
        return padding + (f'FnCall {node.name}\n{exprs}')
    if isinstance(node, Lit):
        return padding + f'Lit\n{_fmt_node(node.child, lvl + 1)}'
    if isinstance(node, Int):
        return padding + f'Int {node.value}'
    if isinstance(node, Var):
        return padding + f'Var {node.name}'
