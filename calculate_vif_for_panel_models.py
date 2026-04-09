"""Compute VIF diagnostics for the panel regression specifications."""

import pandas as pd
import numpy as np
import statsmodels.api as sm

# ============================================================
# 1) LOAD DATA
# ============================================================
DATA_PATH = "dataframe/dataframe.csv"   # Update the path if the dataset location changes.

df = pd.read_csv(DATA_PATH, parse_dates=["date"])
df = df.sort_values(["bank", "date"]).copy()

# ============================================================
# 2) RECREATE THE MODEL VARIABLES
# ============================================================
# Baseline leverage and unit VaR measures.
df["leverage"] = df["total_assets"] / df["total_equity"]
df["unitvar"]  = df["total_var"] / df["total_assets"]

# Log transforms used in the regression specifications.
if (df["leverage"] <= 0).any():
    raise ValueError("Fant leverage <= 0. Log kan ikke tas.")
if (df["unitvar"] <= 0).any():
    raise ValueError("Fant unitvar <= 0. Log kan ikke tas.")

df["ln_leverage"] = np.log(df["leverage"])
df["ln_unitvar"]  = np.log(df["unitvar"])

# Bank size proxy.
df["size"] = np.log(df["total_assets"])

# Group by bank before computing first differences and lags.
g = df.groupby("bank", group_keys=False)

df["dln_leverage"] = g["ln_leverage"].diff()
df["dln_unitvar"]  = g["ln_unitvar"].diff()
df["dsize"]        = g["size"].diff()
df["droa"]         = g["roa"].diff()

# Lagged variables used by the regression models.
for v in [
    "dln_leverage", "dln_unitvar",
    "size", "roa",
    "dsize", "droa",
    "lcr_ratio", "cet1_ratio", "slr_ratio"
]:
    df[f"{v}_l1"] = g[v].shift(1)

# Bank-group indicators.
MARKET_BANKS  = ["goldmansachs", "morganstanley"]
CUSTODY_BANKS = ["bny", "statestreet"]

df["market"]  = df["bank"].isin(MARKET_BANKS).astype(int)
df["custody"] = df["bank"].isin(CUSTODY_BANKS).astype(int)

# Interaction terms for the baseline and bank-group models.
df["dln_unitvar_l1_x_market"]  = df["dln_unitvar_l1"] * df["market"]
df["dln_unitvar_l1_x_custody"] = df["dln_unitvar_l1"] * df["custody"]

# Interaction terms for the regulatory-ratio models.
df["dln_unitvar_l1_x_lcr"]  = df["dln_unitvar_l1"] * df["lcr_ratio_l1"]
df["dln_unitvar_l1_x_cet1"] = df["dln_unitvar_l1"] * df["cet1_ratio_l1"]
df["dln_unitvar_l1_x_slr"]  = df["dln_unitvar_l1"] * df["slr_ratio_l1"]

# Quarter identifier used to partial out time fixed effects.
df["quarter_id"] = df["date"].dt.to_period("Q").astype(str)

# ============================================================
# 3) MODEL SPECIFICATIONS
# ============================================================
MODELS = {
    # ---------- H1-H2 ----------
    "H1H2_baseline": {
        "sample_start": "2010-03-31",
        "sample_end":   "2025-12-31",
        "xvars": ["dln_unitvar_l1", "size_l1", "roa_l1"],
        "bank_fe": True,
        "time_fe": True,
    },
    "H1H2_first_diff": {
        "sample_start": "2010-03-31",
        "sample_end":   "2025-12-31",
        "xvars": ["dln_unitvar_l1", "dsize_l1", "droa_l1"],
        "bank_fe": False,
        "time_fe": True,
    },
    "H1H2_adl": {
        "sample_start": "2010-03-31",
        "sample_end":   "2025-12-31",
        "xvars": ["dln_unitvar_l1", "dln_leverage_l1", "size_l1", "roa_l1"],
        "bank_fe": True,
        "time_fe": True,
    },
    "H1H2_group_fe": {
        "sample_start": "2010-03-31",
        "sample_end":   "2025-12-31",
        "xvars": [
            "dln_unitvar_l1",
            "dln_unitvar_l1_x_market",
            "dln_unitvar_l1_x_custody",
            "size_l1",
            "roa_l1"
        ],
        "bank_fe": True,
        "time_fe": True,
    },
    "H1H2_group_diff": {
        "sample_start": "2010-03-31",
        "sample_end":   "2025-12-31",
        "xvars": [
            "dln_unitvar_l1",
            "dln_unitvar_l1_x_market",
            "dln_unitvar_l1_x_custody",
            "dsize_l1",
            "droa_l1"
        ],
        "bank_fe": False,
        "time_fe": True,
    },

    # ---------- H3 ----------
    "H3_lcr": {
        "sample_start": "2015-03-31",
        "sample_end":   "2025-12-31",
        "xvars": [
            "dln_unitvar_l1",
            "lcr_ratio_l1",
            "dln_unitvar_l1_x_lcr",
            "size_l1",
            "roa_l1"
        ],
        "bank_fe": True,
        "time_fe": True,
    },
    "H3_cet1": {
        "sample_start": "2015-03-31",
        "sample_end":   "2025-12-31",
        "xvars": [
            "dln_unitvar_l1",
            "cet1_ratio_l1",
            "dln_unitvar_l1_x_cet1",
            "size_l1",
            "roa_l1"
        ],
        "bank_fe": True,
        "time_fe": True,
    },
    "H3_slr": {
        "sample_start": "2015-03-31",
        "sample_end":   "2025-12-31",
        "xvars": [
            "dln_unitvar_l1",
            "slr_ratio_l1",
            "dln_unitvar_l1_x_slr",
            "size_l1",
            "roa_l1"
        ],
        "bank_fe": True,
        "time_fe": True,
    },
}

