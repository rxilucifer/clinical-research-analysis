"""
Phase 5: meta-analysis of cardiovascular outcome trials of SGLT2 inhibitors.
Outcome: 3-point MACE (cardiovascular death, non-fatal MI, non-fatal stroke).

Reads data/meta_trials.csv (typed in by hand from the published papers).
Writes output/meta_results.csv, images/meta_forest.png and docs/meta_results.md.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Polygon
from scipy import stats

for folder in ["output", "images", "docs"]:
    Path(folder).mkdir(exist_ok=True)

Z = stats.norm.ppf(0.975)

trials = pd.read_csv("data/meta_trials.csv")
trials["log_hr"] = np.log(trials["hr"])
trials["se"] = (np.log(trials["ci_high"]) - np.log(trials["ci_low"])) / (2 * Z)

# ---------- 1. Check the typed-in numbers ----------
print("Data check (the HR should sit near the middle of its interval on the log scale):")
for _, t in trials.iterrows():
    middle = (np.log(t["ci_low"]) + np.log(t["ci_high"])) / 2
    ok = t["ci_low"] < t["hr"] < t["ci_high"] and abs(t["log_hr"] - middle) < 0.02
    print(f"{'PASS' if ok else 'CHECK'}  {t['trial']}: HR {t['hr']} ({t['ci_low']} to {t['ci_high']})")
print()


# ---------- 2. Pooling ----------
def pool(sub):
    """Fixed-effect and DerSimonian-Laird random-effects pooling of log hazard ratios."""
    y, se = sub["log_hr"].to_numpy(), sub["se"].to_numpy()
    w = 1 / se ** 2
    fixed = float(np.sum(w * y) / np.sum(w))
    q = float(np.sum(w * (y - fixed) ** 2))
    df = len(y) - 1
    c = np.sum(w) - np.sum(w ** 2) / np.sum(w)
    tau2 = max(0.0, (q - df) / c) if df > 0 else 0.0
    w_re = 1 / (se ** 2 + tau2)
    return {
        "fixed": (fixed, float(np.sqrt(1 / np.sum(w)))),
        "random": (float(np.sum(w_re * y) / np.sum(w_re)), float(np.sqrt(1 / np.sum(w_re)))),
        "q": q, "df": df, "tau2": float(tau2),
        "q_p": float(stats.chi2.sf(q, df)) if df > 0 else float("nan"),
        "i2": max(0.0, (q - df) / q * 100) if q > 0 else 0.0,
        "w_fixed": w / w.sum() * 100,
        "w_random": w_re / w_re.sum() * 100,
    }


def hr_ci(est, se):
    return float(np.exp(est)), float(np.exp(est - Z * se)), float(np.exp(est + Z * se))


def hr_text(est, se):
    hr, lo, hi = hr_ci(est, se)
    return f"{hr:.2f} ({lo:.2f} to {hi:.2f})"


def p_value(est, se):
    return float(2 * stats.norm.sf(abs(est / se)))


def p_short(p):
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def md_table(frame):
    header = "| " + " | ".join(frame.columns) + " |"
    divider = "|" + "|".join(["---"] * len(frame.columns)) + "|"
    rows = ["| " + " | ".join(str(v) for v in row) + " |"
            for row in frame.itertuples(index=False)]
    return "\n".join([header, divider] + rows)


res = pool(trials)
fixed_est, fixed_se = res["fixed"]
random_est, random_se = res["random"]

# ---------- 3. Tables ----------
study_table = pd.DataFrame({
    "Trial": trials["trial"],
    "Drug": trials["drug"],
    "Patients": trials["n_randomised"].map("{:,}".format),
    "HR (95% CI)": [f"{r.hr:.2f} ({r.ci_low:.2f} to {r.ci_high:.2f})" for r in trials.itertuples()],
    "Weight, random (%)": [f"{w:.1f}" for w in res["w_random"]],
})

pooled_table = pd.DataFrame([
    {"Model": "Random effects (primary)", "HR (95% CI)": hr_text(random_est, random_se),
     "p": p_short(p_value(random_est, random_se))},
    {"Model": "Fixed effect", "HR (95% CI)": hr_text(fixed_est, fixed_se),
     "p": p_short(p_value(fixed_est, fixed_se))},
])

het_text = (f"Cochran's Q = {res['q']:.2f} on {res['df']} degrees of freedom (p = {res['q_p']:.2f}); "
            f"I-squared = {res['i2']:.0f}%; tau-squared = {res['tau2']:.4f}")

loo_rows = []
for i, t in trials.iterrows():
    r = pool(trials.drop(index=i))
    est, se = r["random"]
    loo_rows.append({"Trial left out": t["trial"],
                     "Pooled HR, random effects (95% CI)": hr_text(est, se),
                     "I-squared": f"{r['i2']:.0f}%"})
loo_table = pd.DataFrame(loo_rows)

print("Included trials:")
print(study_table.to_string(index=False), "\n")
print("Pooled results:")
print(pooled_table.to_string(index=False), "\n")
print("Heterogeneity:", het_text, "\n")
print("Leave-one-out:")
print(loo_table.to_string(index=False), "\n")

# ---------- 4. Save numbers ----------
rows = []
for model, (est, se) in [("random", res["random"]), ("fixed", res["fixed"])]:
    hr, lo, hi = hr_ci(est, se)
    rows.append({"model": model, "hr": hr, "ci_low": lo, "ci_high": hi,
                 "p": p_value(est, se), "Q": res["q"], "df": res["df"],
                 "p_Q": res["q_p"], "I2_percent": res["i2"], "tau2": res["tau2"]})
pd.DataFrame(rows).to_csv("output/meta_results.csv", index=False)


# ---------- 5. Forest plot ----------
def forest_plot(path):
    k = len(trials)
    y_trials = list(range(k, 0, -1))
    size = res["w_random"] / res["w_random"].max()
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.text(1.55, k + 0.9, "HR (95% CI)", fontweight="bold", va="center")
    ax.text(2.1, k + 0.9, "Weight, %", fontweight="bold", va="center")
    for y, t, s, weight in zip(y_trials, trials.itertuples(), size, res["w_random"]):
        ax.plot([t.ci_low, t.ci_high], [y, y], color="#1F4E78", linewidth=1.5)
        ax.plot(t.hr, y, "s", color="#1F4E78", markersize=5 + 9 * s)
        ax.text(1.55, y, f"{t.hr:.2f} ({t.ci_low:.2f} to {t.ci_high:.2f})", va="center")
        ax.text(2.1, y, f"{weight:.1f}", va="center")

    y_fixed, y_random = -0.8, -1.8
    for y, (est, se), colour, weight_note in [
        (y_fixed, res["fixed"], "#7F7F7F", ""), (y_random, res["random"], "#C0504D", "")
    ]:
        hr, lo, hi = hr_ci(est, se)
        ax.add_patch(Polygon([[lo, y], [hr, y + 0.3], [hi, y], [hr, y - 0.3]], closed=True, color=colour))
        ax.text(1.55, y, f"{hr:.2f} ({lo:.2f} to {hi:.2f})", va="center", fontweight="bold")

    ax.axvline(1, color="grey", linestyle="--")
    ax.set_xscale("log")
    ax.set_xlim(0.6, 1.3)
    ax.set_xticks([0.6, 0.8, 1.0, 1.2])
    ax.set_xticklabels(["0.6", "0.8", "1.0", "1.2"])
    ax.minorticks_off()
    ax.set_yticks(y_trials + [y_fixed, y_random])
    ax.set_yticklabels([f"{t.trial}\n(n={t.n_randomised:,})" for t in trials.itertuples()]
                       + ["Fixed effect", "Random effects"])
    ax.set_ylim(-2.7, k + 1.4)
    ax.text(0.8, -2.5, "Favours SGLT2 inhibitor", ha="center")
    ax.text(1.15, -2.5, "Favours placebo", ha="center")
    ax.set_xlabel("Hazard ratio for 3-point MACE (log scale)")
    ax.set_title("SGLT2 inhibitors and 3-point MACE in type 2 diabetes")
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


forest_plot("images/meta_forest.png")

# ---------- 6. Report ----------
hr_r, lo_r, hi_r = hr_ci(random_est, random_se)
report = f"""# Meta-analysis results

