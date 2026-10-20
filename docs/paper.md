# Survival by sex and performance status in advanced lung cancer: an analysis of the NCCTG cohort

**Author:** Dr. Raj Akil Nomani
**Date:** 20 October 2026
**Type:** Learning project. Not clinical advice.

## Abstract

**Background.** Sex and performance status are commonly studied prognostic factors in advanced lung cancer. This report examines both in a published teaching dataset, following a written analysis plan.

**Methods.** We analysed 228 patients from the North Central Cancer Treatment Group (NCCTG) advanced lung cancer cohort. Overall survival was compared between women and men using Kaplan-Meier curves, a log-rank test and Cox regression adjusted for age and ECOG performance status. Performance status was an exploratory question. The proportional hazards assumption was checked, and a post-hoc comparison of early and late follow-up was added after the residual check flagged sex and ECOG 2 or higher.

**Results.** 165 of 228 patients died. Median survival was 270 days in men and 426 days in women (log-rank p = 0.001). The adjusted hazard ratio for women compared with men was 0.58 (95% CI 0.41 to 0.80; p = 0.001), which means a lower rate of death in women than in men. ECOG 2 or higher compared with ECOG 0 had a hazard ratio of 2.50 (95% CI 1.60 to 3.90; p < 0.001).

**Conclusions.** In this cohort, the data show a lower rate of death in women than in men, and a higher rate of death in patients with ECOG 2 or higher than in fully active patients (ECOG 0). These are associations in observational data and do not show that sex or performance status causes a difference in survival.

## 1. Introduction

Advanced lung cancer has a poor prognosis, and clinicians use simple patient characteristics to describe and compare groups of patients. Two of these are sex and performance status. Performance status describes how active a patient is, and the ECOG scale rates it from 0 (fully active) to 4 (bedbound).

This report asks a primary question and a secondary question in a published teaching dataset. **Primary:** is overall survival different between women and men? **Secondary (exploratory):** is a worse performance status associated with shorter survival? The analysis was written down in a statistical analysis plan before any survival analysis was run (docs/statistical_analysis_plan.md).

## 2. Methods

**Data.** The NCCTG advanced lung cancer dataset (228 patients) from the R survival package. It was described by Loprinzi and colleagues in 1994. The data are old, publicly available and contain no personal information.

**Outcome.** Overall survival, measured in days from enrolment to death from any cause. Patients alive at the end of follow-up were censored at their last follow-up time.

**Exposures and covariates.** Sex (primary exposure). ECOG performance score, grouped as 0, 1, or 2 or higher (the small number of patients with higher scores was combined, as set out in the plan). Age, entered per 10 years. Calories at meals was not used because many values were missing.

**Statistical analysis.** Baseline characteristics are described by sex without hypothesis tests. Survival curves were estimated with the Kaplan-Meier method and compared with the log-rank test. Hazard ratios were estimated with Cox proportional hazards regression: Model 1 included sex only, and Model 2 added age and ECOG. Model 2 used the 227 patients with a recorded ECOG score, and no values were imputed. The proportional hazards assumption was checked with a residual-based test and a log-minus-log plot. All tests were two-sided with a significance level of 0.05. The sex comparison was the only confirmatory analysis, and the ECOG analyses were exploratory.

**Changes made after seeing results.** The way ECOG and age enter Model 2 was recorded before the Cox model was run. After the residual check flagged sex and ECOG 2 or higher, a post-hoc comparison of hazard ratios in early (up to day 300) and late follow-up was added and recorded in the analysis plan. These comparisons were not adjusted for multiple testing.

**Software and reproducibility.** Python with pandas, statsmodels and matplotlib. All code and data are in this repository, and each number in this report is generated from the saved results by `make_paper.py`.

## 3. Results

### 3.1 Patients

The cohort had 228 patients: 138 men and 90 women. Median age (range): 63 (39-82) years. Table 1 shows the main characteristics. 1 patient had no recorded ECOG score.

**Table 1. Baseline characteristics by sex**

| Characteristic | All patients | Male | Female |
|---|---|---|---|
| Patients, n | 228 | 138 | 90 |
| Age, years: median (range) | 63 (39-82) | 64 (39-82) | 61 (41-77) |
| ECOG 0, n (%) | 63 (28%) | 36 (26%) | 27 (30%) |
| ECOG 1, n (%) | 113 (50%) | 71 (52%) | 42 (47%) |
| ECOG 2 or higher, n (%) | 51 (22%) | 30 (22%) | 21 (23%) |
| ECOG missing, n | 1 | 1 | 0 |

Numbers are n (%) or median (range). ECOG percentages are of patients with a recorded score.

### 3.2 Survival by sex

165 of 228 patients died during follow-up. Median survival was 270 days (95% CI 210 to 306) in men and 426 days (95% CI 345 to 524) in women. Estimated survival at one year was 34% in men and 53% in women. The log-rank test gave a chi-square of 10.33 on 1 degree of freedom, p = 0.001.

![Kaplan-Meier curves by sex](../images/km_by_sex.png)

**Figure 1.** Kaplan-Meier curves by sex with 95% confidence bands and numbers at risk. Small ticks mark censored patients.

### 3.3 Cox regression

