# Meta-Analysis Plan

**Topic:** SGLT2 inhibitors and 3-point MACE in type 2 diabetes
**Version:** 1.0
**Status:** Plan text drafted before pooling any results. It was saved into this repository on 20 October 2026 (see section 7).

> This is a learning project. It is a small teaching meta-analysis and not a systematic review. It is not clinical advice.

## 1. Question

Do SGLT2 inhibitors reduce 3-point MACE compared with placebo in adults with type 2 diabetes?

| Element | Definition |
|---|---|
| Population | Adults with type 2 diabetes and established cardiovascular disease or high cardiovascular risk |
| Intervention | An SGLT2 inhibitor (empagliflozin, canagliflozin, dapagliflozin or ertugliflozin) |
| Comparator | Placebo, on top of standard care |
| Outcome | First occurrence of 3-point MACE: cardiovascular death, non-fatal myocardial infarction or non-fatal stroke |
| Design | Randomised, placebo-controlled cardiovascular outcome trials |

## 2. Choice of trials

The four large SGLT2 inhibitor cardiovascular outcome trials that reported 3-point MACE as a primary or co-primary outcome: EMPA-REG OUTCOME, CANVAS Program, DECLARE-TIMI 58 and VERTIS-CV.

**This was not a systematic search.** The trials were chosen as the well-known large outcome trials, so selection bias is possible.

Not included: CREDENCE and similar trials in kidney disease or heart failure populations, because their primary outcomes and populations differ.

## 3. Data extraction

- The hazard ratio and 95% confidence interval for 3-point MACE were taken from each trial's publication and are stored in `data/meta_trials.csv`.
- EMPA-REG (95.02%) and VERTIS-CV (95.6%) report slightly different interval levels because of interim analyses. They are treated as 95% intervals.
- The standard error of the log hazard ratio is calculated from the interval: (log upper limit minus log lower limit) divided by 3.92.

## 4. Analysis

1. **Primary analysis:** random-effects meta-analysis (DerSimonian-Laird) of log hazard ratios, with inverse-variance weights. This is chosen because the drugs, populations and follow-up differ.
2. **Secondary:** fixed-effect meta-analysis, shown for comparison.
3. **Heterogeneity:** Cochran's Q, I-squared and tau-squared. With only four trials these have low power, so a low I-squared will not be read as proof that the trials are alike.
4. **Sensitivity analysis:** leave-one-out, repeating the pooling with each trial removed in turn.
5. **Presentation:** forest plot with study weights and both pooled estimates.

## 5. Not done, and why

- **Publication bias:** a funnel plot or test is not informative with four trials.
- **Formal risk of bias assessment:** not done in this teaching project.
- **Subgroups and meta-regression:** too few trials.

## 6. Limitations (stated in advance)

- Four trials, no systematic search, and only aggregate data.
- The trials differ in drug, population (for example the share of patients with established cardiovascular disease) and follow-up.
- Several outcome trials were designed mainly to show safety, with non-inferiority as the main test.
- Results describe the trial populations and may not apply to every patient.

## 7. Changes to this plan

| Date | Change | Reason |
|---|---|---|
| 2026-10-20 | The plan text was saved into this file | The file was empty when the meta-analysis was run on 19 October 2026. The plan had been drafted beforehand, but it was not saved in the repository until now. The analysis followed this plan. |