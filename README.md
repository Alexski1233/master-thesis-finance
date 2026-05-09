# Master Thesis Finance

This repository contains the Python code for my master's thesis.

The thesis looks at risk and leverage in large U.S. banks during the Basel III period. The main question is whether changes in Value-at-Risk are linked to changes in bank leverage, and whether regulation changes that relationship.

This is a research project, not a software package. The scripts are meant to be run from the project root.

## What is in the repo

- `src/pipeline/` contains the main scripts used to build the dataset, run the regressions, and make the figures.
- `src/validation/` contains checks and robustness scripts.
- `data/processed/` contains the final panel dataset when it is included.
- `output/tables/` contains regression and summary tables when they are included.
- `output/figures/` contains generated figures when they are included.

## How to run the project

Run the scripts in this order:

```bash
python src/pipeline/harmonize_var_to_99.py
python src/pipeline/build_bank_panel_dataset.py
python src/pipeline/generate_descriptive_statistics.py
python src/pipeline/run_panel_regressions.py
python src/pipeline/plot_var_to_equity_and_leverage.py
```

Validation checks:

```bash
python src/validation/validate_var_conversion_methods.py
python src/validation/calculate_vif_for_panel_models.py
python src/validation/lcr_sample.py
```

## Python packages

The project uses a standard data analysis setup:

```bash
pandas
numpy
matplotlib
scipy
statsmodels
linearmodels
openpyxl
```

## Notes

The scripts use relative paths, so they should be run from the repository root.
Some scripts overwrite files in `output/` when they are run again.
Raw Excel files and old unused files can be kept locally, but they do not need to be part of the active GitHub version.

## Author

Alexander Ski
