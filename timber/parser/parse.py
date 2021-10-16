from typing import List, Tuple, Optional

from ..lexer import Token, TokenKind, TokenValue, Keyword
from .nodes import (VarDecl, FnDef, Block, Stmt, CompountStmt, SimpleStmt,
                    Expr, WhileStmt, IfStmt, FnCall, Var, Lit, IntLit,
                    InfixFnCall, Program, DefaultFnCall, ReturnStmt, Assign)


Ts = List[Token]


class ParserError(Exception):

    def __init__(self, msg: str, t: Optional[Token]) -> None:
        self.msg = msg
        self.t = t

    def __str__(self) -> str:
        return f'[{self.t}]: {self.msg}'


def parse_program(ts: Ts) -> Program:
    i = 0
    var_decls: List[VarDecl] = []
    fn_defs: List[FnDef] = []
    while i < len(ts):
        if ts[i].value == Keyword.FnDef:
            fn_def, i = parse_fn_def(ts, i)
            fn_defs.append(fn_def)
        elif ts[i].value == Keyword.Var:
            var_decl, i = parse_var_decl(ts, i)
            var_decls.append(var_decl)
            t, i = _consume_kind(ts, i, TokenKind.Semi)
        else:
            t = ts[i]
            msg = f'Expected keywords Def, Var, got {t.value}'
            raise ParserError(msg, t)
    return Program((0, i), var_decls, fn_defs)


def parse_fn_def(ts: Ts, j: int) -> Tuple[FnDef, int]:
    i = j
    _, i = _consume_value(ts, i, TokenKind.Keyword, Keyword.FnDef)
    t, i = _consume_kind(ts, i, TokenKind.Word)
    assert isinstance(t.value, str)
    name = t.value
    _, i = _consume_kind(ts, i, TokenKind.LParen)
    arg_decls: List[VarDecl] = []
    while i < len(ts):
        if ts[i].kind == TokenKind.RParen:
            break
        arg_decl, i = parse_var_decl(ts, i)
        arg_decls.append(arg_decl)
        if ts[i].kind == TokenKind.Comma:
            i += 1
    else:
        raise _unexpected_eot()
    _, i = _consume_kind(ts, i, TokenKind.RParen)
    body, i = parse_block(ts, i)
    return FnDef((j, i), name, arg_decls, body), i


def parse_block(ts: Ts, j: int) -> Tuple[Block, int]:
    i = j
    t, i = _consume_kind(ts, i, TokenKind.LBrace)
    var_decls: List[VarDecl] = []
    stmts: List[Stmt] = []
    while i < len(ts):
        kind = ts[i].kind
        value = ts[i].value
        if kind == TokenKind.RBrace:
            break
        if kind == TokenKind.Keyword and value == Keyword.Var:
            var_decl, i = parse_var_decl(ts, i)
            var_decls.append(var_decl)
        else:
            stmt, i = parse_stmt(ts, i)
            stmts.append(stmt)
        _, i = _consume_kind(ts, i, TokenKind.Semi)
    else:
        raise _unexpected_eot()
    _, i = _consume_kind(ts, i, TokenKind.RBrace)
    return Block((j, i), var_decls, stmts), i


def parse_stmt(ts: Ts, j: int) -> Tuple[Stmt, int]:
    i = j
    t = ts[i]
    compound_starters = [Keyword.While, Keyword.If]
    simple_starters = [Keyword.Return]
    if t.kind == TokenKind.Keyword:
        if t.value in compound_starters:
            comp_stmt, i = parse_comp_stmt(ts, i)
            return Stmt((j, i), comp_stmt), i
        elif t.value in simple_starters:
            simple_stmt, i = parse_simple_stmt(ts, i)
            return Stmt((j, i), simple_stmt), i
        else:
            msg = f'Expected keywords While, If, Return, got {t.value}'
            raise ParserError(msg, t)
    elif t.kind == TokenKind.LBrace:
        comp_stmt, i = parse_comp_stmt(ts, i)
        return Stmt((j, i), comp_stmt), i
    simple_stmt, i = parse_simple_stmt(ts, i)
    return Stmt((j, i), simple_stmt), i


