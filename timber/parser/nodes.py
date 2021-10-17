from dataclasses import dataclass
from typing import List, Union, Tuple


@dataclass
class Node:
    span: Tuple[int, int]


@dataclass
class IntLit(Node):
    value: int


@dataclass
class StrLit(Node):
    value: str


@dataclass
class Lit(Node):
    child: Union[IntLit, StrLit]


@dataclass
class InfixFnCall(Node):
    name: str
    arg_1: 'Expr'
    arg_2: 'Expr'


@dataclass
class DefaultFnCall(Node):
    name: str
    args: List['Expr']


@dataclass
class FnCall(Node):
    child: Union[DefaultFnCall, InfixFnCall]


@dataclass
class ReturnStmt(Node):
    child: 'Expr'


@dataclass
class Assign(Node):
    name: str
    expr: 'Expr'


@dataclass
class WhileStmt(Node):
    guard: 'Expr'
    body: 'Block'


@dataclass
class IfStmt(Node):
    guard: 'Expr'
    body: 'Block'


@dataclass
class Var(Node):
    name: str


@dataclass
class Expr(Node):
    # Recursive case is for parenthesis around expr for precedence in infix
    # notation. Not collapsing this into a flat expression maintains that
    # information.
    child: Union[FnCall, Var, Lit, 'Expr', Assign]


@dataclass
class Block(Node):
    var_decls: List['VarDecl']
    stmts: List['Stmt']


@dataclass
class VarDecl(Node):
    name: str


@dataclass
class FnDef(Node):
    name: str
    arg_decls: List[VarDecl]
    body: Block


@dataclass
class SimpleStmt(Node):
    child: Union[ReturnStmt, Expr]


@dataclass
class CompountStmt(Node):
    child: Union[WhileStmt, IfStmt, Block]


@dataclass
class Stmt(Node):
    child: Union[CompountStmt, SimpleStmt]


@dataclass
class Program(Node):
    var_decls: List[VarDecl]
    fn_defs: List[FnDef]
