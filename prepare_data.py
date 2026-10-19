"""
Phase 2: prepare the analysis dataset and build Table 1.

Reads data/lung.csv (created by get_data.py).
Writes data/analysis_data.csv, output/table1.csv and docs/table1.md.
"""
from pathlib import Path

import pandas as pd

for folder in ["data", "output", "docs"]:
    Path(folder).mkdir(exist_ok=True)

df = pd.read_csv("data/lung.csv")
print(f"Loaded {len(df)} patients\n")

# ---------- 1. Data checks ----------
checks = [
    ("Follow-up times are all positive", (df["time"] > 0).all()),
    ("Event is 0 or 1", df["event"].isin([0, 1]).all()),
    ("Sex is Male or Female", df["sex_label"].isin(["Male", "Female"]).all()),
    ("Age is between 18 and 100", df["age"].between(18, 100).all()),
    ("ECOG is 0 to 4 when recorded", df["ph_ecog"].dropna().isin([0, 1, 2, 3, 4]).all()),
    ("Karnofsky scores are 0 to 100 when recorded",
     pd.concat([df["ph_karno"], df["pat_karno"]]).dropna().between(0, 100).all()),
]
failed = False
for label, ok in checks:
    print(f"{'PASS' if ok else 'FAIL'}  {label}")
    failed = failed or not ok
if failed:
    raise SystemExit("\nFix the data problems above before going on.")

# ---------- 2. Analysis dataset ----------
df.insert(0, "patient_id", range(1, len(df) + 1))
df["female"] = (df["sex_label"] == "Female").astype(int)
df["ecog_group"] = pd.cut(
    df["ph_ecog"], bins=[-0.5, 1.5, 4.5], labels=["0-1", "2 or higher"]
).astype("object")
df["complete_case"] = df[["time", "event", "female", "age", "ph_ecog"]].notna().all(axis=1)

analysis_columns = ["patient_id", "time", "event", "sex_label", "female", "age",
                    "ph_ecog", "ecog_group", "ph_karno", "pat_karno",
                    "wt_loss", "meal_cal", "complete_case"]
df[analysis_columns].to_csv("data/analysis_data.csv", index=False)

print("\nECOG performance score (0 = fully active ... 4 = bedbound):")
print(df["ph_ecog"].value_counts(dropna=False).sort_index().to_string())
print("\nPatients with complete data for the adjusted model:",
      int(df["complete_case"].sum()))

# ---------- 3. Table 1 ----------
def med_range(series):
    s = series.dropna()
    return f"{s.median():g} ({s.min():g}-{s.max():g})" if len(s) else "n/a"


def n_pct(count, total):
    return f"{int(count)} ({count / total * 100:.0f}%)" if total else "n/a"


def summarise(d):
    """Return the Table 1 rows (label, value) for one group of patients."""
    known = d["ph_ecog"].notna().sum()
    return [
        ("Patients, n", str(len(d))),
        ("Age, years: median (range)", med_range(d["age"])),
        ("ECOG 0, n (%)", n_pct((d["ph_ecog"] == 0).sum(), known)),
        ("ECOG 1, n (%)", n_pct((d["ph_ecog"] == 1).sum(), known)),
        ("ECOG 2 or higher, n (%)", n_pct((d["ph_ecog"] >= 2).sum(), known)),
        ("ECOG missing, n", str(int(d["ph_ecog"].isna().sum()))),
        ("Karnofsky score, doctor: median (range)", med_range(d["ph_karno"])),
        ("Karnofsky score, doctor, missing, n", str(int(d["ph_karno"].isna().sum()))),
        ("Karnofsky score, patient: median (range)", med_range(d["pat_karno"])),
        ("Karnofsky score, patient, missing, n", str(int(d["pat_karno"].isna().sum()))),
        ("Weight loss, last 6 months (lb): median (range)", med_range(d["wt_loss"])),
        ("Weight loss missing, n", str(int(d["wt_loss"].isna().sum()))),
        ("Calories at meals: median (range)", med_range(d["meal_cal"])),
        ("Calories at meals missing, n", str(int(d["meal_cal"].isna().sum()))),
    ]


groups = {
    "All patients": df,
    "Male": df[df["sex_label"] == "Male"],
    "Female": df[df["sex_label"] == "Female"],
}
labels = [label for label, _ in summarise(df)]
table1 = pd.DataFrame(
    {name: [value for _, value in summarise(d)] for name, d in groups.items()},
    index=labels,
)
table1.to_csv("output/table1.csv", index_label="Characteristic")

header = "| Characteristic | " + " | ".join(table1.columns) + " |"
divider = "|---|" + "|".join(["---"] * len(table1.columns)) + "|"
rows = ["| " + label + " | " + " | ".join(values) + " |"
        for label, values in zip(table1.index, table1.values)]

notes = """
**Notes**

- Numeric variables are shown as median (range), because several are skewed.
- ECOG percentages are of the patients with a recorded score. ECOG 2 or higher combines the small number of patients with scores of 3 or 4, as set out in the analysis plan.
- Weight loss is in pounds (a negative value means weight gain).
- Calories at meals is shown for completeness but is not used in any model, because many values are missing.
- No p-values are shown. Table 1 describes the patients. It is not a test of whether the groups differ.
"""
Path("docs/table1.md").write_text(
    "# Table 1. Baseline characteristics by sex\n\n"
    + "\n".join([header, divider] + rows) + "\n" + notes,
    encoding="utf-8",
)

print("\n" + table1.to_string())

# ---------- 4. Deaths by sex ----------
deaths = df.groupby("sex_label")["event"].agg(patients="size", deaths="sum")
deaths["deaths_percent"] = (deaths["deaths"] / deaths["patients"] * 100).round(0)
print("\nDeaths by sex:")
print(deaths.to_string())

print("\nSaved: data/analysis_data.csv, output/table1.csv, docs/table1.md")