from typing import List, Optional, Tuple, TypeVar, Callable

from common import (Token, TokenKind, TokenValue, Stmt, Block, Expr, FnCall,
                    Lit, Int, Var, FnDef, WhileLoop, Node, VarDecl, Keyword,
                    Assign)


NodeT = TypeVar('NodeT', bound=Node)


_DONT_CARE = 'placeholder'


class ParsingError(Exception):

    def __init__(self, msg: str, token: Optional[Token] = None) -> None:
        self.msg = msg
        self.token = token

    def __str__(self) -> str:
        span = ''
        if self.token is not None:
            tok = f'[{self.token}]'
        return f'ParsingError{tok}: {self.msg}'


def parse(tokens: List[Token]) -> Node:
    node, _ = parse_stmt(tokens, 0)
    return node


def expected_but_got(expected: List[TokenKind], got: Token) -> ParsingError:
    xs = map(str, expected)
    msg = f'Expected one of: [{", ".join(xs)}], got: {got.kind}'
    return ParsingError(msg, got)


def expected_value_but_got(expected_kind: TokenKind, expect_value: TokenValue,
                           got: Token) -> ParsingError:
    msg = (f'Expected: {expected_kind} with value {expect_value}, got: '
           f'{got.kind} with value {got.value}')
    return ParsingError(msg, got)


def unexpected_end_of_tokens() -> ParsingError:
    return ParsingError('Unexpected end of tokens')


def peek(tokens: List[Token], i: int) -> Optional[Token]:
    return tokens[i] if i < len(tokens) else None


def peek_expect(tokens: List[Token], i: int) -> Token:
    if i >= len(tokens):
        raise unexpected_end_of_tokens()
    return tokens[i]


def expect(tokens: List[Token], i: int, expected: TokenKind
           ) -> Tuple[Token, int]:
    t = peek_expect(tokens, i)
    if not t.kind == expected:
        raise expected_but_got([expected], t)
    return t, i + 1


def expect_value(tokens: List[Token], i: int, expected_kind: TokenKind,
                 expect_value: TokenValue) -> Tuple[Token, int]:
    t = peek_expect(tokens, i)
    if not t.kind == expected_kind and t.value == expect_value:
        raise expected_value_but_got(expected_kind, expect_value, t)
    return t, i + 1


def parse_stmt(tokens: List[Token], i: int) -> Tuple[Stmt, int]:
    t = peek_expect(tokens, i)
    if t.kind == TokenKind.LBrace:
        block, i = parse_block(tokens, i)
        return Stmt(block), i
    elif t.kind == TokenKind.Keyword:
        assert isinstance(t.value, Keyword)
        if t.value == Keyword.FnDef:
            fn_def, i = parse_fn_def(tokens, i)
            return Stmt(fn_def), i
        elif t.value == Keyword.While:
            while_loop, i = parse_while_loop(tokens, i)
            return Stmt(while_loop), i
        elif t.value == Keyword.Var:
            var, i = parse_var_decl(tokens, i)
            return Stmt(var), i
        raise NotImplementedError
    elif t.kind == TokenKind.Word:
        t1 = peek_expect(tokens, i + 1)
        if t1.kind == TokenKind.Eq:
            assign, i = parse_assign(tokens, i)
            return Stmt(assign), i
        elif t1.kind == TokenKind.LParen:
            expr, i = parse_expr(tokens, i)
            return Stmt(expr), i
    raise ParsingError(f'Could not parse token', t)


def parse_block(tokens: List[Token], i: int) -> Tuple[Block, int]:
    t, i = expect(tokens, i, TokenKind.LBrace)
    children: List[Stmt]
    children, i = parse_until(tokens, i, parse_stmt,
                              terminator=TokenKind.RBrace,
                              delimiter=TokenKind.Semi)
    return Block(children), i


