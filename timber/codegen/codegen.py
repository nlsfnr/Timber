from uuid import uuid4
from functools import reduce
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from ..parser.nodes import (VarDecl, FnDef, Block, Stmt, CompountStmt,
                            SimpleStmt, Expr, WhileStmt, IfStmt, FnCall, Var,
                            Lit, IntLit, InfixFnCall, Program, DefaultFnCall,
                            Assign, ReturnStmt, Node)
from ..vm import MWord, Op, OpKind, to_ptr


_DUMMY_ADDR = 0


class CodegenError(Exception):
    pass


@dataclass
class Unit:
    ops: List[Op] = field(default_factory=list)
    target_addrs: Dict[str, int] = field(default_factory=dict)
    jmp_addrs: Dict[int, str] = field(default_factory=dict)

    def target_addr(self, name: str) -> 'Unit':
        self.target_addrs[name] = len(self.ops)
        return self

    def jmp_addr(self, name: str) -> 'Unit':
        # Assumes that the jmp_addr is called _before_ the jmp op is added
        self.jmp_addrs[len(self.ops)] = name
        return self

    def __add_op(self, kind: OpKind, arg: MWord) -> 'Unit':
        self.ops.append(Op(kind, arg))
        return self

    def halt(self) -> 'Unit':
        return self.__add_op(OpKind.Halt, 0)

    def push(self, arg: MWord) -> 'Unit':
        return self.__add_op(OpKind.Push, arg)

    def pop(self) -> 'Unit':
        return self.__add_op(OpKind.Pop, 0)

    def rot(self) -> 'Unit':
        return self.__add_op(OpKind.Rot, 0)

    def dup(self) -> 'Unit':
        return self.__add_op(OpKind.Dup, 0)

    def v_load(self, arg: MWord) -> 'Unit':
        return self.__add_op(OpKind.VLoad, arg)

    def v_store(self, arg: MWord) -> 'Unit':
        return self.__add_op(OpKind.VStore, arg)

    def v_incr(self, arg: MWord) -> 'Unit':
        return self.__add_op(OpKind.VIncr, arg)

    def v_decr(self, arg: MWord) -> 'Unit':
        return self.__add_op(OpKind.VDecr, arg)

    def call(self, arg: MWord) -> 'Unit':
        return self.__add_op(OpKind.Call, arg)

    def ret(self) -> 'Unit':
        return self.__add_op(OpKind.Ret, 0)

    def jmp(self, arg: MWord) -> 'Unit':
        return self.__add_op(OpKind.Jmp, arg)

    def jmp_z(self, arg: MWord) -> 'Unit':
        return self.__add_op(OpKind.JmpZ, arg)

    def jmp_nz(self, arg: MWord) -> 'Unit':
        return self.__add_op(OpKind.JmpNZ, arg)

    def add(self) -> 'Unit':
        return self.__add_op(OpKind.Add, 0)

    def sub(self) -> 'Unit':
        return self.__add_op(OpKind.Sub, 0)

    def shl(self) -> 'Unit':
        return self.__add_op(OpKind.Shl, 0)

    def shr(self) -> 'Unit':
        return self.__add_op(OpKind.Shr, 0)

    def and_(self) -> 'Unit':
        return self.__add_op(OpKind.And, 0)

    def or_(self) -> 'Unit':
        return self.__add_op(OpKind.Or, 0)

    def load(self) -> 'Unit':
        return self.__add_op(OpKind.Load, 0)

    def store(self) -> 'Unit':
        return self.__add_op(OpKind.Store, 0)

    def extend(self, units: List['Unit']) -> 'Unit':
        return reduce(self.__class__.append, units, self)

    def append(self, unit: 'Unit') -> 'Unit':
        addr_offset = len(self.ops)
        offset_target_addrs = {name: addr + addr_offset
                               for name, addr in unit.target_addrs.items()}
        offset_jmp_addrs = {addr + addr_offset: name
                            for addr, name in unit.jmp_addrs.items()}
        self.target_addrs.update(offset_target_addrs)
        self.jmp_addrs.update(offset_jmp_addrs)
        self.ops.extend(unit.ops)
        return self

    def runnable(self) -> 'Unit':
        return (self.__class__()
                .jmp_addr('main')
                .call(_DUMMY_ADDR)
                .halt()
                .append(self))

    def builtins(self) -> 'Unit':
        return (self
                .target_addr('add')
                .v_load(to_ptr(1))
                .v_load(to_ptr(2))
                .add()
                .ret()
                .target_addr('sub')
                .v_load(to_ptr(1))
                .v_load(to_ptr(2))
                .sub()
                .ret())

    def link(self) -> 'Unit':
        for addr, name in self.jmp_addrs.items():
            if name not in self.target_addrs:
                raise CodegenError(f'Unknown target_addr: {name}')
            op = self.ops[addr]
            assert op.kind in [OpKind.Jmp, OpKind.JmpNZ, OpKind.JmpZ,
                               OpKind.Call]
            assert op.arg == _DUMMY_ADDR
            op.arg = self.target_addrs[name] - 1
        return self

    def __str__(self) -> str:
        s = ''
        fn_map = {addr: name for name, addr in self.target_addrs.items()}
        for i, op in enumerate(self.ops):
            s += f'{i:03} {str(op):18}'
            if i in fn_map:
                s += f'{fn_map[i]}'
            s += '\n'
        return s


