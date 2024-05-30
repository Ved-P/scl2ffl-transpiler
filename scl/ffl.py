from enum import Enum

class FflNode:
    """primitive node type"""

    # NOTE: need both args and kwargs as child class also inherits Enum
    def __init__(self, *args, **kwargs):
        self.iden = 2

class FflBlock(FflNode):

    def __init__(self, _equations):
        super().__init__()
        self.equations = _equations

    def __str__(self):
        return "\n".join([str(p) for p in self.equations])

class FflEquation(FflNode):

    def __init__(self, _lhs, _rhs):
        super().__init__()
        self.lhs = _lhs
        self.rhs = _rhs

    def __str__(self):
        return f"{self.lhs} = {self.rhs}"

class FflExpr(FflNode):

    def __init__(self, _op, _exprs):
        super().__init__()
        self.op = _op
        self.exprs = _exprs

    def __str__(self):
        match self.op:
            case FflOperator.SIGNAL | FflOperator.VAR:
                return f"{self.op}()"
            case FflOperator.MUL:
                # add () if add happens before mul
                return f" {self.op} ".join([
                    f"({p})" if isinstance(p, FflExpr) and p.op in {FflOperator.ADD, FflOperator.SUB} else f"{p}"
                    for p in self.exprs
                ])
            case FflOperator.ADD | FflOperator.SUB:
                return f" {self.op} ".join([str(p) for p in self.exprs])
            case _:
                raise NotImplementedError(f"unsupported operator, got: {self.op}")

class FflOperator(FflNode, Enum):

    SIGNAL = 0
    VAR = 1
    ADD = 2
    SUB = 3
    MUL = 4

    def arity(self):
        match self.value:
            case FflOperator.SIGNAL.value | FflOperator.VAR.value:
                return 0
            case FflOperator.ADD.value | FflOperator.SUB.value | FflOperator.MUL.value:
                return 2
            case _:
                raise NotImplementedError(f"unsupported operator, got: {self.value}")
    
    def __str__(self):
        match self.value:
            case FflOperator.SIGNAL.value:
                return "signal"
            case FflOperator.VAR.value:
                return "var"
            case FflOperator.ADD.value:
                return "+"
            case FflOperator.SUB.value:
                return "-"
            case FflOperator.MUL.value:
                return "*"
            case _:
                raise NotImplementedError(f"unsupported operator, got: {self.value}")
