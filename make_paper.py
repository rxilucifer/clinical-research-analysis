"""
Phase 6: assemble the paper-style report (docs/paper.md) from the saved results.

Every number comes from the output files of the earlier phases, so the paper
cannot disagree with the analysis. The Discussion is read from
docs/my_discussion.md, which you write yourself in your own words.
"""
from datetime import date
from pathlib import Path

import pandas as pd
from statsmodels.duration.survfunc import survdiff

AUTHOR = "Dr. Raj Akil Nomani"

Path("docs").mkdir(exist_ok=True)

df = pd.read_csv("data/analysis_data.csv")
km = pd.read_csv("output/km_summary.csv")
cox = pd.read_csv("output/cox_results.csv")
ph = pd.read_csv("output/ph_check.csv")
window = pd.read_csv("output/ph_window_check.csv")
table1 = pd.read_csv("output/table1.csv")
meta = pd.read_csv("output/meta_results.csv")
meta_trials = pd.read_csv("data/meta_trials.csv")


def p_text(p):
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"


def hr_text(r):
    return f"{r['HR']:.2f} (95% CI {r['CI_low']:.2f} to {r['CI_high']:.2f}; {p_text(r['p'])})"


def md_table(frame):
    header = "| " + " | ".join(frame.columns) + " |"
    divider = "|" + "|".join(["---"] * len(frame.columns)) + "|"
    rows = ["| " + " | ".join(str(v) for v in row) + " |"
            for row in frame.itertuples(index=False)]
    return "\n".join([header, divider] + rows)


def km_row(group):
    return km[km["group"] == group].iloc[0]


def cox_row(model, variable):
    return cox[(cox["model"] == model) & (cox["variable"] == variable)].iloc[0]


def logrank(data, column, order):
    codes = data[column].map({name: i for i, name in enumerate(order)}).to_numpy()
    chi2, p = survdiff(data["time"].to_numpy(), data["event"].to_numpy(), codes)
    return float(chi2), float(p)


def rate_words(hr, group, reference):
    if hr < 1:
        return f"a lower rate of death in {group} than in {reference}"
    return f"a higher rate of death in {group} than in {reference}"


# ---------- Numbers ----------
n_all = len(df)
deaths = int(df["event"].sum())
male, female = km_row("Male"), km_row("Female")
lr_sex_chi2, lr_sex_p = logrank(df, "sex_label", ["Male", "Female"])

ecog_df = df[df["ecog_group"].notna()].copy()
ecog_df["ecog_label"] = "ECOG " + ecog_df["ecog_group"]
ecog_low, ecog_high = km_row("ECOG 0-1"), km_row("ECOG 2 or higher")
lr_ecog_chi2, lr_ecog_p = logrank(ecog_df, "ecog_label", ["ECOG 0-1", "ECOG 2 or higher"])

M1 = "Model 1: sex only (all patients)"
M2 = "Model 2: sex, age and ECOG (complete cases)"
S1 = "Secondary: ECOG 2 or higher vs 0-1, unadjusted"
S2 = "Secondary: ECOG 2 or higher vs 0-1, adjusted for sex and age"
sex_u = cox_row(M1, "Female vs male")
sex_a = cox_row(M2, "Female vs male")
age_a = cox_row(M2, "Age, per 10 years")
ecog1 = cox_row(M2, "ECOG 1 vs ECOG 0")
ecog2 = cox_row(M2, "ECOG 2 or higher vs ECOG 0")
sec_u = cox_row(S1, "ECOG 2 or higher vs ECOG 0-1")
sec_a = cox_row(S2, "ECOG 2 or higher vs ECOG 0-1")
n_complete, d_complete = int(sex_a["patients"]), int(sex_a["deaths"])

t1 = table1.set_index("Characteristic")
table1_rows = ["Patients, n", "Age, years: median (range)", "ECOG 0, n (%)",
               "ECOG 1, n (%)", "ECOG 2 or higher, n (%)", "ECOG missing, n"]