@dataclass
class Context:
    stack_ptr_offset: MWord


@dataclass
class Namespace:
    _globals: Dict[str, int]
    _parent: Optional['Namespace'] = None
    _indices: Dict[str, int] = field(default_factory=dict)

    def push_block(self) -> 'Namespace':
        return Namespace(self._globals, self)

    def set_var_decls(self, var_decls: List[VarDecl]) -> None:
        assert len(self._indices) == 0
        height = self.height()
        for idx, var_decl in enumerate(var_decls):
            name = var_decl.name
            if name in self._indices:
                raise CodegenError(f'Duplicate names: {name}')
            self._indices[name] = idx + height

    def get_indices(self) -> Dict[str, int]:
        indices = dict(self._indices)
        if self._parent:
            indices.update(self._parent.get_indices())
        return indices

    def get_index(self, name: str) -> Optional[int]:
        if name in self._indices:
            return self._indices[name]
        if not self._parent:
            return None
        return self._parent.get_index(name)

    def height(self) -> int:
        height = self._parent.height() if self._parent else 0
        return height + len(self._indices)

    def get_offset(self, name: str, ctx: Context) -> int:
        idx = self.get_index(name)
        if idx is None:
            # TODO: Check globals
            a = ', '.join(self._indices.keys())
            raise CodegenError(f'Unknown identifier: {name}, available: {a}')
        return to_ptr(1 + idx) - ctx.stack_ptr_offset


def gen(n: Node) -> Unit:
    pass


def gen_program(n: Program) -> Unit:
    globals_: Dict[str, MWord] = {var_decl.name: idx
                                  for idx, var_decl in enumerate(n.var_decls)}
    return Unit().extend([gen_fn_def(fn_def, globals_)
                          for fn_def in n.fn_defs])


def gen_fn_def(n: FnDef, globals_: Dict[str, MWord]) -> Unit:
    ns = Namespace(globals_)
    ns.set_var_decls(n.arg_decls)
    ctx = Context(stack_required(n) + to_ptr(1))
    unit = Unit().target_addr(n.name)
    return (unit
            .v_incr(ctx.stack_ptr_offset)
            .append(gen_block(n.body, ns, ctx))
            .v_decr(ctx.stack_ptr_offset)
            .ret())


def gen_block(n: Block, ns: Namespace, ctx: Context) -> Unit:
    ns = ns.push_block()
    ns.set_var_decls(n.var_decls)
    return Unit().extend([gen_stmt(s, ns, ctx) for s in n.stmts])


def gen_stmt(n: Stmt, ns: Namespace, ctx: Context) -> Unit:
    child = n.child
    if isinstance(child, CompountStmt):
        return gen_compound_stmt(child, ns, ctx)
    elif isinstance(child, SimpleStmt):
        return gen_simple_stmt(child, ns, ctx)


def gen_compound_stmt(n: CompountStmt, ns: Namespace, ctx: Context) -> Unit:
    child = n.child
    if isinstance(child, WhileStmt):
        return gen_while_stmt(child, ns, ctx)
    if isinstance(child, IfStmt):
        return gen_if_stmt(child, ns, ctx)
    if isinstance(child, Block):
        return gen_block(child, ns, ctx)


