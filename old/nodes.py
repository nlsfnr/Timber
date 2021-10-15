

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
