# Time-window check of proportional hazards

This is a post-hoc sensitivity analysis. It was added after the residual check in `cox_analysis.py` flagged sex and ECOG 2 or higher (see the changes table in the [analysis plan](statistical_analysis_plan.md)).

The Cox model (Model 2) was fitted separately for early follow-up (day 0 to 300) and late follow-up (after day 300). If the hazard ratio is about the same in both windows, the proportional hazards assumption is reasonable.

- Early window: 227 patients, 100 deaths
- Late window: 91 patients, 64 deaths

| Variable | HR early (day 0 to 300) | HR late (after day 300) | Ratio of HRs, late vs early (95% CI) | p for difference |
|---|---|---|---|---|
| Female vs male | 0.47 (0.30 to 0.73) | 0.78 (0.47 to 1.30) | 1.67 (0.85 to 3.29) | 0.139 |
| Age, per 10 years | 1.05 (0.83 to 1.31) | 1.23 (0.91 to 1.68) | 1.18 (0.80 to 1.73) | 0.400 |
| ECOG 1 vs ECOG 0 | 1.92 (1.09 to 3.38) | 1.11 (0.63 to 1.97) | 0.58 (0.26 to 1.29) | 0.182 |
| ECOG 2 or higher vs ECOG 0 | 3.87 (2.11 to 7.08) | 1.28 (0.61 to 2.70) | 0.33 (0.13 to 0.86) | 0.024 |

## How to read this

- A ratio of hazard ratios near 1, with an interval that includes 1, gives no sign that the effect changed over time.
- A ratio clearly away from 1 means the effect differs between early and late follow-up. In that case the single hazard ratio in the main analysis is an average, and both windows should be reported.
- The late window has fewer deaths, so the test has limited power. Failing to find a difference does not prove that there is none.
- The cutoff was chosen as a round number near the median survival. A different cutoff could give somewhat different results.
