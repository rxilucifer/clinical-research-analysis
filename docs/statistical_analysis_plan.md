# Statistical Analysis Plan

**Project:** Clinical Research Analysis
**Version:** 1.0
**Date:** 19 October 2026
**Status:** Written before running any survival analysis

> This is a learning project. It is not clinical advice, and the dataset is a published teaching dataset.

## 1. Research question

**Primary:** Is overall survival different between women and men with advanced lung cancer?

**Secondary (exploratory):** Is a worse performance status (ECOG 2 or higher) associated with shorter survival?

## 2. Data source

The NCCTG advanced lung cancer data (called `cancer` in the current version of the R `survival` package, and `lung` in older versions): 228 patients.
Reference: Loprinzi CL, et al. J Clin Oncol 1994;12(3):601-607.

## 3. Study population

All 228 patients in the dataset.

## 4. Variables

| Role | Variable | Definition |
|---|---|---|
| Outcome | Overall survival | Time in days from enrolment to death from any cause |
| Event indicator | event | 1 = died, 0 = censored |
| Primary exposure | sex | Male or female |
| Secondary exposure | ECOG group | ECOG 0 or 1, versus ECOG 2 or higher |
| Covariate | age | Age in years, treated as a continuous variable |
| Covariate | ECOG | Performance score, used for adjustment in the primary model |

## 5. Methods

1. **Table 1:** baseline characteristics by sex (number and percent for categories, median and range for numbers).
2. **Kaplan-Meier curves** by sex, with median survival and 95% confidence intervals, plus number at risk.
3. **Log-rank test** comparing the two curves.
4. **Cox proportional hazards regression:**
   - Model 1: sex only (unadjusted hazard ratio, female vs male, with 95% confidence interval)
   - Model 2: sex, age and ECOG (adjusted hazard ratio)
5. **Proportional hazards check:** Schoenfeld residuals and a log-minus-log plot. If the assumption looks violated, this will be stated in the report.
6. **Secondary analysis:** the same methods for ECOG 0-1 versus 2 or higher.
7. **Meta-analysis (later phase):** a separate analysis of published trial results, with its own plan.

## 6. Handling of special situations

- **Censoring:** patients alive at the end of follow-up are censored at their last follow-up time.
- **Missing data:** missingness is reported for every variable. Models use complete cases, and no values are imputed.
- **Variables left out:** meal calories is missing for many patients, so it is not used in any model.
- **Small groups:** if fewer than 10 patients are in an ECOG category, it is combined with the next category.

## 7. Significance and interpretation

- Two-sided tests, significance level 0.05.
- The primary question is the only confirmatory analysis. Everything else is exploratory, and p-values from exploratory analyses will not be over-interpreted.
- Effect sizes (hazard ratios) and confidence intervals are reported, not only p-values.

## 8. Software

Python (pandas, statsmodels, matplotlib, and lifelines if available). Code and data are in this repository.

## 9. Limitations (stated in advance)

- The data are observational, so a difference in survival between groups does not show that sex or performance status causes it.
- Residual confounding is possible.
- This is a well-known teaching dataset, so its main results are already published. This plan documents good practice and is not true pre-registration.
- The data are old, from patients treated with the practice of that time, so the results may not describe patients today.

## 10. Changes to this plan

Any change made after the analysis starts will be listed here with the reason.

| Date | Change | Reason |
|---|---|---|
| 2026-10-19 | Model 2 uses the 227 patients with a recorded ECOG score | One patient has a missing ECOG score, found when checking the data. No survival analysis had been run at this point. |
| 2026-10-19 | In Model 2, ECOG is entered as three categories (0, 1, 2 or higher, with 0 as the reference), and age is reported per 10 years | The plan did not say how ECOG enters the model. Only one patient has ECOG 3, so categories are combined, as the plan requires for groups under 10. No Cox model had been run at this point. |
| 2026-10-19 | Added a time-window check of proportional hazards (early vs late follow-up, cutoff at day 300) | The residual check in cox_analysis.py flagged sex and ECOG 2 or higher. This is a post-hoc sensitivity analysis, added after seeing the Model 2 results. |
| 2026-10-19 | The time-window check tests four variables and its p-values are not adjusted for multiplicity | Results are descriptive and are not used to change the primary conclusion. |