def gen_simple_stmt(n: SimpleStmt, ns: Namespace, ctx: Context) -> Unit:
    child = n.child
    if isinstance(child, ReturnStmt):
        return gen_return_stmt(child, ns, ctx)
    elif isinstance(child, Expr):
        return gen_expr(child, ns, ctx).pop()


def gen_expr(n: Expr, ns: Namespace, ctx: Context) -> Unit:
    child = n.child
    if isinstance(child, FnCall):
        return gen_fn_call(child, ns, ctx)
    elif isinstance(child, Var):
        return gen_var(child, ns, ctx)
    elif isinstance(child, Lit):
        return gen_lit(child, ns, ctx)
    elif isinstance(child, Expr):
        return gen_expr(child, ns, ctx)
    elif isinstance(child, Assign):
        return gen_assign(child, ns, ctx)


def gen_fn_call(n: FnCall, ns: Namespace, ctx: Context) -> Unit:
    child = n.child
    if isinstance(child, DefaultFnCall):
        return gen_default_fn_call(child, ns, ctx)
    elif isinstance(child, InfixFnCall):
        return gen_infix_fn_call(child, ns, ctx)


def gen_default_fn_call(n: DefaultFnCall, ns: Namespace, ctx: Context) -> Unit:
    arg_exprs = [gen_expr(expr, ns, ctx) for expr in n.args]
    arg_exprs_with_vstore = [e.v_store(to_ptr(i + 1))
                             for i, e in enumerate(arg_exprs)]
    arg_setup = Unit().extend(arg_exprs_with_vstore)
    return arg_setup.jmp_addr(n.name).call(_DUMMY_ADDR)


def gen_infix_fn_call(n: InfixFnCall, ns: Namespace, ctx: Context) -> Unit:
    raise NotImplementedError


def gen_var(n: Var, ns: Namespace, ctx: Context) -> Unit:
    return Unit().v_load(ns.get_offset(n.name, ctx))


def gen_assign(n: Assign, ns: Namespace, ctx: Context) -> Unit:
    expr = gen_expr(n.expr, ns, ctx)
    return Unit().append(expr).dup().v_store(ns.get_offset(n.name, ctx))


def gen_while_stmt(n: WhileStmt, ns: Namespace, ctx: Context) -> Unit:
    guard_expr = gen_expr(n.guard, ns, ctx)
    body = gen_block(n.body, ns, ctx)
    guard_name = str(uuid4())
    start_name = str(uuid4())
    return (Unit()
            .jmp_addr(guard_name)
            .jmp(_DUMMY_ADDR)
            .target_addr(start_name)
            .append(body)
            .target_addr(guard_name)
            .append(guard_expr)
            .jmp_addr(start_name)
            .jmp_nz(_DUMMY_ADDR))


def gen_if_stmt(n: IfStmt, ns: Namespace, ctx: Context) -> Unit:
    raise NotImplementedError


def gen_return_stmt(n: ReturnStmt, ns: Namespace, ctx: Context) -> Unit:
    expr = gen_expr(n.child, ns, ctx)
    return (Unit()
            .append(expr)
            .v_decr(ctx.stack_ptr_offset)
            .ret())


def gen_int_lit(n: IntLit, ns: Namespace, ctx: Context) -> Unit:
    return Unit().push(n.value)


def gen_lit(n: Lit, ns: Namespace, ctx: Context) -> Unit:
    return gen_int_lit(n.child, ns, ctx)


def stack_required(n: Node) -> MWord:
    if isinstance(n, FnDef):
        return to_ptr(len(n.arg_decls)) + stack_required(n.body)
    elif isinstance(n, Block):
        block_sizes = [stack_required(s) for s in n.stmts]
        biggest_block = max(block_sizes) if block_sizes else 0
        return to_ptr(len(n.var_decls)) + biggest_block
    elif isinstance(n, (Stmt, CompountStmt)):
        return stack_required(n.child)
    elif isinstance(n, (WhileStmt, IfStmt)):
        return stack_required(n.body)
    elif isinstance(n, Program):
        raise CodegenError('Program can not have a stack size')
    return 0
