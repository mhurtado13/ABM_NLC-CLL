# ABM NLC-CLL (PhysiCell-Based Model)

Agent-based model (ABM) of CLL and microenvironment interactions built on PhysiCell/BioFVM.

This repository is a custom PhysiCell project with:
- CLL-related cell populations (cancer, monocytes, macrophages, NLCs, apoptotic, dead)
- Diffusive signaling fields (cytokines, antiapoptotic, stress)
- Cell behavior rules loaded from CSV (CBHG rules)

## Overview

The simulation represents interactions among CLL cells and immune/stromal-like populations in a 2D tissue domain.

Core runtime flow:
1. Load XML configuration.
2. Initialize substrates (BioFVM).
3. Initialize cell definitions and rules.
4. Seed cells from CSV initial conditions.
5. Simulate diffusion + cell updates over time.
6. Save snapshots to `output/`.

Relevant implementation files:
- `main.cpp`: entry point, simulation loop, outputs
- `custom_modules/custom.cpp`: cell setup, rule initialization, tissue seeding
- `config/NLC_CLL.xml`: model/domain/cell definitions and file wiring
- `config/rules0.csv`: behavior rules
- `config/cells.csv`: initial cell positions and cell types

## Model Configuration (What Is Simulated)

Primary config file: `config/NLC_CLL.xml`

### Domain and Timing
- 2D domain (`use_2D=true`), box: x/y from -500 to 500 microns, z thin slab
- Duration: `max_time = 18720 min` (13 days)
- Time steps:
	- diffusion: `dt_diffusion = 0.01 min`
	- mechanics: `dt_mechanics = 0.1 min`
	- phenotype: `dt_phenotype = 6 min`
- Parallel threads: `omp_num_threads = 4`

### Microenvironment Substrates
The model defines three diffusive signals:
1. `cytokines`
2. `antiapoptotic`
3. `stress`

These appear in `microenvironment_setup` and are used by chemotaxis, secretion/uptake, and cell rules.

### Cell Agents (Types and Characteristics)

Defined in `<cell_definitions>`:
1. `cancer`
2. `monocytes`
3. `macrophages`
4. `NLCs`
5. `apoptotic`
6. `dead`

Key characteristics by type (from `config/NLC_CLL.xml`):
- `cancer`
	- motile (`speed=1`), chemotaxis toward `antiapoptotic`
	- secretes cytokines, uptakes antiapoptotic
	- baseline transformation toward apoptotic state exists
- `monocytes`
	- slow motility (`speed=0.1`), chemotaxis toward `stress`
	- uptake of cytokines/stress
	- phagocytosis of apoptotic/dead cells
	- can transform to `macrophages` and `NLCs` (rule-modulated)
- `macrophages`
	- similar motility pattern to monocytes
	- phagocytosis of apoptotic/dead cells
	- can attack cancer and induce damage
	- can transform to `NLCs` (rule-modulated)
- `NLCs`
	- motile, chemotaxis toward stress
	- antiapoptotic secretion (important for CLL survival support)
	- moderate phagocytosis and adhesive interactions
- `apoptotic` and `dead`
	- represent CLL progression states and debris-like populations
	- feed back into stress/cytokine dynamics and phagocytic behaviors

### Initial Conditions

Configured under `<initial_conditions>`:
- cell positions loaded from CSV:
	- folder: `config`
	- filename: `cells.csv`

In this project, this CSV seeding is the practical initializer (the generic `number_of_cells` parameter is set to `0`, so random per-type placement in `custom.cpp` is effectively disabled by default).

## Rules (CBHG) and Their Meaning

Rules are enabled in XML via:
- `<cell_rules><rulesets><ruleset ... format="csv" ...>`
- loaded from `config/rules0.csv`

The parsed rule summary is visible in `output/detailed_rules.txt` after running.

Main rules in this model:

### Cancer
- contact with NLCs decreases migration speed
- damage increases transform to apoptotic
- antiapoptotic decreases transform to apoptotic

### Monocytes
- stress increases phagocytose apoptotic
- stress increases phagocytose dead
- cytokines increases transform to macrophages
- intracellular stress increases transform to NLCs
- intracellular cytokines increases transform to NLCs

### Macrophages
- stress increases phagocytose apoptotic
- stress increases phagocytose dead
- intracellular stress increases transform to NLCs
- intracellular cytokines increases transform to NLCs

### NLCs
- stress increases phagocytose apoptotic
- stress increases phagocytose dead
- contact with cancer increases antiapoptotic secretion

Interpretation: NLC contact and antiapoptotic signaling support CLL survival, while stress/cytokine pathways regulate myeloid-to-NLC transitions and clearance phenotypes.

## Build and Run

These commands follow normal PhysiCell usage patterns from the official MathCancer repository (compile with `make`, clean with `make clean`, clear outputs with `make data-cleanup`) adapted to this project.

### Requirements
- Linux/macOS
- `g++` with OpenMP support
- `make`
- Optional (post-processing): Python 3 + packages used in `scripts/`

### Compile

```bash
make clean
make
```

This creates executable `project` (see `PROGRAM_NAME := project` in `Makefile`).

### Run with this model config

```bash
./project config/NLC_CLL.xml
```

Important: this repository does not rely on the default `./config/PhysiCell_settings.xml` at launch. Pass `config/NLC_CLL.xml` explicitly.

### Clean output data

```bash
make data-cleanup
```

### Useful additional targets

```bash
make clean          # remove objects and executable
make jpeg           # convert SVG snapshots to JPG (ImageMagick required)
make movie          # build MP4 from snapshots (ffmpeg required)
```

## Outputs

Simulation outputs are written to `output/`, including:
- `initial.svg`, `final.svg`
- `output00000000.xml`-style MultiCellDS snapshots
- `detailed_rules.txt` and `detailed_rules.html`
- `dictionaries.txt` (signals and behaviors dictionary)

## Batch Runs and Data Collection

Example script:
- `scripts/run_model.py`

It runs multiple iterations and writes aggregate CSV metrics into `data/`.

Example:
```bash
python scripts/run_model.py 10
```

This uses:
- `scripts/collect_data.py`
- `config/NLC_CLL.xml`
- output snapshots in `output/`

## Relation to Official PhysiCell (MathCancer)

This project follows the standard PhysiCell project structure and Makefile workflow from:
- https://github.com/MathCancer/PhysiCell

In particular:
- `make` compiles
- `make clean` removes build artifacts
- `make data-cleanup` resets output data

The main difference is model-specific configuration and rules:
- XML: `config/NLC_CLL.xml`
- rules: `config/rules0.csv`
- initial cell layout: `config/cells.csv`

## Citation

If you use this model, cite PhysiCell and BioFVM as requested in source headers (`main.cpp`, `custom_modules/custom.cpp`).

Primary PhysiCell reference:
- Ghaffarizadeh A, Heiland R, Friedman SH, Mumenthaler SM, Macklin P. PhysiCell: an Open Source Physics-Based Cell Simulator for Multicellular Systems. PLoS Comput Biol. 2018;14(2):e1005991.
