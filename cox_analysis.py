"""
Phase 4: Cox proportional hazards regression.

Reads data/analysis_data.csv (created by prepare_data.py).
Writes output/cox_results.csv, output/ph_check.csv, images/forest_plot.png,
images/loglog_by_sex.png and docs/cox_results.md.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.duration.hazard_regression import PHReg
from statsmodels.duration.survfunc import SurvfuncRight

for folder in ["images", "output", "docs"]:
    Path(folder).mkdir(exist_ok=True)

df = pd.read_csv("data/analysis_data.csv")

# ---------- Variables ----------
df["age_10y"] = df["age"] / 10  # age in units of 10 years
ecog_known = df["ph_ecog"].notna()
df["ecog_1"] = np.where(ecog_known, (df["ph_ecog"] == 1).astype(float), np.nan)
df["ecog_2plus"] = np.where(ecog_known, (df["ph_ecog"] >= 2).astype(float), np.nan)
complete = df[df["complete_case"].astype(bool)].copy()
print(f"All patients: {len(df)}. Complete cases for the adjusted model: {len(complete)}\n")


def p_phrase(p):
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"


def p_short(p):
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def md_table(frame):
    header = "| " + " | ".join(frame.columns) + " |"
    divider = "|" + "|".join(["---"] * len(frame.columns)) + "|"
    rows = ["| " + " | ".join(str(v) for v in row) + " |"
            for row in frame.itertuples(index=False)]
    return "\n".join([header, divider] + rows)


def fit_cox(data, columns):
    model = PHReg(
        data["time"].to_numpy(dtype=float),
        data[columns].to_numpy(dtype=float),
        status=data["event"].to_numpy(dtype=int),
        ties="efron",
    )
    return model.fit()


# ---------- Models ----------
M1 = "Model 1: sex only (all patients)"
M1C = "Model 1 repeated on the complete cases"
M2 = "Model 2: sex, age and ECOG (complete cases)"
S1 = "Secondary: ECOG 2 or higher vs 0-1, unadjusted"
S2 = "Secondary: ECOG 2 or higher vs 0-1, adjusted for sex and age"

specs = [
    (M1, df, ["female"], ["Female vs male"]),
    (M1C, complete, ["female"], ["Female vs male"]),
    (M2, complete, ["female", "age_10y", "ecog_1", "ecog_2plus"],
     ["Female vs male", "Age, per 10 years", "ECOG 1 vs ECOG 0", "ECOG 2 or higher vs ECOG 0"]),
    (S1, complete, ["ecog_2plus"], ["ECOG 2 or higher vs ECOG 0-1"]),
    (S2, complete, ["ecog_2plus", "female", "age_10y"],
     ["ECOG 2 or higher vs ECOG 0-1", "Female vs male", "Age, per 10 years"]),
]

rows, fits = [], {}
for name, data, columns, labels in specs:
    res = fit_cox(data, columns)
    fits[name] = (res, data, columns, labels)
    ci = np.asarray(res.conf_int())
    for i, label in enumerate(labels):
        rows.append({
            "model": name, "variable": label,
            "HR": float(np.exp(res.params[i])),
            "CI_low": float(np.exp(ci[i, 0])),
            "CI_high": float(np.exp(ci[i, 1])),
            "p": float(res.pvalues[i]),
            "patients": len(data),
            "deaths": int(data["event"].sum()),
        })
results = pd.DataFrame(rows)
results.to_csv("output/cox_results.csv", index=False)


def hr_text(r):
    return f"{r['HR']:.2f} ({r['CI_low']:.2f} to {r['CI_high']:.2f})"


pretty = pd.DataFrame({
    "Model": results["model"],
    "Variable": results["variable"],
    "HR (95% CI)": results.apply(hr_text, axis=1),
    "p": results["p"].map(p_short),
    "Patients": results["patients"],
    "Deaths": results["deaths"],
})
print("Hazard ratios:")
print(pretty.to_string(index=False), "\n")


def row_of(model, variable):
    return results[(results["model"] == model) & (results["variable"] == variable)].iloc[0]


def sentence(r, subject):
    return (f"{subject}: hazard ratio {r['HR']:.2f} "
            f"(95% CI {r['CI_low']:.2f} to {r['CI_high']:.2f}, {p_phrase(r['p'])}).")


sex1 = row_of(M1, "Female vs male")
sex2 = row_of(M2, "Female vs male")
text1 = sentence(sex1, "Unadjusted, women compared with men")
text2 = sentence(sex2, "Adjusted for age and ECOG, women compared with men")
print(text1)
print(text2, "\n")


# ---------- Proportional hazards check (Model 2) ----------
def schoenfeld(time, event, X, beta):
    """Schoenfeld residuals: each death's covariates minus the risk-weighted average."""
    event_rows = np.where(event == 1)[0]
    resid = np.zeros((len(event_rows), X.shape[1]))
    for k, i in enumerate(event_rows):
        at_risk = time >= time[i]
        w = np.exp(X[at_risk] @ beta)
        resid[k] = X[i] - (w[:, None] * X[at_risk]).sum(axis=0) / w.sum()
    return time[event_rows], resid


