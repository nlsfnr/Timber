from .nodes import (VarDecl, FnDef, Block, Stmt, CompountStmt, SimpleStmt,
                    Expr, WhileStmt, IfStmt, FnCall, Var, Lit, IntLit,
                    InfixFnCall, Program, DefaultFnCall, Node)


def fmt_node(node: Node, lvl: int = 0) -> str:
    if isinstance(node, VarDecl):
        s = f'VarDecl {node.name}'
    elif isinstance(node, FnDef):
        args_s = ', '.join(a.name for a in node.arg_decls)
        s = f'FnDef {node.name}({args_s})\n'
        s += fmt_node(node.body, lvl + 1)
    elif isinstance(node, Block):
        stmt_s = '\n'.join(fmt_node(s, lvl + 1) for s in node.stmts)
        var_decl_s = '\n'.join(fmt_node(v, lvl + 1) for v in node.var_decls)
        s = f'Block\n{var_decl_s}\n{stmt_s}'
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
    elif isinstance(node, InfixFnCall):
        s = f'InfixFnCall {node.name}'
        s += fmt_node(node.arg_1, lvl + 1)
        s += fmt_node(node.arg_2, lvl + 2)
    elif isinstance(node, Program):
        var_decl_s = '\n'.join(fmt_node(v, lvl + 1) for v in node.var_decls)
        fn_def_s = '\n'.join(fmt_node(f, lvl + 1) for f in node.fn_defs)
        s = f'Program\n{var_decl_s}\n{fn_def_s}'
    elif isinstance(node, Var):
        s = f'Var {node.name}'
    elif isinstance(node, DefaultFnCall):
        arg_s = '\n'.join(fmt_node(a, lvl + 1) for a in node.args)
        s = f'DefaultFnCall {node.name}\n{arg_s}'
    else:
        raise NotImplementedError
    return '  ' * lvl + s
