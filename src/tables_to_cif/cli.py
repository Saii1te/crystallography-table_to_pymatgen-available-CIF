"""Single entry point: `tables-to-cif {parse,build,verify} ...`."""
from __future__ import annotations
import argparse, sys

from . import parse_tables, build_cif, verify_cif


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="tables-to-cif")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("parse",  help="parse Markdown tables -> JSON",
                   add_help=False)
    sub.add_parser("build",  help="JSON -> CIF",  add_help=False)
    sub.add_parser("verify", help="round-trip CIF through pymatgen",
                   add_help=False)
    args, rest = ap.parse_known_args(argv)
    return {
        "parse":  parse_tables.main,
        "build":  build_cif.main,
        "verify": verify_cif.main,
    }[args.cmd](rest)


if __name__ == "__main__":
    sys.exit(main())
