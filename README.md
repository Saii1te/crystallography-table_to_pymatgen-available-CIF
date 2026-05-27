# tables-to-cif

Convert crystallographic supplementary tables (Markdown / plain text,
typically `Table S1`–`S4` in journal SI) into a CIF file that
[`pymatgen.io.cif.CifParser`](https://pymatgen.org) can parse without
errors.

This repository is also packaged as an
[Anthropic Agent Skill](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills);
see [`SKILL.md`](SKILL.md) for the agent-facing manifest.

## Selection rules

When the source tables contain **multiple temperatures** or both
experimental and DFT-optimised hydrogen positions, the tool follows two
opinionated defaults:

1. **Prefer the temperature closest to 298 K** (room temperature).
   Ties are broken in favour of the higher temperature.
2. **Prefer experimental data over geometry-optimised data.​**
   Optimised hydrogens from `Table S4` are only used when (a) the user
   passes `--use-opt-h` explicitly, or (b) no experimental hydrogens
   exist for the chosen temperature.

Both defaults can be overridden from the CLI.

## Install

```bash
git clone https://github.com/<your-name>/tables-to-cif.git
cd tables-to-cif
pip install -e .[test]
```

Requires Python ≥ 3.10 and `pymatgen` for the verification step.

## Quick start

```bash
tables-to-cif parse  examples/nh4b4o6f.md  --out parsed.json
tables-to-cif build  parsed.json           --out NH4B4O6F.cif
tables-to-cif verify NH4B4O6F.cif
```

Or, equivalently, run the modules directly:

```bash
python -m tables_to_cif.parse_tables --input examples/nh4b4o6f.md --out parsed.json
python -m tables_to_cif.build_cif    parsed.json --out NH4B4O6F.cif
python -m tables_to_cif.verify_cif   NH4B4O6F.cif
```

Expected verification output for the bundled example:

```
OK
  reduced formula : H4NB4O6F
  lattice abc     : (7.602, 11.197, 6.5952)        # 296 K chosen, closest to 298 K
  space group     : ('Pna2_1', 33)
  hydrogen source : experimental (S4, 296 K)
```

## CLI options

| flag                | default        | meaning                                            |
|---------------------|----------------|----------------------------------------------------|
| `--temperature K`   | nearest to 298 | force a specific temperature dataset               |
| `--use-opt-h`       | off            | use S4 "geometry optimization" H instead of expt   |
| `--label-map JSON`  | `{}`           | override element inference per atom label          |
| `--out PATH`        | required       | output CIF or JSON path                            |

## Development

```bash
pip install -e .[test]
pytest -q
```

CI runs `pytest` on Python 3.10–3.12 (see `.github/workflows/ci.yml`).

## License

MIT — see [`LICENSE`](LICENSE).
