"""
Time-window check of the proportional hazards assumption (post-hoc).

Added because the residual check in cox_analysis.py flagged sex and
ECOG 2 or higher. The Cox model is fitted twice: early follow-up
(day 0 to CUTOFF) and late follow-up (after CUTOFF). The hazard ratios are
then compared.

Reads data/analysis_data.csv.
Writes output/ph_window_check.csv and docs/ph_window_check.md.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.duration.hazard_regression import PHReg

Path("output").mkdir(exist_ok=True)
Path("docs").mkdir(exist_ok=True)

CUTOFF = 300  # days, roughly the median survival time of all patients
Z = 1.96

df = pd.read_csv("data/analysis_data.csv")
df = df[df["complete_case"].astype(bool)].copy()
df["age_10y"] = df["age"] / 10
df["ecog_1"] = (df["ph_ecog"] == 1).astype(float)
df["ecog_2plus"] = (df["ph_ecog"] >= 2).astype(float)

COLUMNS = ["female", "age_10y", "ecog_1", "ecog_2plus"]
LABELS = ["Female vs male", "Age, per 10 years",
          "ECOG 1 vs ECOG 0", "ECOG 2 or higher vs ECOG 0"]

# Early window: follow every patient only up to the cutoff
early = df.copy()
early["event"] = ((early["time"] <= CUTOFF) & (early["event"] == 1)).astype(int)
early["time"] = early["time"].clip(upper=CUTOFF)

# Late window: patients still followed at the cutoff; the clock restarts there
late = df[df["time"] > CUTOFF].copy()
late["time"] = late["time"] - CUTOFF


def fit(data):
    return PHReg(
        data["time"].to_numpy(dtype=float),
        data[COLUMNS].to_numpy(dtype=float),
        status=data["event"].to_numpy(dtype=int),
        ties="efron",
    ).fit()


def hr_text(result, i):
    b, se = result.params[i], result.bse[i]
    return f"{np.exp(b):.2f} ({np.exp(b - Z * se):.2f} to {np.exp(b + Z * se):.2f})"


def p_short(p):
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def md_table(frame):
    header = "| " + " | ".join(frame.columns) + " |"
    divider = "|" + "|".join(["---"] * len(frame.columns)) + "|"
    rows = ["| " + " | ".join(str(v) for v in row) + " |"
            for row in frame.itertuples(index=False)]
    return "\n".join([header, divider] + rows)


early_fit, late_fit = fit(early), fit(late)
n_early, d_early = len(early), int(early["event"].sum())
n_late, d_late = len(late), int(late["event"].sum())
print(f"Early window (day 0 to {CUTOFF}): {n_early} patients, {d_early} deaths")
print(f"Late window (after day {CUTOFF}): {n_late} patients, {d_late} deaths\n")

rows = []
for i, label in enumerate(LABELS):
    b1, se1 = early_fit.params[i], early_fit.bse[i]
    b2, se2 = late_fit.params[i], late_fit.bse[i]
    diff = b2 - b1
    se_diff = np.sqrt(se1 ** 2 + se2 ** 2)
    p_diff = 2 * (1 - stats.norm.cdf(abs(diff / se_diff)))
    rows.append({
        "Variable": label,
        f"HR early (day 0 to {CUTOFF})": hr_text(early_fit, i),
        f"HR late (after day {CUTOFF})": hr_text(late_fit, i),
        "Ratio of HRs, late vs early (95% CI)":
            f"{np.exp(diff):.2f} ({np.exp(diff - Z * se_diff):.2f} to {np.exp(diff + Z * se_diff):.2f})",
        "p for difference": p_short(p_diff),
    })
table = pd.DataFrame(rows)
table.to_csv("output/ph_window_check.csv", index=False)
print(table.to_string(index=False))

report = f"""# Time-window check of proportional hazards

This is a post-hoc sensitivity analysis. It was added after the residual check in `cox_analysis.py` flagged sex and ECOG 2 or higher (see the changes table in the [analysis plan](statistical_analysis_plan.md)).

The Cox model (Model 2) was fitted separately for early follow-up (day 0 to {CUTOFF}) and late follow-up (after day {CUTOFF}). If the hazard ratio is about the same in both windows, the proportional hazards assumption is reasonable.

- Early window: {n_early} patients, {d_early} deaths
- Late window: {n_late} patients, {d_late} deaths

{md_table(table)}

## How to read this

- A ratio of hazard ratios near 1, with an interval that includes 1, gives no sign that the effect changed over time.
- A ratio clearly away from 1 means the effect differs between early and late follow-up. In that case the single hazard ratio in the main analysis is an average, and both windows should be reported.
- The late window has fewer deaths, so the test has limited power. Failing to find a difference does not prove that there is none.
- The cutoff was chosen as a round number near the median survival. A different cutoff could give somewhat different results.
"""
Path("docs/ph_window_check.md").write_text(report, encoding="utf-8")
print("\nSaved: output/ph_window_check.csv, docs/ph_window_check.md")