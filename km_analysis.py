"""
Phase 3: Kaplan-Meier curves and log-rank tests.

Reads data/analysis_data.csv (created by prepare_data.py).
Writes images/km_by_sex.png, images/km_by_ecog.png, output/km_summary.csv
and docs/km_results.md.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.duration.survfunc import SurvfuncRight, survdiff

for folder in ["images", "output", "docs"]:
    Path(folder).mkdir(exist_ok=True)

Z = 1.96  # for 95% confidence limits
df = pd.read_csv("data/analysis_data.csv")
print(f"Loaded {len(df)} patients\n")


def km_curve(time, event):
    """Kaplan-Meier estimate with 95% confidence limits (complementary log-log)."""
    sf = SurvfuncRight(np.asarray(time), np.asarray(event))
    times = np.r_[0.0, sf.surv_times]
    prob = np.r_[1.0, sf.surv_prob]
    se = np.r_[0.0, sf.surv_prob_se]
    lower = np.full(len(prob), np.nan)
    upper = np.full(len(prob), np.nan)
    ok = (prob > 0) & (prob < 1) & (se > 0)
    se_cll = se[ok] / (prob[ok] * np.abs(np.log(prob[ok])))
    lower[ok] = prob[ok] ** np.exp(Z * se_cll)
    upper[ok] = prob[ok] ** np.exp(-Z * se_cll)
    return sf, times, prob, lower, upper


def value_at(t, times, values):
    """Value of a step function at time t."""
    i = np.searchsorted(times, t, side="right") - 1
    return values[i]


def at_risk(time, t):
    return int((np.asarray(time) >= t).sum())


def num(x, digits=0):
    return "n/a" if pd.isna(x) else f"{x:.{digits}f}"


def pct(x):
    return "n/a" if pd.isna(x) else f"{x * 100:.0f}%"


def p_text(p):
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"


def md_table(frame):
    header = "| " + " | ".join(frame.columns) + " |"
    divider = "|" + "|".join(["---"] * len(frame.columns)) + "|"
    rows = ["| " + " | ".join(str(v) for v in row) + " |"
            for row in frame.itertuples(index=False)]
    return "\n".join([header, divider] + rows)


def summarise(name, d):
    """Median survival and survival at fixed times for one group."""
    sf, times, prob, lower, upper = km_curve(d["time"], d["event"])
    low, high = sf.quantile_ci(0.5)
    row = {
        "group": name,
        "patients": len(d),
        "deaths": int(d["event"].sum()),
        "censored": int((d["event"] == 0).sum()),
        "median_days": float(sf.quantile(0.5)),
        "median_ci_low": float(low),
        "median_ci_high": float(high),
    }
    for day in (180, 365, 500):
        row[f"survival_{day}d"] = value_at(day, times, prob)
        row[f"survival_{day}d_low"] = value_at(day, times, lower)
        row[f"survival_{day}d_high"] = value_at(day, times, upper)
    return row


def km_plot(groups, title, note, path):
    """Kaplan-Meier curves with confidence bands, censor marks and a risk table."""
    colours = ["#1F4E78", "#C0504D"]
    risk_times = list(range(0, 1001, 200))
    fig, (ax, ax2) = plt.subplots(
        2, 1, figsize=(9, 7), sharex=True, gridspec_kw={"height_ratios": [4, 1]}
    )
    for (name, d), colour in zip(groups.items(), colours):
        sf, times, prob, lower, upper = km_curve(d["time"], d["event"])
        ax.step(times, prob, where="post", color=colour, label=f"{name} (n={len(d)})")
        ax.fill_between(times, lower, upper, step="post", color=colour, alpha=0.15)
        censored = d.loc[d["event"] == 0, "time"]
        ax.plot(censored, [value_at(t, times, prob) for t in censored],
                "|", color=colour, markersize=6)

    ax.axhline(0.5, color="grey", linestyle=":", linewidth=1)
    ax.set_ylim(0, 1.02)
    ax.set_xlim(0, 1050)
    ax.set_xticks(risk_times)
    ax.set_ylabel("Probability of survival")
    ax.set_title(title)
    ax.grid(alpha=0.3)
    ax.legend(loc="lower left")
    ax.text(0.97, 0.95, note, transform=ax.transAxes, ha="right", va="top")

    n_groups = len(groups)
    for row, (name, d) in enumerate(groups.items()):
        y = n_groups - 1 - row
        for t in risk_times:
            ax2.text(t, y, str(at_risk(d["time"], t)), ha="center", va="center")
    ax2.set_yticks(range(n_groups))
    ax2.set_yticklabels(list(groups)[::-1])
    ax2.set_ylim(-0.6, n_groups - 0.4)
    ax2.set_xlabel("Days since enrolment")
    ax2.set_title("Number at risk", loc="left", fontsize=9)
    for spine in ax2.spines.values():
        spine.set_visible(False)
    ax2.tick_params(left=False)

    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def analyse(data, column, order, title, image):
    """Kaplan-Meier summary, log-rank test and chart for two groups."""
    groups = {name: data[data[column] == name] for name in order}
    summary = pd.DataFrame([summarise(name, d) for name, d in groups.items()])
    codes = data[column].map({name: i for i, name in enumerate(order)}).to_numpy()
    chi2, p = survdiff(data["time"].to_numpy(), data["event"].to_numpy(), codes)
    km_plot(groups, title, f"Log-rank {p_text(p)}", image)
    return summary, float(chi2), float(p)


def pretty(summary):
    out = []
    for _, r in summary.iterrows():
        row = {
            "Group": r["group"],
            "Patients": int(r["patients"]),
            "Deaths": int(r["deaths"]),
            "Censored": int(r["censored"]),
            "Median survival, days (95% CI)":
                f"{num(r['median_days'])} ({num(r['median_ci_low'])} to {num(r['median_ci_high'])})",
        }
        for day in (180, 365, 500):
            row[f"Survival at {day} days (95% CI)"] = (
                f"{pct(r[f'survival_{day}d'])} "
                f"({pct(r[f'survival_{day}d_low'])} to {pct(r[f'survival_{day}d_high'])})"
            )
        out.append(row)
    return pd.DataFrame(out)


def describe(summary, chi2, p):
    parts = []
    for _, r in summary.iterrows():
        parts.append(
            f"{r['group']}: median survival {num(r['median_days'])} days "
            f"(95% CI {num(r['median_ci_low'])} to {num(r['median_ci_high'])}), "
            f"{int(r['deaths'])} deaths among {int(r['patients'])} patients"
        )
    return "; ".join(parts) + f". Log-rank test: chi-square = {chi2:.2f} on 1 degree of freedom, {p_text(p)}."


# ---------- Primary analysis: sex ----------
sex_summary, sex_chi2, sex_p = analyse(
    df, "sex_label", ["Male", "Female"],
    "Overall survival by sex (all patients)", "images/km_by_sex.png",
)

# ---------- Secondary (exploratory): performance status ----------
ecog = df[df["ecog_group"].notna()].copy()
ecog["ecog_label"] = "ECOG " + ecog["ecog_group"]
ecog_summary, ecog_chi2, ecog_p = analyse(
    ecog, "ecog_label", ["ECOG 0-1", "ECOG 2 or higher"],
    "Overall survival by performance status (exploratory)", "images/km_by_ecog.png",
)

# ---------- Save and print ----------
combined = pd.concat(
    [sex_summary.assign(analysis="Primary: sex"),
     ecog_summary.assign(analysis="Exploratory: ECOG")]
)
combined.to_csv("output/km_summary.csv", index=False)

print("PRIMARY: survival by sex")
print(pretty(sex_summary).to_string(index=False))
print(describe(sex_summary, sex_chi2, sex_p), "\n")
print("EXPLORATORY: survival by performance status")
print(pretty(ecog_summary).to_string(index=False))
print(describe(ecog_summary, ecog_chi2, ecog_p), "\n")

report = f"""# Kaplan-Meier results