# ============================================================
# 4) HELPER FUNCTIONS
# ============================================================
def residualize_on_fe(data, varname, bank_fe=False, time_fe=False):
    """
    Apply the Frisch-Waugh-Lovell step to remove bank and/or time fixed effects
    from a single variable.
    """
    y = data[varname].astype(float)

    fe_parts = []
    if bank_fe:
        fe_parts.append(pd.get_dummies(data["bank"], drop_first=True, dtype=float))
    if time_fe:
        fe_parts.append(pd.get_dummies(data["quarter_id"], drop_first=True, dtype=float))

    if not fe_parts:
        return y.copy()

    X_fe = pd.concat(fe_parts, axis=1)
    X_fe = sm.add_constant(X_fe, has_constant="add")

    fit = sm.OLS(y, X_fe).fit()
    return fit.resid


def vif_with_aux_regressions(data, xvars, bank_fe=False, time_fe=False):
    """
    Compute VIF using auxiliary regressions:
    1) residualize each regressor with respect to the selected fixed effects
    2) regress each residualized regressor on the remaining residualized regressors
    3) compute VIF_j = 1 / (1 - R²_j)
    """
    # Residualize each regressor with respect to the chosen fixed effects.
    X_resid = pd.DataFrame(index=data.index)
    for x in xvars:
        X_resid[x] = residualize_on_fe(data, x, bank_fe=bank_fe, time_fe=time_fe)

    rows = []
    for x in xvars:
        y_aux = X_resid[x]
        X_aux = X_resid.drop(columns=[x])
        X_aux = sm.add_constant(X_aux, has_constant="add")

        aux_fit = sm.OLS(y_aux, X_aux).fit()
        r2_aux = aux_fit.rsquared

        # Guard against numerical edge cases.
        if np.isclose(1 - r2_aux, 0):
            vif = np.inf
            tolerance = 0.0
        else:
            vif = 1.0 / (1.0 - r2_aux)
            tolerance = 1.0 - r2_aux

        rows.append({
            "variable": x,
            "R2_aux": r2_aux,
            "tolerance": tolerance,
            "VIF": vif
        })

    out = pd.DataFrame(rows).sort_values("VIF", ascending=False).reset_index(drop=True)
    return out


# ============================================================
# 5) RUN VIF FOR ALL MODELS
# ============================================================
all_results = []
max_vif_rows = []

for model_name, spec in MODELS.items():
    cols_needed = ["bank", "quarter_id", "date"] + spec["xvars"]

    d = df.loc[
        (df["date"] >= spec["sample_start"]) &
        (df["date"] <= spec["sample_end"]),
        cols_needed
    ].copy()

    d = d.dropna().reset_index(drop=True)

    vif_table = vif_with_aux_regressions(
        data=d,
        xvars=spec["xvars"],
        bank_fe=spec["bank_fe"],
        time_fe=spec["time_fe"]
    )

    vif_table.insert(0, "model", model_name)
    vif_table.insert(1, "N", len(d))

    all_results.append(vif_table)

    max_vif_rows.append({
        "model": model_name,
        "N": len(d),
        "max_VIF": vif_table["VIF"].max(),
        "mean_VIF": vif_table["VIF"].mean()
    })

# Combine model-level outputs into full summary tables.
vif_results = pd.concat(all_results, ignore_index=True)
vif_summary = pd.DataFrame(max_vif_rows).sort_values("max_VIF", ascending=False)

# ============================================================
# 6) PRINT AND SAVE RESULTS
# ============================================================
pd.set_option("display.max_rows", 200)
pd.set_option("display.max_columns", 20)
pd.set_option("display.width", 200)

print("\n" + "="*90)
print("VIF-RESULTATER FOR ALLE MODELLER")
print("="*90)
print(vif_results.round(4))

print("\n" + "="*90)
print("OPPSUMMERING")
print("="*90)
print(vif_summary.round(4))

# Save the detailed output and the model summary.
vif_results.to_csv("output/tables/vif_results_all_models.csv", index=False)
vif_summary.to_csv("output/tables/vif_summary_all_models.csv", index=False)
