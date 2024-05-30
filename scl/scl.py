from enum import Enum

class SclNode:
    """primitive node type"""

    # NOTE: need both args and kwargs as child class also inherits Enum
    def __init__(self, *args, **kwargs):
        self.iden = 2

class SclCircuit(SclNode):

    @staticmethod
    def from_json(node):
        match node:
            case ["circuit", *stmts]:
                _stmts = [SclStmt.from_json(p) for p in stmts]
                return SclCircuit(_stmts)
            case _:
                raise NotImplementedError(f"unsupported json component, got: {node}")

    def __init__(self, _stmts):
        super().__init__()
        self.stmts = _stmts

    def __str__(self):
        _iden = " "*self.iden
        _stmts = "\n".join([f"{_iden}{p}" for p in self.stmts])
        return f"(circuit\n{_stmts}\n)"

class SclStmt(SclNode):

    @staticmethod
    def from_json(node):
        match node:
            case ["signal", *_]:
                return SclDecl.from_json(node)
            case ["var", *_]:
                return SclDecl.from_json(node)
            case [":=", *_]:
                return SclAssign.from_json(node)
            case ["eq", *_]:
                return SclEq.from_json(node)
            # case ["for", *_]:
            #     return SclFor.from_json(node)
            case _:
                raise NotImplementedError(f"unsupported json component, got: {node}")
            
    def __init__(self):
        super().__init__()
        pass

    def __str__(self):
        raise Exception(f"cannot print a non-terminal node")

class SclDecl(SclStmt):

    @staticmethod
    def from_json(node):
        match node:
            case ["signal", *_]:
                return SclSignal.from_json(node)
            case ["var", *_]:
                return SclVar.from_json(node)
            case _:
                raise NotImplementedError(f"unsupported json component, got: {node}")
    
    def __init__(self):
        super().__init__()
        pass

    def __str__(self):
        raise Exception(f"cannot print a non-terminal node")

class SclSignal(SclDecl):

    @staticmethod
    def from_json(node):
        match node:
            case ["signal", *syms]:
                # check all symbols are string
                for p in syms:
                    assert isinstance(p, str), f"unsupported signal, got: {p}"
                _syms = [p for p in syms]
                return SclSignal(_syms)
            case _:
                raise NotImplementedError(f"unsupported json component, got: {node}")

    def __init__(self, _syms):
        super().__init__()
        self.syms = _syms

    def __str__(self):
        _syms = " ".join([str(p) for p in self.syms])
        return f"(signal {_syms})"

class SclVar(SclDecl):

    @staticmethod
    def from_json(node):
        match node:
            case ["var", *syms]:
                # check all symbols are string
                for p in syms:
                    assert isinstance(p, str), f"unsupported variable, got: {p}"
                _syms = [p for p in syms]
                return SclVar(_syms)
            case _:
                raise NotImplementedError(f"unsupported json component, got: {node}")

    def __init__(self, _syms):
        super().__init__()
        self.syms = _syms

    def __str__(self):
        _syms = " ".join([str(p) for p in self.syms])
        return f"(var {_syms})"

class SclAssign(SclStmt):

    @staticmethod
    def from_json(node):
        match node:
            case [":=", sym, expr]:
                assert isinstance(sym, str), f"unsupported node, got: {sym}"
                _sym = sym
                _expr = SclExpr.from_json(expr)
                return SclAssign(_sym, _expr)
            case _:
                raise NotImplementedError(f"unsupported json component, got: {node}")

    def __init__(self, _sym, _expr):
        super().__init__()
        self.sym = _sym
        self.expr = _expr

    def __str__(self):
        return f"(:= {self.sym} {self.expr})"

class SclEq(SclStmt):

    @staticmethod
    def from_json(node):
        match node:
            case ["eq", lhs, rhs]:
                _lhs = SclExpr.from_json(lhs)
                _rhs = SclExpr.from_json(rhs)
                return SclEq(_lhs, _rhs)
            case _:
                raise NotImplementedError(f"unsupported json component, got: {node}")

    def __init__(self, _lhs, _rhs):
        super().__init__()
        self.lhs = _lhs
        self.rhs = _rhs
    
    def __str__(self):
        return f"(eq {self.lhs} {self.rhs})"