res2, data2, cols2, labels2 = fits[M2]
t_events, resid = schoenfeld(
    data2["time"].to_numpy(dtype=float), data2["event"].to_numpy(dtype=int),
    data2[cols2].to_numpy(dtype=float), np.asarray(res2.params),
)
ph_rows = []
for j, label in enumerate(labels2):
    rho, p = stats.spearmanr(t_events, resid[:, j])
    ph_rows.append({
        "Variable": label,
        "Correlation of residuals with time": f"{rho:.2f}",
        "p": p_short(p),
        "Reading": "possible violation" if p < 0.05 else "no clear sign of a problem",
    })
ph_table = pd.DataFrame(ph_rows)
ph_table.to_csv("output/ph_check.csv", index=False)
print("Proportional hazards check (Model 2):")
print(ph_table.to_string(index=False), "\n")

# Log-minus-log plot by sex: roughly parallel lines support proportional hazards
fig, ax = plt.subplots(figsize=(7, 5))
for name, colour in [("Male", "#1F4E78"), ("Female", "#C0504D")]:
    d = df[df["sex_label"] == name]
    sf = SurvfuncRight(d["time"].to_numpy(dtype=float), d["event"].to_numpy(dtype=int))
    t, s = np.asarray(sf.surv_times), np.asarray(sf.surv_prob)
    keep = (s > 0) & (s < 1) & (t > 0)
    ax.step(np.log(t[keep]), np.log(-np.log(s[keep])), where="post", color=colour, label=name)
ax.set_xlabel("log(time in days)")
ax.set_ylabel("log(-log(survival))")
ax.set_title("Log-minus-log plot by sex\n(roughly parallel lines support proportional hazards)")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("images/loglog_by_sex.png", dpi=150)
plt.close()

# ---------- Forest plot (Model 2) ----------
m2 = results[results["model"] == M2].reset_index(drop=True)
y = np.arange(len(m2))[::-1]
fig, ax = plt.subplots(figsize=(8, 3.6))
ax.errorbar(
    m2["HR"], y,
    xerr=[(m2["HR"] - m2["CI_low"]).to_numpy(), (m2["CI_high"] - m2["HR"]).to_numpy()],
    fmt="s", color="#1F4E78", capsize=4,
)
ax.axvline(1, color="grey", linestyle="--")
ax.set_xscale("log")
ax.set_yticks(y)
ax.set_yticklabels(m2["variable"])
ax.set_xlabel("Hazard ratio (log scale) with 95% confidence interval")
ax.set_title("Model 2: adjusted hazard ratios for death")
ax.grid(axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig("images/forest_plot.png", dpi=150)
plt.close()

# ---------- Report ----------
report = f"""# Cox regression results

These results follow the [statistical analysis plan](statistical_analysis_plan.md). A hazard ratio (HR) compares the rate of death between groups at any point in time. An HR below 1 means a lower rate than the reference group, and above 1 means a higher rate.

## Primary analysis: sex

{text1}

{text2}

![Forest plot](../images/forest_plot.png)

## All models

{md_table(pretty)}

Model 2 uses {int(len(complete))} patients, because one patient has no recorded ECOG score. ECOG 0 and male sex are the reference groups. Age is shown per 10 years.

## Checking the proportional hazards assumption

The Cox model assumes that hazard ratios stay roughly constant over time. Two checks were used: the correlation of Schoenfeld residuals with event time (an approximate check) and a log-minus-log plot.

{md_table(ph_table)}

![Log-minus-log plot by sex](../images/loglog_by_sex.png)

A p-value below 0.05 in the table would suggest that a hazard ratio changes over time. With only four covariates and a modest number of deaths, these checks cannot rule out smaller departures from the assumption.

## Limits

- The data are observational, so a hazard ratio shows an association and does not show that sex or performance status causes a difference in survival.
- Adjustment for age and ECOG reduces confounding but cannot remove it. Other factors, such as the treatments patients received, are not in the data.
- The ECOG analysis is exploratory, as stated in the plan. The primary question is the sex comparison only.
- The data are old, so results may not describe patients today.
"""
Path("docs/cox_results.md").write_text(report, encoding="utf-8")
print("Saved: output/cox_results.csv, output/ph_check.csv, images/forest_plot.png, "
      "images/loglog_by_sex.png, docs/cox_results.md")