def parse_expr(tokens: List[Token], i: int) -> Tuple[Expr, int]:
    t = peek_expect(tokens, i)
    if t.kind == TokenKind.Int:
        lit, i = parse_lit(tokens, i)
        return Expr(lit), i
    elif t.kind == TokenKind.Word:
        # Var | FnCall
        t1 = peek(tokens, i + 1)
        if t1 is not None and t1.kind == TokenKind.LParen:
            # FnCall
            fn_call, i = parse_fn_call(tokens, i)
            return Expr(fn_call), i
        else:
            var, i = parse_var(tokens, i)
            return Expr(var), i
    else:
        raise expected_but_got([TokenKind.Int, TokenKind.Word], t)


def parse_fn_call(tokens: List[Token], i: int) -> Tuple[FnCall, int]:
    name_token, i = expect(tokens, i, TokenKind.Word)
    assert isinstance(name_token.value, str)
    _, i = expect(tokens, i, TokenKind.LParen)
    arg_exprs, i = parse_until(tokens, i, parse_expr, TokenKind.Comma,
                               TokenKind.RParen)
    return FnCall(name_token.value, arg_exprs), i


def parse_fn_def(tokens: List[Token], i: int) -> Tuple[FnDef, int]:
    _, i = expect_value(tokens, i, TokenKind.Keyword, Keyword.FnDef)
    name_token, i = expect(tokens, i, TokenKind.Word)
    assert isinstance(name_token.value, str)
    _, i = expect(tokens, i, TokenKind.LParen)
    arg_vars, i = parse_until(tokens, i, parse_var, TokenKind.Comma,
                              TokenKind.RParen)
    arg_names = [a.name for a in arg_vars]
    stmt, i = parse_stmt(tokens, i)
    return FnDef(name_token.value, arg_names, stmt), i


def parse_assign(tokens: List[Token], i: int) -> Tuple[Assign, int]:
    name_token, i = expect(tokens, i, TokenKind.Word)
    assert isinstance(name_token.value, str)
    _, i = expect(tokens, i, TokenKind.Eq)
    expr, i = parse_expr(tokens, i)
    return Assign(name_token.value, expr), i


def parse_lit(tokens: List[Token], i: int) -> Tuple[Lit, int]:
    t = peek_expect(tokens, i)
    if t.kind == TokenKind.Int:
        int_, i = parse_int(tokens, i)
        return Lit(int_), i
    else:
        raise expected_but_got([TokenKind.Int], t)


def parse_int(tokens: List[Token], i: int) -> Tuple[Int, int]:
    t, i = expect(tokens, i, TokenKind.Int)
    assert isinstance(t.value, int)
    return Int(t, t.value), i


def parse_var_decl(tokens: List[Token], i: int) -> Tuple[VarDecl, int]:
    _, i = expect_value(tokens, i, TokenKind.Keyword, Keyword.Var)
    name_token, i = expect(tokens, i, TokenKind.Word)
    assert isinstance(name_token.value, str)
    return VarDecl(name_token.value), i


def parse_var(tokens: List[Token], i: int) -> Tuple[Var, int]:
    t, i = expect(tokens, i, TokenKind.Word)
    assert isinstance(t.value, str)
    return Var(t, t.value), i


def parse_while_loop(tokens: List[Token], i: int) -> Tuple[WhileLoop, int]:
    _, i = expect_value(tokens, i, TokenKind.Keyword, Keyword.While)
    _, i = expect(tokens, i, TokenKind.LParen)
    guard, i = parse_expr(tokens, i)
    _, i = expect(tokens, i, TokenKind.RParen)
    body, i = parse_stmt(tokens, i)
    return WhileLoop(guard, body), i


def parse_until(tokens: List[Token], i: int,
                parse_fn: Callable[[List[Token], int], Tuple[NodeT, int]],
                delimiter: TokenKind, terminator: TokenKind
                ) -> Tuple[List[NodeT], int]:
    nodes: List[NodeT] = []
    first = True
    while i < len(tokens):
        t = peek_expect(tokens, i)
        if t.kind == terminator:
            break
        if not first:
            if t.kind != delimiter:
                raise expected_but_got([delimiter], t)
            i += 1
        first = False
        node, i = parse_fn(tokens, i)
        nodes.append(node)
    else:
        raise unexpected_end_of_tokens()
    return nodes, i + 1
