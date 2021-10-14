from common import (Node, Stmt, Block, Expr, Lit, Int, Var, FnCall, FnDef,
                    VarDecl, WhileLoop, Assign)


def fmt_node(node: Node) -> str:
    return _fmt_node(node, 0)


def _fmt_node(node: Node, lvl: int) -> str:
    padding = '  ' * lvl
    if isinstance(node, Stmt):
        return padding + f'Stmt\n{_fmt_node(node.child, lvl + 1)}'
    if isinstance(node, Block):
        stmts = '\n'.join([_fmt_node(stmt, lvl + 1) for stmt in node.children])
        return padding + f'Block\n{stmts}'
    if isinstance(node, WhileLoop):
        return padding + (f'WhileLoop\n'
                          f'{_fmt_node(node.guard, lvl + 1)}\n'
                          f'{_fmt_node(node.body, lvl + 1)}')
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
    if isinstance(node, VarDecl):
        return padding + f'VarDecl {node.name}'
    if isinstance(node, Assign):
        return padding + f'Assign {node.name}\n{_fmt_node(node.expr, lvl + 1)}'
    raise NotImplementedError
