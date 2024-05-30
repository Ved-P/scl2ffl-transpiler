import sys

from scl.common import parse_scl
from scl.compile import compile

if __name__ == "__main__":
    
    assert len(sys.argv)-1 == 1, \
        f"Invalid number of arguments, expected: 1, got: {len(sys.argv)-1}"


    fpath = sys.argv[1]
    with open(fpath, "r") as f:
        raw = f.read()
        obj = parse_scl(raw)
    
    out = compile(obj)
    print(f"{out}")