Unadjusted, the hazard ratio for women compared with men was 0.59 (95% CI 0.42 to 0.82; p = 0.001). After adjustment for age and ECOG (Model 2, 227 patients, 164 deaths) it was 0.58 (95% CI 0.41 to 0.80; p = 0.001). Age showed a hazard ratio of 1.12 (95% CI 0.93 to 1.34; p = 0.235) per 10 years. Compared with ECOG 0, the hazard ratio was 1.51 (95% CI 1.02 to 2.23; p = 0.040) for ECOG 1 and 2.50 (95% CI 1.60 to 3.90; p < 0.001) for ECOG 2 or higher.

![Forest plot of Model 2](../images/forest_plot.png)

**Figure 2.** Adjusted hazard ratios for death (Model 2) with 95% confidence intervals, on a log scale.

### 3.4 Secondary analysis: performance status

Median survival was 353 days (95% CI 305 to 428) in patients with ECOG 0-1 and 183 days (95% CI 145 to 285) in patients with ECOG 2 or higher (log-rank p < 0.001). The hazard ratio for ECOG 2 or higher compared with ECOG 0-1 was 2.00 (95% CI 1.41 to 2.82; p < 0.001) unadjusted and 1.91 (95% CI 1.34 to 2.71; p < 0.001) adjusted for sex and age. This analysis was exploratory.

![Kaplan-Meier curves by ECOG group](../images/km_by_ecog.png)

**Figure 3.** Kaplan-Meier curves by performance status group.

### 3.5 Proportional hazards

The residual-based check flagged sex and ECOG 2 or higher. Table 2 compares hazard ratios in early and late follow-up (cutoff day 300). This is a post-hoc analysis, and its p-values are not adjusted for multiple testing.

**Table 2. Hazard ratios in early and late follow-up (Model 2)**

| Variable | HR early (day 0 to 300) | HR late (after day 300) | Ratio of HRs, late vs early (95% CI) | p for difference |
|---|---|---|---|---|
| Female vs male | 0.47 (0.30 to 0.73) | 0.78 (0.47 to 1.30) | 1.67 (0.85 to 3.29) | 0.139 |
| Age, per 10 years | 1.05 (0.83 to 1.31) | 1.23 (0.91 to 1.68) | 1.18 (0.80 to 1.73) | 0.4 |
| ECOG 1 vs ECOG 0 | 1.92 (1.09 to 3.38) | 1.11 (0.63 to 1.97) | 0.58 (0.26 to 1.29) | 0.182 |
| ECOG 2 or higher vs ECOG 0 | 3.87 (2.11 to 7.08) | 1.28 (0.61 to 2.70) | 0.33 (0.13 to 0.86) | 0.024 |

![Log-minus-log plot by sex](../images/loglog_by_sex.png)

**Figure 4.** Log-minus-log plot by sex. Roughly parallel lines support proportional hazards.

## 4. Discussion

### Principal findings

In this cohort of 228 patients, women had a lower rate of death than men (adjusted HR 0.58, 95% CI 0.41 to 0.80). Adjusting for age and ECOG performance status changed the estimate very little compared with the unadjusted HR of 0.59, so age and performance status do not appear to explain the difference between men and women, although unmeasured factors could still play a part. Patients with ECOG 2 or higher had a higher rate of death than fully active patients (HR 2.50, 95% CI 1.60 to 3.90), while age showed no clear association with survival (HR 1.12 per 10 years, 95% CI 0.93 to 1.34).

### Comparison with other studies

No formal comparison with the published literature was made in this learning project. A fuller report would review the literature on sex differences and performance status in advanced lung cancer.

### What the proportional hazards check means

The residual-based check flagged sex and ECOG 2 or higher. In a post-hoc comparison of early and late follow-up, the hazard ratio for ECOG 2 or higher was 3.87 early and 1.28 late (ratio of hazard ratios 0.33, 95% CI 0.13 to 0.86, p = 0.024), so the single hazard ratio of 2.50 is best read as an average over follow-up. For sex, the early and late hazard ratios were 0.47 and 0.78, but the difference was not clear (p = 0.139). These comparisons were not adjusted for multiple testing, and the late window had fewer deaths, so they should be treated as leads to check and not as confirmed findings.

### Conclusion

In this cohort, women had a lower rate of death than men, and this was not explained by age or performance status, while a worse performance status was associated with a higher rate of death, with the association appearing stronger early in follow-up in an exploratory comparison. These are associations in observational data, so the results do not show that sex or performance status causes a difference in survival.

## 5. Limitations

- The data are observational. Hazard ratios show associations and do not show that sex or performance status causes a difference in survival.
- Adjustment for age and ECOG reduces confounding but cannot remove it. Treatment, stage and other factors are not available.
- The data are old and come from one trial cohort, so the results may not describe patients today.
- The proportional hazards check flagged sex and ECOG 2 or higher. The follow-up comparison was added after seeing the results, was not adjusted for multiple testing, and had limited power in the late window.
- The analysis plan was written for a well-known teaching dataset whose main results are already published. It documents good practice and is not true pre-registration.

## Appendix A. A small meta-analysis (evidence synthesis exercise)

To practise evidence synthesis, a separate meta-analysis pooled 4 published cardiovascular outcome trials of SGLT2 inhibitors in type 2 diabetes (EMPA-REG OUTCOME, CANVAS Program, DECLARE-TIMI 58, VERTIS-CV). The outcome was 3-point MACE. The random-effects pooled hazard ratio was 0.91 (95% CI 0.85 to 0.97), with I-squared of 0%. The trials were chosen as the large well-known outcome trials and were not found by a systematic search. See docs/meta_analysis_plan.md and docs/meta_results.md.

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
