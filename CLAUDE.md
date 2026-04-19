# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Agent-based model (ABM) of chronic lymphocytic leukemia (CLL) and its tumor microenvironment, built on the PhysiCell/BioFVM framework. The model simulates 2D tissue dynamics over 13 days with six cell types (CLL, monocytes, macrophages, NLCs, apoptotic, dead) and three diffusive signaling fields (cytokines, antiapoptotic, stress).

## Build & Run

```bash
# Compile
make

# Run single simulation
./project config/NLC_CLL.xml

# Clean build artifacts
make clean

# Clear output directory
make data-cleanup

# Batch run (N iterations, randomized seeds, saves CSVs to data/)
python scripts/run_model.py <N>
```

## Key Configuration Files

| File | Purpose |
|------|---------|
| `config/NLC_CLL.xml` | Master config: domain (1000×1000 µm), substrates, all cell type phenotypes |
| `config/rules0.csv` | CBHG signal→behavior rules (16 rules, evaluated every 6 min) |
| `config/cells.csv` | Initial cell positions (~4000 CLL + ~200 myeloid); overrides random placement |
| `config/parameters.txt` | Runtime overrides (e.g., `random_seed`) |

## Architecture

```
BioFVM (diffusion solver)  →  3 substrates on a 20µm voxel mesh
        ↓
Cell Container (6 types)   →  phenotype: motility, secretion, phagocytosis, transformation
        ↓
Rules Engine (CBHG)        →  CSV rules map signal levels → behavior rate changes
        ↓
custom_modules/custom.cpp  →  create_cell_types(), setup_tissue(), callbacks
```

**Main loop** (`main.cpp`): each diffusion_dt (0.01 min) — solve diffusion → update cell mechanics → apply phenotype/rules → advance time. Snapshots saved every 60 min as MultiCellDS XML + SVG.

**Rules engine**: `config/rules0.csv` is parsed at startup into PhysiCell's signal/behavior dictionaries. Each row: `cell_type, signal, direction, behavior, parameters`. Key rules:
- CLL: stress → apoptosis; antiapoptotic signal → blocks apoptosis; NLC contact → reduced migration
- Monocytes: cytokines → transform to macrophages; intracellular signals → transform to NLCs
- NLCs: cancer contact → secrete antiapoptotic signal

**Cell seeding**: `custom.cpp` loads positions from `cells.csv` via `load_cells_from_pugixml()`; the XML `number_of_cells=0` for all types suppresses random placement.

**Internalized substrate tracking** (`track_internalized_substrates_in_each_agent=true` in XML) enables rules to evaluate intracellular signal levels (e.g., intracellular cytokines trigger monocyte→NLC transformation).

## Analysis Scripts

- `scripts/collect_data.py` — extracts metrics from MultiCellDS snapshots using `pcdl` library; calculates CLL viability = alive/(alive+apoptotic+dead)×100% and CLL concentration = total/initial×100%
- `scripts/run_model.py` — batch runner: modifies XML seed in-memory per iteration, calls `./project`, aggregates 5 CSVs (viability, concentration, monocytes, macrophages, NLCs)
- `scripts/model_post_analysis.ipynb` — plotting and statistical analysis of batch results
- `scripts/model_analysis_pcdl.ipynb` — spatial/substrate analysis using pcdl

## Output

Snapshots saved to `output/` every 60 min: `output_NNNNNNNN.xml` (MultiCellDS cell state) + `snapshot_NNNNNNNN.svg` (2D visualization at z=0).
