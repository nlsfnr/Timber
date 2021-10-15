from dataclasses import dataclass
from typing import List, Union, Tuple


@dataclass
class Node:
    span: Tuple[int, int]


@dataclass
class IntLit(Node):
    value: int


@dataclass
class Lit(Node):
    child: Union[IntLit]


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
    child: Union[FnCall, Var, Lit]


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
    child: Union[WhileStmt, IfStmt]


@dataclass
class Stmt(Node):
    child: Union[CompountStmt, SimpleStmt]


@dataclass
class Program(Node):
    var_decls: List[VarDecl]
    fn_defs: List[FnDef]
