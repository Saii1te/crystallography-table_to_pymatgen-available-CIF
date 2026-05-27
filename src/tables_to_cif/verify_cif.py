"""Round-trip the generated CIF through pymatgen."""
from __future__ import annotations
import argparse, sys
from pathlib import Path

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="tables-to-cif verify")
    ap.add_argument("cif", type=Path)
    args = ap.parse_args(argv)

    from pymatgen.io.cif import CifParser  # imported lazily for fast --help
    structures = CifParser(str(args.cif)).parse_structures(primitive=False)
    if not structures:
        print("FAIL: pymatgen returned no structures", file=sys.stderr)
        return 1
    s = structures[0]
    print("OK")
    print(f"  reduced formula : {s.composition.reduced_formula}")
    print(f"  full formula    : {s.composition.formula}")
    print(f"  lattice abc     : {tuple(round(x, 4) for x in s.lattice.abc)}")
    print(f"  lattice angles  : {tuple(round(x, 3) for x in s.lattice.angles)}")
    print(f"  num sites       : {len(s)}")
    print(f"  space group     : {s.get_space_group_info()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