# class SclFor(SclStmt):

#     @staticmethod
#     def from_json(node):
#         match node:
#             case ["for", sym, start, end, step, stmts]:
#                 assert isinstance(sym, str), f"unsupported node, got: {sym}"
#                 # NOTE: for now, the loop has to be boudned by constants only
#                 assert isinstance(start, str), f"unsupported node, got: {start}"
#                 assert isinstance(end, str), f"unsupported node, got: {end}"
#                 assert isinstance(step, str), f"unsupported node, got: {step}"
#                 _sym = sym
#                 _start = start
#                 _end = end
#                 _step = step
#                 _stmts = [SclStmt.from_json(p) for p in stmts]
#                 return SclFor(_sym, _start, _end, _step, _stmts)
#             case _:
#                 raise NotImplementedError(f"unsupported json component, got: {node}")

#     def __init__(self, _sym, _start, _end, _step, _stmts):
#         super().__init__()
#         self.sym = _sym
#         self.start = _start
#         self.end = _end
#         self.step = _step
#         self.stmts = _stmts

#     def __str__(self):
#         _iden = " "*self.iden
#         _stmts = "\n".join([f"{_iden}{p}" for p in self.stmts])
#         return f"(for {self.sym} {self.start} {self.end} {self.step}\n{_stmts}\n)"

class SclExpr(SclNode):

    @staticmethod
    def from_json(node):
        match node:
            case [op, *exprs]:
                _op = SclOperator.from_json(op)
                _exprs = [SclExpr.from_json(p) for p in exprs]
                assert _op.arity() == len(_exprs), f"arity mismatch, got: {_op.arity()} and {len(_exprs)}"
                return SclExpr(_op, _exprs)
            case obj if isinstance(obj, int):
                return obj
            case obj if isinstance(obj, str):
                return obj
            case _:
                raise NotImplementedError(f"unsupported json component, got: {node}")
    
    def __init__(self, _op, _exprs):
        super().__init__()
        self.op = _op
        self.exprs = _exprs

    def __str__(self):
        _exprs = " ".join([str(p) for p in self.exprs])
        return f"({self.op} {_exprs})"

class SclOperator(SclNode, Enum):

    EQ = 0
    NEQ = 1
    ADD = 2
    SUB = 3
    MUL = 4
    DIV = 5
    AND = 6
    OR = 7
    NOT = 8

    ITE = 9

    @staticmethod
    def from_json(node):
        match node:
            case "==":
                return SclOperator.EQ
            case "!=":
                return SclOperator.NEQ
            case "+":
                return SclOperator.ADD
            case "-":
                return SclOperator.SUB
            case "*":
                return SclOperator.MUL
            case "/":
                return SclOperator.DIV
            case "and":
                return SclOperator.AND
            case "or":
                return SclOperator.OR
            case "not":
                return SclOperator.NOT
            case "ite":
                return SclOperator.ITE
            case _:
                raise NotImplementedError(f"unsupported json component, got: {node}")
            
    def arity(self):
        match self.value:
            case SclOperator.EQ.value | SclOperator.NEQ.value | SclOperator.ADD.value | \
                 SclOperator.SUB.value | SclOperator.MUL.value | SclOperator.DIV.value | \
                 SclOperator.AND.value | SclOperator.OR.value | SclOperator.NOT.value:
                return 2
            case SclOperator.ITE.value:
                return 3
            case _:
                raise NotImplementedError(f"unsupported operator, got: {self.value}")
    
    def __str__(self):
        match self.value:
            case SclOperator.EQ.value:
                return "=="
            case SclOperator.NEQ.value:
                return "!="
            case SclOperator.ADD.value:
                return "+"
            case SclOperator.SUB.value:
                return "-"
            case SclOperator.MUL.value:
                return "*"
            case SclOperator.DIV.value:
                return "/"
            case SclOperator.AND.value:
                return "and"
            case SclOperator.OR.value:
                return "or"
            case SclOperator.NOT.value:
                return "not"
            case SclOperator.ITE.value:
                return "ite"
            case _:
                raise NotImplementedError(f"unsupported operator, got: {self.value}")