table1_small = t1.loc[table1_rows].reset_index()
age_all = t1.loc["Age, years: median (range)", "All patients"]
n_male = t1.loc["Patients, n", "Male"]
n_female = t1.loc["Patients, n", "Female"]
ecog_missing = t1.loc["ECOG missing, n", "All patients"]

flag_names = {
    "Female vs male": "sex",
    "Age, per 10 years": "age",
    "ECOG 1 vs ECOG 0": "ECOG 1",
    "ECOG 2 or higher vs ECOG 0": "ECOG 2 or higher",
}
flagged = [flag_names.get(v, v)
           for v in ph[ph["Reading"] == "possible violation"]["Variable"]]
flag_text = " and ".join(flagged) if flagged else "none of the variables"
cutoff = window.columns[1].split(" to ")[-1].rstrip(")")

mr = meta[meta["model"] == "random"].iloc[0]
n_trials = len(meta_trials)
trial_names = ", ".join(meta_trials["trial"])

sex_words = rate_words(sex_a["HR"], "women", "men")
ecog_words = rate_words(ecog2["HR"], "patients with ECOG 2 or higher",
                        "fully active patients (ECOG 0)")

# ---------- Discussion written by you ----------
disc_path = Path("docs/my_discussion.md")
discussion, extra_refs = "", ""
if disc_path.exists():
    content = disc_path.read_text(encoding="utf-8")
    discussion, _, extra_refs = content.partition("### Additional references")
    discussion = discussion.strip()
    extra_refs = "" if "WRITE HERE" in extra_refs else extra_refs.strip()
draft = (not discussion) or ("WRITE HERE" in discussion)
if not discussion:
    discussion = "*The Discussion has not been written yet. Create docs/my_discussion.md.*"
banner = "> **DRAFT.** The Discussion is not finished.\n\n" if draft else ""

today = date.today().strftime("%d %B %Y")