SGLT2 inhibitors versus placebo, outcome 3-point MACE (cardiovascular death, non-fatal myocardial infarction or non-fatal stroke). This follows the [meta-analysis plan](meta_analysis_plan.md). It is a small teaching meta-analysis of four trials and not a systematic review.

![Forest plot](../images/meta_forest.png)

## Included trials

{md_table(study_table)}

Hazard ratios are taken from the primary publications. EMPA-REG (95.02%) and VERTIS-CV (95.6%) report slightly different interval levels, and both are treated as 95% intervals.

## Pooled results

{md_table(pooled_table)}

In the primary random-effects analysis, SGLT2 inhibitors were associated with a hazard ratio for 3-point MACE of {hr_r:.2f} (95% CI {lo_r:.2f} to {hi_r:.2f}) compared with placebo.

## Heterogeneity

{het_text}.

With only four trials, these tests have low power. A low I-squared does not prove the trials are alike. The trials differ in drug, population (for example the share of patients with established cardiovascular disease) and follow-up.

## Sensitivity analysis: leave one out

{md_table(loo_table)}

## Limits

- Four trials chosen as the well-known large outcome trials, not found by a systematic search, so selection bias is possible.
- Only aggregate results from publications were used, and no formal risk of bias assessment was done.
- Publication bias could not be assessed with four trials.
- Several trials were designed mainly to show safety, so a result close to 1 is not evidence that a drug has no effect.
- These are results for trial populations and may not apply to every patient.
"""
Path("docs/meta_results.md").write_text(report, encoding="utf-8")
print("Saved: output/meta_results.csv, images/meta_forest.png, docs/meta_results.md")