def parse_comp_stmt(ts: Ts, j: int) -> Tuple[CompountStmt, int]:
    i = j
    t = ts[i]
    if t.kind == TokenKind.Keyword:
        if t.value == Keyword.While:
            while_stmt, i = parse_while_stmt(ts, i)
            return CompountStmt((j, i), while_stmt), i
        if t.value == Keyword.If:
            if_stmt, i = parse_if_stmt(ts, i)
            return CompountStmt((j, i), if_stmt), i
    elif t.kind == TokenKind.LBrace:
        block, i = parse_block(ts, i)
        return CompountStmt((j, i), block), i
    msg = f'Expected keywords While, If, got {t.value}'
    raise ParserError(msg, t)


def parse_simple_stmt(ts: Ts, j: int) -> Tuple[SimpleStmt, int]:
    i = j
    t = ts[i]
    if t.kind == TokenKind.Keyword:
        ret_stmt, i = parse_ret_stmt(ts, i)
        return SimpleStmt((j, i), ret_stmt), i
    expr, i = parse_expr(ts, i)
    return SimpleStmt((j, i), expr), i


def parse_ret_stmt(ts: Ts, j: int) -> Tuple[ReturnStmt, int]:
    i = j
    _, i = _consume_value(ts, i, TokenKind.Keyword, Keyword.Return)
    expr, i = parse_expr(ts, i)
    return ReturnStmt((j, i), expr), i


def parse_assign(ts: Ts, j: int) -> Tuple[Assign, int]:
    i = j
    t, i = _consume_kind(ts, i, TokenKind.Word)
    assert isinstance(t.value, str)
    name = t.value
    _, i = _consume_kind(ts, i, TokenKind.Eq)
    expr, i = parse_expr(ts, i)
    return Assign((j, i), name, expr), i


def parse_while_stmt(ts: Ts, j: int) -> Tuple[WhileStmt, int]:
    i = j
    _, i = _consume_value(ts, i, TokenKind.Keyword, Keyword.While)
    _, i = _consume_kind(ts, i, TokenKind.LParen)
    guard, i = parse_expr(ts, i)
    _, i = _consume_kind(ts, i, TokenKind.RParen)
    body, i = parse_block(ts, i)
    return WhileStmt((j, i), guard, body), i


def parse_if_stmt(ts: Ts, j: int) -> Tuple[IfStmt, int]:
    i = j
    _, i = _consume_value(ts, i, TokenKind.Keyword, Keyword.If)
    _, i = _consume_kind(ts, i, TokenKind.LParen)
    guard, i = parse_expr(ts, i)
    _, i = _consume_kind(ts, i, TokenKind.RParen)
    body, i = parse_block(ts, i)
    return IfStmt((j, i), guard, body), i


def parse_expr(ts: Ts, j: int, accept_infix: bool = True) -> Tuple[Expr, int]:
    i = j
    t = ts[i]
    if t.kind == TokenKind.LParen:
        _, i = _consume_kind(ts, i, TokenKind.LParen)
        child, i = parse_expr(ts, i)
        _, i = _consume_kind(ts, i, TokenKind.RParen)
        return Expr((j, i), child), i
    elif t.kind == TokenKind.Word:
        t1 = _peek(ts, i, 1)
        if t1.kind == TokenKind.LParen:
            fn_call, i = parse_fn_call(ts, i)
            return Expr((j, i), fn_call), i
        elif t1.kind == TokenKind.Eq:
            assign, i = parse_assign(ts, i)
            return Expr((j, i), assign), i
        else:
            var, i = parse_var(ts, i)
            return Expr((j, i), var), i
    elif t.kind == TokenKind.Int:
        lit, i = parse_lit(ts, i)
        return Expr((j, i), lit), i
    raise ParserError('Unexpected token', t)