These results follow the [statistical analysis plan](statistical_analysis_plan.md). They are unadjusted: age and performance status are not yet taken into account (Phase 4).

## Primary analysis: overall survival by sex

All {len(df)} patients.

![Kaplan-Meier curves by sex](../images/km_by_sex.png)

{md_table(pretty(sex_summary))}

{describe(sex_summary, sex_chi2, sex_p)}

## Secondary analysis (exploratory): overall survival by performance status

{len(ecog)} patients with a recorded ECOG score. ECOG 0-1 means fully active or walking about with symptoms. ECOG 2 or higher means in bed for part of the day or more.

![Kaplan-Meier curves by ECOG group](../images/km_by_ecog.png)

{md_table(pretty(ecog_summary))}

{describe(ecog_summary, ecog_chi2, ecog_p)}

## How to read these results

- The curve shows the share of patients still alive over time. Small ticks mark patients who were censored (still alive or lost to follow-up at that time).
- Median survival is the time at which the curve crosses 50%. It is read from the curve, so it takes censoring into account.
- The shaded bands are 95% confidence intervals. They widen on the right, where few patients remain at risk.
- The log-rank test asks whether the curves differ more than chance would explain. A small p-value is not proof of cause, and a large one is not proof of no difference.

## Limits

- These are unadjusted comparisons. Men and women may differ in age or performance status, which could explain part of a difference. The adjusted Cox model in the next phase addresses this.
- The ECOG analysis is exploratory, as stated in the plan.
- The data are observational and old, so results may not describe patients today.
"""
Path("docs/km_results.md").write_text(report, encoding="utf-8")
print("Saved: images/km_by_sex.png, images/km_by_ecog.png, output/km_summary.csv, docs/km_results.md")