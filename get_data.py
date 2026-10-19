"""
Downloads the NCCTG advanced lung cancer dataset (228 patients, from the
R 'survival' package) and saves it as data/lung.csv.

Source: Loprinzi CL, et al. Prospective evaluation of prognostic variables
from patient-completed questionnaires. J Clin Oncol 1994;12(3):601-607.
"""
from pathlib import Path

import statsmodels.api as sm

Path("data").mkdir(exist_ok=True)

# The dataset is called 'lung' in older versions and 'cancer' in newer ones
lung = None
for name in ["lung", "cancer"]:
    try:
        lung = sm.datasets.get_rdataset(name, "survival").data
        print(f"Loaded '{name}' from the R 'survival' package\n")
        break
    except ValueError:
        print(f"'{name}' was not found, trying the next name...")

if lung is None:
    raise SystemExit("Could not find the lung cancer data under either name.")

expected = {"time", "status", "age", "sex", "ph.ecog"}
if not expected <= set(lung.columns):
    raise SystemExit(f"Unexpected columns. Found: {list(lung.columns)}")

lung = lung.rename(columns={
    "ph.ecog": "ph_ecog", "ph.karno": "ph_karno", "pat.karno": "pat_karno",
    "meal.cal": "meal_cal", "wt.loss": "wt_loss",
})

# In this dataset: status 1 = censored, 2 = dead; sex 1 = male, 2 = female
lung["event"] = (lung["status"] == 2).astype(int)
lung["sex_label"] = lung["sex"].map({1: "Male", 2: "Female"})
lung.to_csv("data/lung.csv", index=False)

print(f"Saved {len(lung)} patients to data/lung.csv\n")
print("Columns:", ", ".join(lung.columns), "\n")
print("Missing values per column:")
print(lung.isna().sum().to_string(), "\n")
print("Outcome (1 = died, 0 = censored):")
print(lung["event"].value_counts().to_string(), "\n")
print("Patients by sex:")
print(lung["sex_label"].value_counts().to_string(), "\n")
print("Follow-up time in days:")
print(lung["time"].describe().round(0).to_string())