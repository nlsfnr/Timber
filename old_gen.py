from dataclasses import dataclass, field
from typing import List, Dict

from common import Stmt, FnCall, Expr, Lit, Int, Block
from vm import Instr, InstrKind, Program


TOS = 0
STACK = 1

_DUMMY_ADDR = -9999999


class GenError(Exception):
    pass


@dataclass
class Unit:
    instrs: List[Instr] = field(default_factory=list)
    labels: Dict[str, int] = field(default_factory=dict)
    jumps: Dict[int, str] = field(default_factory=dict)

    def push(self, instr: Instr) -> 'Unit':
        self.instrs.append(instr)
        return self

    def label(self, name: str) -> 'Unit':
        self.labels[name] = len(self.instrs)
        return self

    def jump(self, name: str) -> int:
        self.jumps[len(self.instrs)] = name
        return _DUMMY_ADDR

    def __str__(self) -> str:
        instrs_s = '\n'.join([f'{i:03} {x.kind.name:6} '
                              f'{x.arg if x.arg is not None else ""}'
                              for i, x in enumerate(self.instrs)])
        return f'{self.labels}\n{self.jumps}\n{instrs_s}'


def _get_tos(d: int) -> Unit:
    return (Unit()
            .push(Instr(InstrKind.Push, TOS))
            .push(Instr(InstrKind.Load))
            .push(Instr(InstrKind.Push, d))
            .push(Instr(InstrKind.Add))
            .push(Instr(InstrKind.Load)))


def _store_tos() -> Unit:
    return (Unit()
            .push(Instr(InstrKind.Push, TOS))
            .push(Instr(InstrKind.Load))
            .push(Instr(InstrKind.Store)))


def get_intrinsics() -> Unit:
    primitives = (
        ('add', InstrKind.Add),
        # ('sub', InstrKind.Sub),
        # ('shl', InstrKind.Shl),
        # ('shr', InstrKind.Shr),
        # ('and', InstrKind.And),
        # ('or', InstrKind.Or),
    )
    units: List[Unit] = []
    for name, instr_kind in primitives:
        unit = merge([
            Unit().label(name),
            _get_tos(0),
            _get_tos(1),
            Unit().push(Instr(instr_kind)),
            _store_tos(),
            Unit().push(Instr(InstrKind.Ret)),
        ])
        units.append(unit)
    return merge(units)


def get_setup() -> Unit:
    return (Unit()
            .push(Instr(InstrKind.Push, STACK))
            .push(Instr(InstrKind.Push, TOS))
            .push(Instr(InstrKind.Store)))


def merge(units: List[Unit]) -> Unit:
    merged = Unit()
    for unit in units:
        # TODO: Check for name collisions
        addr_offset = len(merged.instrs)
        offset_labels = {name: addr + addr_offset
                         for name, addr in unit.labels.items()}
        offset_jumps = {addr + addr_offset: name
                        for addr, name in unit.jumps.items()}
        merged.labels.update(offset_labels)
        merged.jumps.update(offset_jumps)
        merged.instrs.extend(unit.instrs)
    return merged


def gen(stmt: Stmt) -> Unit:
    return gen_stmt(stmt)


def gen_stmt(stmt: Stmt) -> Unit:
    child = stmt.child
    if isinstance(child, Expr):
        return gen_expr(child)
    elif isinstance(child, Block):
        return merge([gen_stmt(child) for child in child.children])
    raise NotImplementedError


def gen_block(block: Block) -> Unit:
    return merge([gen_stmt(child) for child in block.children])


def gen_expr(expr: Expr) -> Unit:
    child = expr.child
    if isinstance(child, FnCall):
        return gen_fn_call(child)
    if isinstance(child, Lit):
        return gen_lit(child)
    raise NotImplementedError


def gen_lit(lit: Lit) -> Unit:
    child = lit.child
    if isinstance(child, Int):
        return gen_int(child)
    raise NotImplementedError


def gen_int(int_: Int) -> Unit:
    return Unit().push(Instr(InstrKind.Push, int_.value))


def gen_fn_call(fn_call: FnCall) -> Unit:
    name = fn_call.name
    arg_exprs = fn_call.args
    arg_expr_units = [gen_expr(arg_expr) for arg_expr in arg_exprs]
    arg_units = []
    for i, aeu in enumerate(arg_expr_units):
        arg_setup = (Unit()
                     .push(Instr(InstrKind.Push, TOS))
                     .push(Instr(InstrKind.Load))
                     .push(Instr(InstrKind.Push, i))
                     .push(Instr(InstrKind.Add))
                     .push(Instr(InstrKind.Store)))
        arg_units.append(merge([aeu, arg_setup]))
    fn_setup = merge(arg_units)
    return fn_setup.push(Instr(InstrKind.Call, fn_setup.jump(name)))


def link(unit: Unit) -> Program:
    for addr, name in unit.jumps.items():
        if name not in unit.labels:
            raise GenError(f'Unknown label: {name}')
        instr = unit.instrs[addr]
        assert instr.kind in [InstrKind.Jmp, InstrKind.JmpF, InstrKind.Call]
        assert instr.arg == _DUMMY_ADDR
        instr.arg = unit.labels[name] - 1
    return Program(unit.instrs)
