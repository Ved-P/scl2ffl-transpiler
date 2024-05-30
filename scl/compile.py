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
            # ============================
            # add your implementation here
            # ============================
            return None, []

        case SclEq():
            # ============================
            # add your implementation here
            # ============================
            return None, []

        case SclExpr():
            # ============================
            # add your implementation here
            # ============================
            return None, []

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