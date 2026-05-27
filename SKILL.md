---
name: tables-to-cif
description: >
  Convert crystallographic supplementary tables (Markdown or plain text,
  typically "Table S1 Crystal data", "Table S2 Atomic coordinates",
  "Table S3 Bond distances and angles", "Table S4 Hydrogen coordinates")
  into a CIF file that pymatgen.io.cif.CifParser can parse without
  errors. Trigger this skill whenever the user pastes such tables and
  asks for a CIF, a pymatgen Structure, or downstream crystallographic
  analysis.
license: MIT
---

# tables-to-cif

## When to use
Activate this skill if the user input contains any of:
- Headers like `Table S1`, `Crystal data`, `space group`, `Wyck.`,
  `x/a`, `U_eq`, `Bond distances`, `Hydrogen coordinates`.
- A request for `.cif`, `pymatgen Structure`, `VESTA`, `建模`,
  `导入`, `结构文件`, `crystallographic information file`.

## Selection rules (defaults)

These rules are enforced by `build_cif.py` and must be respected unless
the user overrides them:

1. **Temperature preference.​** When several temperatures are present
   (e.g. 296 K and 140 K in the same S1/S2/S4 tables), pick the one
   **closest to 298 K**. If two temperatures are equidistant from
   298 K, pick the **higher** one.
2. **Data-source preference.​** Always prefer **experimental** atomic
   positions over DFT / "geometry optimization" positions. Optimised
   coordinates (e.g. the `140 K data after geometry optimization` block
   in S4) are used only when:
   - the user passes `--use-opt-h`, **or**
   - no experimental hydrogens exist for the chosen temperature.

   Non-hydrogen sites (S2) are always taken from the experimental
   refinement.

The agent should mention the chosen temperature and hydrogen source in
its reply so the user can verify the selection.

## Inputs
- `--input PATH`           Markdown / plain-text source file.
- `--temperature K`        Force a specific dataset (overrides rule 1).
- `--use-opt-h`            Force optimised H (overrides rule 2).
- `--label-map JSON`       Override element inference, e.g.
                           `{"M1": "Na"}`.
- `--out PATH`             Output path.

## Workflow
1. `python -m tables_to_cif.parse_tables --input tables.md --out parsed.json`
2. Inspect `parsed.json`. The agent should surface the available
   temperatures and whether optimised H is present.
3. `python -m tables_to_cif.build_cif parsed.json --out structure.cif`
   The script prints the chosen temperature and hydrogen source.
4. `python -m tables_to_cif.verify_cif structure.cif`

## Conventions and gotchas
- Element symbol is inferred by stripping trailing digits from the atom
  label (`B1` → `B`, `Fe2A` → `Fe`).
- ESDs in parentheses are stripped: `7.602(2)` → `7.602`.
- Hydrogen labels with an obviously missing decimal point (fractional
  coord outside `[-1, 2]`) are auto-corrected with a WARNING.
- S3 (bonds/angles) is preserved as `#`-prefixed comments only;
  pymatgen recomputes geometry from coordinates anyway.
- For non-P1 structures, both `_symmetry_Int_Tables_number` and the
  `_symmetry_equiv_pos_as_xyz` loop are emitted to maximise parser
  compatibility.
