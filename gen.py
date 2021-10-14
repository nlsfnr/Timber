from functools import reduce
from dataclasses import dataclass, field
from typing import Optional, Dict

from vm import Val, Instr, InstrKind, Program
from common import Stmt, Block, Expr, Lit, Int, Var, FnCall, FnDef, WhileLoop


_TOS_ADDR_PTR = 0
_STACK_BASE = 8
_DUMMY_ADDR = -9999999


class GenError(Exception):
    pass


@dataclass
class Unit:
    instrs: Program = field(default_factory=Program)
    labels: Dict[str, int] = field(default_factory=dict)
    jumps: Dict[int, str] = field(default_factory=dict)
    comments: Dict[int, str] = field(default_factory=dict)

    _next_label_id: int = -1

    @classmethod
    def new_label(self) -> str:
        self._next_label_id += 1
        return f'__{self._next_label_id}'

    def _add_instr(self, instr_kind: InstrKind, arg: Optional[Val] = None
                   ) -> 'Unit':
        self.instrs.append(Instr(instr_kind, arg))
        return self

    def insert(self, unit: 'Unit') -> 'Unit':
        addr_offset = len(self.instrs)
        offset_labels = {name: addr + addr_offset
                         for name, addr in unit.labels.items()}
        offset_jumps = {addr + addr_offset: name
                        for addr, name in unit.jumps.items()}
        if self.instrs.here in self.comments and 0 in unit.comments:
            unit.comments[0] = (self.comments[self.instrs.here] + '\n' +
                                unit.comments[0])
        offset_comments = {addr + addr_offset: comment
                           for addr, comment in unit.comments.items()}
        self.labels.update(offset_labels)
        self.jumps.update(offset_jumps)
        self.comments.update(offset_comments)
        self.instrs.extend(unit.instrs)
        return self

    def link(self) -> 'Unit':
        for addr, name in self.jumps.items():
            if name not in self.labels:
                raise GenError(f'Unknown label: {name}')
            instr = self.instrs[addr]
            assert instr.kind in [InstrKind.Jmp, InstrKind.JmpF,
                                  InstrKind.JmpT, InstrKind.Call]
            assert instr.arg == _DUMMY_ADDR
            instr.arg = self.labels[name] - 1
        return self

    def label(self, name: str) -> 'Unit':
        self.labels[name] = len(self.instrs)
        return self

    def comment(self, comment: str) -> 'Unit':
        idx = self.instrs.here
        if idx not in self.comments:
            self.comments[self.instrs.here] = comment
        else:
            self.comments[idx] += '\n' + comment
        return self

    def noop(self) -> 'Unit':
        return self._add_instr(InstrKind.Pop)

    def halt(self) -> 'Unit':
        return self._add_instr(InstrKind.Halt)

    def rot(self) -> 'Unit':
        return self._add_instr(InstrKind.Rot)

    def dup(self) -> 'Unit':
        return self._add_instr(InstrKind.Dup)

    def load(self) -> 'Unit':
        return self._add_instr(InstrKind.Load)

    def store(self) -> 'Unit':
        return self._add_instr(InstrKind.Store)

    def add(self) -> 'Unit':
        return self._add_instr(InstrKind.Add)

    def sub(self) -> 'Unit':
        return self._add_instr(InstrKind.Sub)

    def shl(self) -> 'Unit':
        return self._add_instr(InstrKind.Shl)

    def shr(self) -> 'Unit':
        return self._add_instr(InstrKind.Shr)

    def and_(self) -> 'Unit':
        return self._add_instr(InstrKind.And)

    def or_(self) -> 'Unit':
        return self._add_instr(InstrKind.Or)

    def call(self, name: str) -> 'Unit':
        self.jumps[self.instrs.here] = name
        return self._add_instr(InstrKind.Call, _DUMMY_ADDR)

    def ret(self) -> 'Unit':
        return self._add_instr(InstrKind.Ret)

    def st(self) -> 'Unit':
        return self._add_instr(InstrKind.St)

    def jmp(self, name: str) -> 'Unit':
        self.jumps[self.instrs.here] = name
        return self._add_instr(InstrKind.Jmp, _DUMMY_ADDR)

    def jmp_f(self, name: str) -> 'Unit':
        self.jumps[self.instrs.here] = name
        return self._add_instr(InstrKind.JmpF, _DUMMY_ADDR)

    def jmp_t(self, name: str) -> 'Unit':
        self.jumps[self.instrs.here] = name
        return self._add_instr(InstrKind.JmpT, _DUMMY_ADDR)

    def push(self, arg: Val) -> 'Unit':
        return self._add_instr(InstrKind.Push, arg)

    def pop(self) -> 'Unit':
        return self._add_instr(InstrKind.Pop)

    def print(self) -> 'Unit':
        return self._add_instr(InstrKind.Print)

    def incr_tos(self, offset: Val) -> 'Unit':
        assert offset >= 0
        return (self
                .load_tos_ptr()
                .push(offset)
                .add()
                .store_tos_ptr())

    def decr_tos(self, offset: Val) -> 'Unit':
        assert offset >= 0
        return (self
                .load_tos_ptr()
                .push(offset)
                .sub()
                .store_tos_ptr())

    def load_tos_ptr(self, offset: Val = 0) -> 'Unit':
        if offset == 0:
            return (self
                    .push(_TOS_ADDR_PTR)
                    .load())
        return (self
                .push(_TOS_ADDR_PTR)
                .load()
                .push(offset)
                .add())

    def store_tos_ptr(self) -> 'Unit':
        return (self
                .push(_TOS_ADDR_PTR)
                .store())

    def load_tos(self, offset: Val = 0) -> 'Unit':
        return self.load_tos_ptr(offset).load()

    def store_tos(self, offset: Val = 0) -> 'Unit':
        return self.load_tos_ptr(offset).store()

    def push_tos(self) -> 'Unit':
        return (self
                .comment('push TOS {')
                .store_tos()
                .incr_tos(1)
                .comment('} push TOS'))

    def pop_tos(self) -> 'Unit':
        return (self
                .comment('pop TOS {')
                .decr_tos(1)
                .load_tos()
                .comment('} pop TOS'))

    @classmethod
    def fresh(cls) -> 'Unit':
        return (cls()
                .comment('entrypoint {')
                .push(_STACK_BASE)
                .push(_TOS_ADDR_PTR)
                .store()
                .call('main')
                .halt()
                .comment('} entrypoint'))

    def intrinsics(self) -> 'Unit':
        binary_ops = (
            ('add', Unit().add()),
            # ('sub', Unit().sub()),
            # ('and', Unit().and_()),
            # ('or', Unit().or_()),
            # ('shr', Unit().shr()),
            ('shl', Unit().shl()),
        )
        for name, unit in binary_ops:
            (self
             .comment(f'def {name} {{')
             .label(name)
             .pop_tos()
             .pop_tos()
             .rot()
             .insert(unit)
             .rot()
             .ret()
             .comment(f'}} def {name}'))
        unary_ops = (
            ('print', Unit().print().push(0)),
        )
        for name, unit in unary_ops:
            (self
             .comment(f'def {name} {{')
             .label(name)
             .pop_tos()
             .insert(unit)
             .rot()
             .ret()
             .comment(f'}} def {name}'))
        (self
         .comment('def exit {')
         .label('exit')
         .pop()  # Pop the return address
         .pop_tos()
         .halt()
         .comment('} def exit'))
        (self
         .comment('def return {')
         .label('return')
         .pop_tos()
         .rot()
         .pop()  # Pop the return address
         .rot()
         .ret()  # Return to the caller's return address
         .comment('} def return'))
        return self

    def __str__(self) -> str:
        lines = []
        for i, x in enumerate(self.instrs):
            if i in self.comments:
                lines.append(self.comments[i])
            lines.append(f'  {i:03} {x.kind.name:6} '
                         f'{x.arg if x.arg is not None else ""}')
        if i + 1 in self.comments:
            lines.append(self.comments[i + 1])
        return '\n'.join(lines)

    def to_program(self) -> Program:
        return self.instrs


