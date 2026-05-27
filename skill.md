---
name: tables-to-cif
description: >
  Convert crystallographic supplementary tables, in Markdown or plain text,
  typically including "Table S1 Crystal data", "Table S2 Atomic coordinates",
  "Table S3 Bond distances and angles", and "Table S4 Hydrogen coordinates",
  into a CIF file that pymatgen.io.cif.CifParser can parse without errors.
  Trigger this skill whenever the user pastes such tables and asks for a CIF,
  a pymatgen Structure, VESTA import, structure modeling, or downstream
  crystallographic analysis.
license: MIT
---

# tables-to-cif

## When to use

Activate this skill if the user input contains any of the following:

- Headers or terms such as `Table S1`, `Crystal data`, `space group`, `Wyck.`, `x/a`, `U_eq`, `Bond distances`, `Hydrogen coordinates`.
- Requests involving `.cif`, `pymatgen Structure`, `VESTA`, `建模`, `导入`, `结构文件`, or `crystallographic information file`.
- Crystallographic supplementary tables copied from a paper, PDF, image OCR result, Markdown table, or plain-text transcription.

## Inputs

- `--input PATH`  
  Markdown or plain-text file containing one or more of Tables S1–S4. Multiple temperatures in the same table are supported.

- `--temperature K` optional  
  Which temperature dataset to export when several temperatures coexist.

- `--use-opt-h` optional  
  Use the geometry-optimized hydrogen coordinates from S4 instead of the experimental hydrogen coordinates.

- `--label-map JSON` optional  
  Override element inference, for example `{"M1": "Na"}`.

- `--out PATH`  
  Output CIF file.

## Default selection rules

When multiple datasets are available and the user has not explicitly chosen one, apply the following rules in order:

1. Prefer the dataset with temperature closest to 298 K.
2. Prefer experimental atomic coordinates over geometry-optimized coordinates.
3. Prefer experimental hydrogen coordinates over geometry-optimized hydrogen coordinates.
4. If two or more experimental datasets are equally close to 298 K, ask the user which one to export before continuing.
5. If only geometry-optimized hydrogen coordinates are available, use them only after clearly noting that experimental hydrogen coordinates were not available.

These defaults are intended to produce the structure most comparable to standard room-temperature experimental crystallographic data, unless the user explicitly requests otherwise.

## Workflow

1. Parse the input tables.

   ```bash
   python scripts/parse_tables.py --input tables.md --out parsed.json
