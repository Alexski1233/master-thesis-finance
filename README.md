# Risk, Leverage and Capital Structure under the Basel III Regime

## Key Takeaways (for recruiters)

- Built a quarterly panel dataset for 8 U.S. G-SIB banks (2010–2025)
- Conducted panel regressions with fixed effects and clustered standard errors
- Tested the Adrian–Shin risk–leverage mechanism under Basel III constraints
- Found weaker procyclicality and evidence that the Supplementary Leverage Ratio constrains leverage adjustment
- Implemented full pipeline in Python (data cleaning, transformation, regression, diagnostics)
This repository contains the data pipeline, validation scripts, figures, and regression code used in the master's thesis:

*Risk, Leverage and Capital Structure under the Basel III Regime: An extension of Adrian & Shin's framework to the Basel III period*

The project studies whether the procyclical risk-leverage mechanism documented by Adrian and Shin remains empirically relevant for large U.S. banks in the Basel III era. Using quarterly panel data for eight U.S. G-SIBs from 2010 to 2025, the analysis tests whether changes in Value-at-Risk are associated with short-run leverage adjustment, and whether this relationship is moderated by key Basel III constraints such as the Supplementary Leverage Ratio, CET1, and the Liquidity Coverage Ratio.

## Project Overview

The empirical workflow in this repository has four main steps:

1. Build a quarterly bank panel from raw balance sheet workbooks.
2. Harmonize VaR observations to a comparable 99% confidence level.
3. Generate descriptive statistics, validation outputs, figures, and regression tables.
4. Evaluate multicollinearity and compare alternative VaR conversion methods.

The repo focuses on reproducible empirical analysis rather than application packaging. Most scripts are designed to be run as standalone research scripts.

## Repository Structure

```text
.
├── dataframe/
│   ├── Balansesheet_v2/              # Raw bank-specific Excel workbooks
│   ├── build_bank_panel_dataset.py   # Builds the merged quarterly panel
│   └── dataframe.csv                 # Output panel used by downstream scripts
├── data/
│   ├── raw/
│   │   ├── VaR_python.xlsx           # Raw VaR source
│   │   └── VIXCLS (1).csv            # VIX series used in descriptive statistics
│   └── processed/
│       ├── balance_sheet_panel_balanced.csv
│       └── balance_sheet_panel_unbalanced.csv
├── output/
│   ├── data/                         # Derived datasets
│   ├── figures/                      # Validation and analysis figures
│   └── tables/                       # Descriptive statistics and regression tables
├── src/
│   ├── pipeline/                     # Main empirical pipeline
│   └── validation/                   # Validation and diagnostics
└── README.md
```

## Main Scripts

### Data Construction

- `dataframe/build_bank_panel_dataset.py`
  Builds the quarterly panel dataset by extracting balance sheet and financial variables from bank-specific Excel files and merging them with harmonized VaR data.

- `src/pipeline/harmonize_var_to_99.py`
  Reads the raw VaR workbook and converts bank-level VaR observations to comparable 99% VaR measures using both Gaussian scaling and a Bank of America empirical scaling factor.

### Descriptive Analysis

- `src/pipeline/generate_descriptive_statistics.py`
  Produces the descriptive statistics table used in the thesis, including balance sheet variables, growth rates, regulatory ratios, payout variables, return on assets, and VIX.

### Figures

- `src/pipeline/plot_var_to_equity_and_leverage.py`
  Produces a Figure 5-style plot of Unit VaR, leverage, and VaR-to-equity over time. The script standardizes each series relative to a pre-period and aggregates across banks using lagged asset weights.

### Regression Analysis

- `src/pipeline/run_panel_regressions.py`
  Runs the main panel regression specifications with fixed effects, lag structures, interaction terms, and both clustered and robust standard errors. Exports publication-style result tables to `output/tables/`.

### Validation and Diagnostics

- `src/validation/validate_var_conversion_methods.py`
  Compares alternative methods for converting VaR(95%) to VaR(99%) using Bank of America observations from the raw Excel source.

- `src/validation/calculate_vif_for_panel_models.py`
  Computes VIF diagnostics for the regression specifications after partialling out fixed effects where relevant.

## Data

The analysis uses quarterly observations for eight major U.S. banks:

- Bank of America
- BNY Mellon
- Citigroup
- Goldman Sachs
- JPMorgan Chase
- Morgan Stanley
- State Street
- Wells Fargo

The repository combines three main data components:

- Bank-level balance sheet and financial statement data from Excel workbooks in `dataframe/Balansesheet_v2/`
- VaR observations from `data/raw/VaR_python.xlsx`
- VIX data from `data/raw/VIXCLS (1).csv`

## Typical Workflow

Run the scripts in this order if you want to reproduce the main outputs:

```bash
python dataframe/build_bank_panel_dataset.py
python src/pipeline/harmonize_var_to_99.py
python src/pipeline/generate_descriptive_statistics.py
python src/validation/validate_var_conversion_methods.py
python src/pipeline/run_panel_regressions.py
python src/validation/calculate_vif_for_panel_models.py
python src/pipeline/plot_var_to_equity_and_leverage.py
```

Depending on your environment, you may need a standard scientific Python stack including:

- `pandas`
- `numpy`
- `matplotlib`
- `scipy`
- `statsmodels`
- `linearmodels`
- `openpyxl`

## Main Outputs

Key generated files include:

- `output/data/var_99.csv`
- `output/tables/descriptive_statistics.csv`
- `output/tables/regression_results_clustered_SE.csv`
- `output/tables/regression_results_robust_SE.csv`
- `output/tables/vif_results_all_models.csv`
- `output/tables/vif_summary_all_models.csv`
- `output/figures/boa_validation_comprehensive_excel.png`

## Main Research Finding

Consistent with the thesis, the empirical results in this repository suggest that the classic Adrian-Shin risk-leverage mechanism is weaker in the Basel III period than in earlier pre-crisis settings. Short-run changes in VaR are not robustly associated with leverage adjustment in the originally predicted direction across the full sample, while the Supplementary Leverage Ratio appears to be the most important regulatory moderator among the Basel III measures tested.

## Notes

- This is a research repository built around a thesis workflow, so several scripts are intended to be executed directly rather than imported as a package.
- File paths are currently configured relative to the repository root.
- Some outputs depend on the availability of locally stored Excel source files.

## Author

Alexander Ski  
Master's thesis in Economics and Finance  
Norwegian University of Science and Technology (NTNU)