def gen(stmt: Stmt) -> Unit:
    return (Unit()
            .fresh()
            .insert(gen_stmt(stmt))
            .halt()
            .intrinsics()
            .link())


def gen_stmt(stmt: Stmt) -> Unit:
    child = stmt.child
    if isinstance(child, Block):
        return gen_block(child)
    elif isinstance(child, Expr):
        return gen_expr(child).pop()
    elif isinstance(child, FnDef):
        return gen_fn_def(child)
    elif isinstance(child, WhileLoop):
        return gen_while_loop(child)
    else:
        raise NotImplementedError


def gen_block(block: Block) -> Unit:
    units = map(gen_stmt, block.children)
    return reduce(Unit.insert, units, Unit())


def gen_expr(expr: Expr) -> Unit:
    child = expr.child
    if isinstance(child, Lit):
        return gen_lit(child)
    if isinstance(child, Var):
        return gen_var(child)
    if isinstance(child, FnCall):
        return gen_fn_call(child)
    else:
        raise NotImplementedError


def gen_fn_def(fn_def: FnDef) -> Unit:
    # The body of a function must leave the (single) return value on the
    # hardware stack.
    body = gen_stmt(fn_def.stmt)
    return (Unit()
            .comment(f'def {fn_def.name} {{')
            .label(fn_def.name)
            .insert(body)
            .push(0)
            .rot()
            .ret()
            .comment(f'}} def {fn_def.name}'))


def gen_while_loop(while_loop: WhileLoop) -> Unit:
    guard = gen_expr(while_loop.guard)
    body = gen_stmt(while_loop.body)
    start_label = Unit.new_label()
    guard_label = Unit.new_label()
    end_label = Unit.new_label()
    return (Unit()
            .comment('while loop {')
            .jmp(guard_label)
            .label(start_label)
            .comment('while body {')
            .insert(body)
            .comment('} while body')
            .comment('while guard {')
            .label(guard_label)
            .insert(guard)
            .jmp_t(start_label)
            .comment('} while guard')
            .label(end_label)
            .comment('} while loop'))


def gen_fn_call(fn_call: FnCall) -> Unit:
    args_raw = [gen_expr(arg) for arg in fn_call.args]
    args_pushed = [Unit().insert(arg).push_tos()
                   for i, arg in enumerate(args_raw)]
    args = reduce(Unit.insert, args_pushed,
                  Unit().comment(f'call {fn_call.name} {{'))
    return args.call(fn_call.name).comment(f'}} call {fn_call.name}')


def gen_lit(lit: Lit) -> Unit:
    child = lit.child
    if isinstance(child, Int):
        return gen_int(child)
    else:
        raise NotImplementedError


def gen_int(int_: Int) -> Unit:
    return Unit().push(int_.value)


def gen_var(var: Var) -> Unit:
    raise NotImplementedError
