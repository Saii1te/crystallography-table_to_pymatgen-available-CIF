"""Parse Markdown / plain-text crystallographic tables into a dict."""
from __future__ import annotations
import argparse, json, logging, re, sys
from pathlib import Path

log = logging.getLogger("tables_to_cif.parse")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

NUM_ESD = re.compile(r"-?\d+\.?\d*(?:$\d+$)?")
TEMP_HEADER = re.compile(r"^\s*\|?\s*(\d{2,4})\s*K\s*\|?\s*$")
SG_PATTERN = re.compile(
    r"([A-Z][a-z\-/0-9_ ]*?\d*)\s*$?\s*No\.?\s*(\d+)\s*$?", re.I)


def strip_esd(token: str) -> float:
    token = token.strip().replace(" ", "")
    m = re.match(r"(-?\d+\.?\d*)(?:$\d+$)?$", token)
    if not m:
        raise ValueError(f"cannot parse numeric token: {token!r}")
    raw = m.group(1)
    v = float(raw)
    if "." not in raw and abs(v) > 5:
        digits = raw.lstrip("-")
        fixed = float(f"{digits[0]}.{digits[1:]}")
        if v < 0:
            fixed = -fixed
        log.warning("auto-fixing %s -> %s (likely missing decimal point)",
                    token, fixed)
        return fixed
    return v


def split_row(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        cells = [c.strip() for c in line.strip("|").split("|")]
    else:
        cells = re.split(r"\s{2,}|	", line)
    return [c for c in cells if c]


def infer_element(label: str) -> str:
    m = re.match(r"([A-Z][a-z]?)", label)
    if not m:
        raise ValueError(f"cannot infer element from label: {label!r}")
    return m.group(1)


def parse_s1(block: str) -> dict:
    cell: dict = {"a": [], "b": [], "c": [], "V": [], "T": []}
    sg_symbol = sg_number = None
    formula = None
    for line in block.splitlines():
        low = line.lower().strip().lstrip("|").strip()
        if low.startswith(("a /", "a/")):
            cell["a"] = [strip_esd(t) for t in NUM_ESD.findall(line)]
        elif low.startswith(("b /", "b/")):
            cell["b"] = [strip_esd(t) for t in NUM_ESD.findall(line)]
        elif low.startswith(("c /", "c/")):
            cell["c"] = [strip_esd(t) for t in NUM_ESD.findall(line)]
        elif "volume" in low:
            cell["V"] = [strip_esd(t) for t in NUM_ESD.findall(line)]
        elif "temperature" in low:
            cell["T"] = [int(strip_esd(t)) for t in NUM_ESD.findall(line)]
        elif "space group" in low:
            m = SG_PATTERN.search(line)
            if m:
                sg_symbol = m.group(1).strip()
                sg_number = int(m.group(2))
        elif "empirical formula" in low:
            cells = split_row(line)
            if len(cells) >= 2:
                formula = cells[-1]
    cell["alpha"] = cell["beta"] = cell["gamma"] = 90.0
    cell["sg_symbol"] = sg_symbol or "P 1"
    cell["sg_number"] = sg_number or 1
    if formula:
        cell["formula"] = formula
    return cell


def parse_atom_block(block: str, with_u: bool = True) -> dict[int, list[dict]]:
    sites: dict[int, list[dict]] = {}
    current_T: int | None = None
    opt_flag = False
    for raw in block.splitlines():
        line = raw.rstrip()
        if not line.strip():
            continue
        line = re.sub(r"-\s+(?=\d)", "-", line)
        m = TEMP_HEADER.match(line)
        if m:
            current_T = int(m.group(1))
            sites.setdefault(current_T, [])
            opt_flag = False
            continue
        if "geometry optimization" in line.lower():
            current_T = -1
            sites.setdefault(-1, [])
            opt_flag = True
            continue
        cells = split_row(line)
        if not cells or not re.match(r"[A-Z][a-z]?\d+\w*$", cells[0]):
            continue
        label = cells[0]
        nums = [c for c in cells[1:] if NUM_ESD.fullmatch(c.replace(" ", ""))]
        if len(nums) < 3:
            continue
        x, y, z = (strip_esd(t) for t in nums[:3])
        u = strip_esd(nums[3]) if (with_u and len(nums) >= 4) else 0.02
        wyck = next((c for c in cells[1:] if re.fullmatch(r"\d+[a-z]", c)), "")
        site = {
            "label": label,
            "element": infer_element(label),
            "wyck": wyck,
            "xyz": [x, y, z],
            "u_eq": u,
            "optimised": opt_flag,
        }
        if current_T is None:
            current_T = 0
            sites.setdefault(0, [])
        sites[current_T].append(site)
    return sites


def split_tables(text: str) -> dict[str, str]:
    parts = re.split(r"(?im)^(\s*Table\s+S(\d+)[^
]*)$", text)
    out: dict[str, str] = {}
    for i in range(1, len(parts) - 1, 3):
        out[f"S{parts[i + 1]}"] = parts[i + 2]
    return out


def parse_text(text: str) -> dict:
    """Pure-string entry point used by tests and the CLI."""
    tables = split_tables(text)
    if not tables:
        raise ValueError("no 'Table Sn' headers found")
    data: dict = {}
    if "S1" in tables:
        data["cell"] = parse_s1(tables["S1"])
    if "S2" in tables:
        data["sites"] = parse_atom_block(tables["S2"], with_u=True)
    if "S4" in tables:
        h = parse_atom_block(tables["S4"], with_u=False)
        data["hydrogens"] = {k: v for k, v in h.items() if k != -1}
        data["hydrogens_opt"] = h.get(-1, [])
    if "S3" in tables:
        data["bonds_raw"] = tables["S3"].strip()
    return data


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="tables-to-cif parse")
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--out", default=Path("parsed.json"), type=Path)
    args = ap.parse_args(argv)
    data = parse_text(args.input.read_text(encoding="utf-8"))
    args.out.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    log.info("wrote %s", args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