def parse_infix_fn_call(ts: Ts, j: int) -> Tuple[InfixFnCall, int]:
    raise NotImplementedError
    i = j
    arg_1, i = parse_expr(ts, i, accept_infix=False)
    t, i = _consume_kind(ts, i, TokenKind.Word)
    assert isinstance(t.value, str)
    name = t.value
    arg_2, i = parse_expr(ts, i)
    return InfixFnCall((j, i), name, arg_1, arg_2), i


def parse_lit(ts: Ts, j: int) -> Tuple[Lit, int]:
    i = j
    int_lit, i = parse_int_lit(ts, i)
    return Lit((j, i), int_lit), i


def parse_int_lit(ts: Ts, j: int) -> Tuple[IntLit, int]:
    i = j
    t, i = _consume_kind(ts, i, TokenKind.Int)
    assert isinstance(t.value, int)
    return IntLit((j, i), t.value), i


def parse_var(ts: Ts, j: int) -> Tuple[Var, int]:
    i = j
    t, i = _consume_kind(ts, i, TokenKind.Word)
    assert isinstance(t.value, str)
    return Var((j, i), t.value), i


def parse_fn_call(ts: Ts, j: int) -> Tuple[FnCall, int]:
    i = j
    t1 = _peek(ts, i, 1)
    if t1.kind == TokenKind.LParen:
        default_fn_call, i = parse_default_fn_call(ts, i)
        return FnCall((j, i), default_fn_call), i
    if t1.kind == TokenKind.Word:
        infix_fn_call, i = parse_infix_fn_call(ts, i)
        return FnCall((j, i), infix_fn_call), i
    raise ParserError('Failed parsing FnCall', ts[i])


def parse_default_fn_call(ts: Ts, j: int) -> Tuple[DefaultFnCall, int]:
    i = j
    t, i = _consume_kind(ts, i, TokenKind.Word)
    assert isinstance(t.value, str)
    name = t.value
    _, i = _consume_kind(ts, i, TokenKind.LParen)
    arg_exprs: List[Expr] = []
    while i < len(ts):
        if ts[i].kind == TokenKind.RParen:
            break
        arg_expr, i = parse_expr(ts, i)
        arg_exprs.append(arg_expr)
        if ts[i].kind == TokenKind.Comma:
            i += 1
    else:
        raise _unexpected_eot()
    _, i = _consume_kind(ts, i, TokenKind.RParen)
    return DefaultFnCall((j, i), name, arg_exprs), i


def parse_var_decl(ts: Ts, j: int) -> Tuple[VarDecl, int]:
    i = j
    _, i = _consume_value(ts, i, TokenKind.Keyword, Keyword.Var)
    t, i = _consume_kind(ts, i, TokenKind.Word)
    assert isinstance(t.value, str)
    return VarDecl((j, i), t.value), i


def _peek(ts: Ts, i: int, d: int = 1) -> Token:
    if i + d >= len(ts):
        raise _unexpected_eot()
    return ts[i + d]


def _unexpected_eot() -> ParserError:
    return ParserError('Unexpected end of tokens', None)


def _consume_any(ts: Ts, i: int) -> Tuple[Token, int]:
    if i >= len(ts):
        raise _unexpected_eot()
    return ts[i], i + 1


def _consume_kind(ts: Ts, i: int, kind: TokenKind) -> Tuple[Token, int]:
    t, i = _consume_any(ts, i)
    if t.kind != kind:
        raise ParserError(f'Expected kind {kind}, got {t.kind}', t)
    return t, i


def _consume_value(ts: Ts, i: int, kind: TokenKind, value: TokenValue
                   ) -> Tuple[Token, int]:
    t, i = _consume_kind(ts, i, kind)
    if t.value != value:
        raise ParserError(f'Expected value {value}, got {t.value}', t)
    return t, i