paper = f"""# Survival by sex and performance status in advanced lung cancer: an analysis of the NCCTG cohort

**Author:** {AUTHOR} | **Date:** {today} | **Type:** Learning project. Not clinical advice.

{banner}## Abstract

**Background.** Sex and performance status are commonly studied prognostic factors in advanced lung cancer. This report examines both in a published teaching dataset, following a written analysis plan.

**Methods.** We analysed {n_all} patients from the North Central Cancer Treatment Group (NCCTG) advanced lung cancer cohort. Overall survival was compared between women and men using Kaplan-Meier curves, a log-rank test and Cox regression adjusted for age and ECOG performance status. Performance status was an exploratory question. The proportional hazards assumption was checked, and a post-hoc comparison of early and late follow-up was added after the residual check flagged {flag_text}.

**Results.** {deaths} of {n_all} patients died. Median survival was {male['median_days']:.0f} days in men and {female['median_days']:.0f} days in women (log-rank {p_text(lr_sex_p)}). The adjusted hazard ratio for women compared with men was {hr_text(sex_a)}, which means {sex_words}. ECOG 2 or higher compared with ECOG 0 had a hazard ratio of {hr_text(ecog2)}.

**Conclusions.** In this cohort, the data show {sex_words}, and {ecog_words}. These are associations in observational data and do not show that sex or performance status causes a difference in survival.

## 1. Introduction

Advanced lung cancer has a poor prognosis, and clinicians use simple patient characteristics to describe and compare groups of patients. Two of these are sex and performance status. Performance status describes how active a patient is, and the ECOG scale rates it from 0 (fully active) to 4 (bedbound).

This report asks a primary question and a secondary question in a published teaching dataset. **Primary:** is overall survival different between women and men? **Secondary (exploratory):** is a worse performance status associated with shorter survival? The analysis was written down in a statistical analysis plan before any survival analysis was run (docs/statistical_analysis_plan.md).

## 2. Methods

**Data.** The NCCTG advanced lung cancer dataset ({n_all} patients) from the R survival package. It was described by Loprinzi and colleagues in 1994. The data are old, publicly available and contain no personal information.

**Outcome.** Overall survival, measured in days from enrolment to death from any cause. Patients alive at the end of follow-up were censored at their last follow-up time.

**Exposures and covariates.** Sex (primary exposure). ECOG performance score, grouped as 0, 1, or 2 or higher (the small number of patients with higher scores was combined, as set out in the plan). Age, entered per 10 years. Calories at meals was not used because many values were missing.

**Statistical analysis.** Baseline characteristics are described by sex without hypothesis tests. Survival curves were estimated with the Kaplan-Meier method and compared with the log-rank test. Hazard ratios were estimated with Cox proportional hazards regression: Model 1 included sex only, and Model 2 added age and ECOG. Model 2 used the {n_complete} patients with a recorded ECOG score, and no values were imputed. The proportional hazards assumption was checked with a residual-based test and a log-minus-log plot. All tests were two-sided with a significance level of 0.05. The sex comparison was the only confirmatory analysis, and the ECOG analyses were exploratory.

**Changes made after seeing results.** The way ECOG and age enter Model 2 was recorded before the Cox model was run. After the residual check flagged {flag_text}, a post-hoc comparison of hazard ratios in early (up to day {cutoff}) and late follow-up was added and recorded in the analysis plan. These comparisons were not adjusted for multiple testing.

**Software and reproducibility.** Python with pandas, statsmodels and matplotlib. All code and data are in this repository, and each number in this report is generated from the saved results by `make_paper.py`.

## 3. Results

### 3.1 Patients

The cohort had {n_all} patients: {n_male} men and {n_female} women. Median age (range): {age_all} years. Table 1 shows the main characteristics. {ecog_missing} patient had no recorded ECOG score.

**Table 1. Baseline characteristics by sex**

{md_table(table1_small)}

Numbers are n (%) or median (range). ECOG percentages are of patients with a recorded score.

### 3.2 Survival by sex

{deaths} of {n_all} patients died during follow-up. Median survival was {male['median_days']:.0f} days (95% CI {male['median_ci_low']:.0f} to {male['median_ci_high']:.0f}) in men and {female['median_days']:.0f} days (95% CI {female['median_ci_low']:.0f} to {female['median_ci_high']:.0f}) in women. Estimated survival at one year was {male['survival_365d'] * 100:.0f}% in men and {female['survival_365d'] * 100:.0f}% in women. The log-rank test gave a chi-square of {lr_sex_chi2:.2f} on 1 degree of freedom, {p_text(lr_sex_p)}.

![Kaplan-Meier curves by sex](../images/km_by_sex.png)

**Figure 1.** Kaplan-Meier curves by sex with 95% confidence bands and numbers at risk. Small ticks mark censored patients.

### 3.3 Cox regression

Unadjusted, the hazard ratio for women compared with men was {hr_text(sex_u)}. After adjustment for age and ECOG (Model 2, {n_complete} patients, {d_complete} deaths) it was {hr_text(sex_a)}. Age showed a hazard ratio of {hr_text(age_a)} per 10 years. Compared with ECOG 0, the hazard ratio was {hr_text(ecog1)} for ECOG 1 and {hr_text(ecog2)} for ECOG 2 or higher.

![Forest plot of Model 2](../images/forest_plot.png)

**Figure 2.** Adjusted hazard ratios for death (Model 2) with 95% confidence intervals, on a log scale.

### 3.4 Secondary analysis: performance status

Median survival was {ecog_low['median_days']:.0f} days (95% CI {ecog_low['median_ci_low']:.0f} to {ecog_low['median_ci_high']:.0f}) in patients with ECOG 0-1 and {ecog_high['median_days']:.0f} days (95% CI {ecog_high['median_ci_low']:.0f} to {ecog_high['median_ci_high']:.0f}) in patients with ECOG 2 or higher (log-rank {p_text(lr_ecog_p)}). The hazard ratio for ECOG 2 or higher compared with ECOG 0-1 was {hr_text(sec_u)} unadjusted and {hr_text(sec_a)} adjusted for sex and age. This analysis was exploratory.

![Kaplan-Meier curves by ECOG group](../images/km_by_ecog.png)

**Figure 3.** Kaplan-Meier curves by performance status group.

### 3.5 Proportional hazards

The residual-based check flagged {flag_text}. Table 2 compares hazard ratios in early and late follow-up (cutoff day {cutoff}). This is a post-hoc analysis, and its p-values are not adjusted for multiple testing.

**Table 2. Hazard ratios in early and late follow-up (Model 2)**

{md_table(window)}

![Log-minus-log plot by sex](../images/loglog_by_sex.png)

**Figure 4.** Log-minus-log plot by sex. Roughly parallel lines support proportional hazards.

## 4. Discussion

{discussion}

## 5. Limitations

- The data are observational. Hazard ratios show associations and do not show that sex or performance status causes a difference in survival.
- Adjustment for age and ECOG reduces confounding but cannot remove it. Treatment, stage and other factors are not available.
- The data are old and come from one trial cohort, so the results may not describe patients today.
- The proportional hazards check flagged {flag_text}. The follow-up comparison was added after seeing the results, was not adjusted for multiple testing, and had limited power in the late window.
- The analysis plan was written for a well-known teaching dataset whose main results are already published. It documents good practice and is not true pre-registration.

## Appendix A. A small meta-analysis (evidence synthesis exercise)

To practise evidence synthesis, a separate meta-analysis pooled {n_trials} published cardiovascular outcome trials of SGLT2 inhibitors in type 2 diabetes ({trial_names}). The outcome was 3-point MACE. The random-effects pooled hazard ratio was {mr['hr']:.2f} (95% CI {mr['ci_low']:.2f} to {mr['ci_high']:.2f}), with I-squared of {mr['I2_percent']:.0f}%. The trials were chosen as the large well-known outcome trials and were not found by a systematic search. See docs/meta_analysis_plan.md and docs/meta_results.md.

![Forest plot of the meta-analysis](../images/meta_forest.png)

## References

1. Loprinzi CL, Laurie JA, Wieand HS, et al. Prospective evaluation of prognostic variables from patient-completed questionnaires. J Clin Oncol 1994;12(3):601-607.
2. Kaplan EL, Meier P. Nonparametric estimation from incomplete observations. J Am Stat Assoc 1958;53:457-481.
3. Cox DR. Regression models and life-tables. J R Stat Soc B 1972;34:187-220.
4. Schoenfeld D. Partial residuals for the proportional hazards regression model. Biometrika 1982;69(1):239-241.
5. Oken MM, Creech RH, Tormey DC, et al. Toxicity and response criteria of the Eastern Cooperative Oncology Group. Am J Clin Oncol 1982;5(6):649-655.
6. DerSimonian R, Laird N. Meta-analysis in clinical trials. Control Clin Trials 1986;7:177-188.
7. Zinman B, et al. Empagliflozin, cardiovascular outcomes, and mortality in type 2 diabetes. N Engl J Med 2015;373:2117-2128.
8. Neal B, et al. Canagliflozin and cardiovascular and renal events in type 2 diabetes. N Engl J Med 2017;377:644-657.
9. Wiviott SD, et al. Dapagliflozin and cardiovascular outcomes in type 2 diabetes. N Engl J Med 2019;380:347-357.
10. Cannon CP, et al. Cardiovascular outcomes with ertugliflozin in type 2 diabetes. N Engl J Med 2020;383:1425-1435.
"""
if extra_refs:
    paper += "\n" + extra_refs + "\n"

Path("docs/paper.md").write_text(paper, encoding="utf-8")

words = len(paper.split())
print(f"Wrote docs/paper.md ({words} words)")
print(f"Deaths: {deaths} of {n_all}; median survival men {male['median_days']:.0f}, women {female['median_days']:.0f} days")
print(f"Adjusted HR for sex: {hr_text(sex_a)}")
print(f"ECOG 2 or higher vs 0: {hr_text(ecog2)}")
print("STATUS:", "DRAFT, write docs/my_discussion.md" if draft else "complete")