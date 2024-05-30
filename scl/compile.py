from .scl import *
from .ffl import *

sind = {} # index of symbol; for signal it's always -1
stype = {} # type of symbol; False - signal, True - variable
def fresh_var(name):
    """create a new variable"""
    global sind, stype
    if name not in sind.keys():
        sind[name] = 0
        stype[name] = True
    sind[name] += 1
    return f"{name}${sind[name]-1}"

def fresh_signal(name):
    """create a new signal"""
    global sind, stype
    assert name not in sind.keys(), f"signal already exists, got: {name}"
    sind[name] = -1
    stype[name] = False
    return f"{name}"

def curr_sym(name):
    """refer to a symbol's current form"""
    assert name in sind.keys(), f"symbol is not registered, got: {name}"
    if stype[name]:
        # variable
        return f"{name}${sind[name]-1}"
    else:
        # signal
        return f"{name}"
    
def reset_symbols():
    global sind, stype
    sind = {}
    stype = {}

def sclop2fflop(op):
    match op:
        case SclOperator.ADD:
            return FflOperator.ADD
        case SclOperator.SUB:
            return FflOperator.SUB
        case SclOperator.MUL:
            return FflOperator.MUL
        case _:
            raise NotImplementedError(f"unsupported scl operator, got: {op}")
        
def compile_iszero(sym_in):
    _inv = fresh_var("_inv")
    _out = fresh_var("_expr")
    _tmp = []
    _tmp.append(FflEquation(_inv, FflExpr(FflOperator.VAR, [])))
    _tmp.append(FflEquation(_out, FflExpr(FflOperator.VAR, [])))
    _tmp.append(FflEquation(
        FflExpr(FflOperator.MUL, [sym_in, _inv]),
        FflExpr(FflOperator.SUB, [1, _out])
    ))
    _tmp.append(FflEquation(
        FflExpr(FflOperator.MUL, [sym_in, _out]),
        0
    ))
    return _out, _tmp

def compile(node):
    # returns (retv, equations)
    match node:

        case SclCircuit():
            # clear variable counter when starting a new circuit
            reset_symbols()
            _tmp = []
            for stmt in node.stmts:
                _expr, _equations = compile(stmt)
                _tmp += _equations
            return FflBlock(_tmp)
        
        case SclSignal():
            return None, [
                FflEquation(fresh_signal(sym), FflExpr(FflOperator.SIGNAL, []))
                for sym in node.syms
            ]

        case SclVar():
            # delay its compilation to assign
            return None, []

        case SclAssign():

            # Compile the expression to be set equal to.
            expr_scl, eq_array = compile(node.expr)

            # Create a fresh var.
            var_name = fresh_var(node.sym)

            # Assign it to var().
            eq_array += [FflEquation(var_name, FflExpr(FflOperator.VAR, []))]

            # Add an equation assigning sym = expr, using a new version var.
            eq_array += [FflEquation(var_name, expr_scl)]

            return None, eq_array

        case SclEq():

            # Compile the left and right nodes.
            lhs_scl, lhs_eq_array = compile(node.lhs)
            rhs_scl, rhs_eq_array = compile(node.rhs)

            # Combine the equation array.
            total_eq_array = lhs_eq_array
            total_eq_array += rhs_eq_array

            # Add an equation setting lhs = rhs.
            total_eq_array += [FflEquation(lhs_scl, rhs_scl)]

            return None, total_eq_array

        case SclExpr():

            # Return values.
            res_expr = ""
            eq_array = []

            # Addition, Multiplication, and Subtraction.
            if (node.op.arity() == 2 and node.op != SclOperator.DIV):
                
                # Compile the expressions to be operated on.
                in0_expr, in0_arr = compile(node.exprs[0])
                in1_expr, in1_arr = compile(node.exprs[1])

                # Store the previous equations.
                eq_array += in0_arr
                eq_array += in1_arr

                # Create a new expr var.
                res_expr = fresh_var("_expr")
                eq_array += [FflEquation(res_expr, FflExpr(FflOperator.VAR, []))]

                # Add the operation equation.
                eq_array += [FflEquation(
                    res_expr,
                    FflExpr(
                        sclop2fflop(node.op),
                        [in0_expr, in1_expr]
                    )
                )]

            elif (node.op == SclOperator.DIV):

                # Compile the expressions to be operated on.
                in0_expr, in0_arr = compile(node.exprs[0])
                in1_expr, in1_arr = compile(node.exprs[1])

                # Store the previous equations.
                eq_array += in0_arr
                eq_array += in1_arr

                # Create a new expr var.
                res_expr = fresh_var("_expr")
                eq_array += [FflEquation(res_expr, FflExpr(FflOperator.VAR, []))]

                # Add the operation equation but reformat to multiplication.
                eq_array += [FflEquation(
                    in0_expr,
                    FflExpr(
                        FflOperator.MUL,
                        [res_expr, in1_expr]
                    )
                )]

            return res_expr, eq_array

        # only when reading; for writing/creation use fresh_* directly
        case obj if isinstance(obj, str):
            return curr_sym(obj), []

        case obj if isinstance(obj, int):
            return obj, []
        
        case SclOperator():
            raise Exception(f"compilation should be done in expression, not here")
        
        # non-terminal exceptions should be put at last to prevent early matching

        case SclStmt():
            raise Exception(f"cannot compile a non-terminal node")
        
        case SclDecl():
            raise Exception(f"cannot compile a non-terminal node")

        case _:
            raise NotImplementedError(f"unsupported node, got: {node}")