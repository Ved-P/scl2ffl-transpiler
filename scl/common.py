import sexpdata

from .scl import SclCircuit

def unwrap(obj):
    """unwrap symbol from sexp as string"""
    if isinstance(obj, list):
        return [unwrap(p) for p in obj]
    elif isinstance(obj, sexpdata.Symbol):
        return obj.value()
    elif isinstance(obj, int):
        return obj
    else:
        raise Exception(f"cannot unwrap given type, got: {obj}")
        
def parse_scl(raw: str):
    l = unwrap(sexpdata.loads(raw))
    o = SclCircuit.from_json(l)
    return o
