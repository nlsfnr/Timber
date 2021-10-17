from .nodes import (VarDecl, FnDef, Block, Stmt, CompountStmt, SimpleStmt,
                    Expr, WhileStmt, IfStmt, FnCall, Var, Lit, IntLit,
                    InfixFnCall, Program, DefaultFnCall, Assign, ReturnStmt,
                    Node, StrLit)


def fmt_node(node: Node, lvl: int = 0) -> str:
    if isinstance(node, VarDecl):
        s = f'VarDecl {node.name}\n'
    elif isinstance(node, FnDef):
        args_s = ', '.join(a.name for a in node.arg_decls)
        s = f'FnDef {node.name}({args_s})\n'
        s += fmt_node(node.body, lvl + 1)
    elif isinstance(node, Block):
        stmt_s = '\n'.join(fmt_node(s, lvl + 1) for s in node.stmts)
        var_decl_s = '\n'.join(fmt_node(v, lvl + 1) for v in node.var_decls)
        s = 'Block'
        s += f'\n{var_decl_s}' if var_decl_s else ''
        s += f'\n{stmt_s}' if stmt_s else ''
        if not (var_decl_s or stmt_s):
            s += '\n'
    elif isinstance(node, Stmt):
        s = 'Stmt\n' + fmt_node(node.child, lvl + 1)
    elif isinstance(node, CompountStmt):
        s = 'CompountStmt\n' + fmt_node(node.child, lvl + 1)
    elif isinstance(node, SimpleStmt,):
        s = 'SimpleStmt\n' + fmt_node(node.child, lvl + 1)
    elif isinstance(node, Expr):
        s = 'Expr\n' + fmt_node(node.child, lvl + 1)
    elif isinstance(node, WhileStmt):
        s = 'WhileStmt\n'
        s += fmt_node(node.guard, lvl + 1)
        s += fmt_node(node.body, lvl + 1)
    elif isinstance(node, IfStmt):
        s = 'IfStmt\n'
        s += fmt_node(node.guard, lvl + 1)
        s += fmt_node(node.body, lvl + 1)
    elif isinstance(node, FnCall):
        s = 'FnCall\n' + fmt_node(node.child, lvl + 1)
    elif isinstance(node, Var):
        s = f'Var {node.name}\n'
    elif isinstance(node, Lit):
        s = 'Lit\n' + fmt_node(node.child, lvl + 1)
    elif isinstance(node, IntLit,):
        s = f'IntLit {node.value}\n'
    elif isinstance(node, StrLit,):
        s = f'StrLit {node.value}\n'
    elif isinstance(node, InfixFnCall):
        s = f'InfixFnCall {node.name}\n'
        s += fmt_node(node.arg_1, lvl + 1)
        s += fmt_node(node.arg_2, lvl + 1)
    elif isinstance(node, Program):
        var_decl_s = '\n'.join(fmt_node(v, lvl + 1) for v in node.var_decls)
        fn_def_s = '\n'.join(fmt_node(f, lvl + 1) for f in node.fn_defs)
        s = f'Program\n{var_decl_s}\n{fn_def_s}\n'
    elif isinstance(node, Var):
        s = f'Var {node.name}\n'
    elif isinstance(node, DefaultFnCall):
        arg_s = ''.join(fmt_node(a, lvl + 1) for a in node.args)
        s = f'DefaultFnCall {node.name}\n{arg_s}'
    elif isinstance(node, Assign):
        s = f'Assign {node.name}\n' + fmt_node(node.expr, lvl + 1)
    elif isinstance(node, ReturnStmt):
        s = 'Return\n' + fmt_node(node.child, lvl + 1)
    else:
        raise NotImplementedError(f'Unknown node: {node}')
    return f'{node.span[0]:3} {node.span[1]:3} ' + '  ' * lvl + s
