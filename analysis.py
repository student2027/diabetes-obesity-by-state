"""
Diabetes and obesity by state, United States, 2023 — Python analysis.

Data: CDC U.S. Chronic Disease Indicators (CDI), dataset hksd-2xuw,
  downloaded 2026-11-24 from data.cdc.gov (BRFSS as the underlying source).
  Tidy file: data/diabetes_obesity_by_state_tidy.csv
  (made by data/make_tidy.py from the raw CDI download).
Measures: age-adjusted prevalence (%) among adults aged >= 18, Overall.
  Diabetes: ever told by a doctor they have diabetes (excluding gestational).
  Obesity: BMI >= 30, from self-reported height and weight.
Analytic sample: 50 states + District of Columbia with both measures
  present, n = 49. Kentucky and Pennsylvania have "No data available"
  for both measures in 2023 in CDI and are excluded. The "United States"
  national row and the territories (Guam, Puerto Rico, Virgin Islands)
  are in the tidy file but excluded from the main analysis.

Run: python3 analysis.py   (from the project folder)
Requires: pandas, numpy, scipy.
Writes: output/summary_statistics.csv, output/top_bottom_states.csv
        and prints the results to the console.
This is an ecological, cross-sectional analysis of state-level
prevalence. It describes association only — it cannot show that
obesity causes diabetes, or that one state's obesity level causes
its diabetes level.
"""
import math

import numpy as np
import pandas as pd
from scipy import stats

DATA = "data/diabetes_obesity_by_state_tidy.csv"

df = pd.read_csv(DATA)
# Analytic sample: states + DC, both measures present
an = df[df["included_in_analysis"] == True].copy()  # noqa: E712
an["diabetes_pct"] = pd.to_numeric(an["diabetes_pct"])
an["obesity_pct"] = pd.to_numeric(an["obesity_pct"])
an = an.dropna(subset=["diabetes_pct", "obesity_pct"])
n = len(an)
print(f"States + DC included in analysis: n = {n}")
print(f"States + DC excluded (no data): "
      f"{sorted(df[(df['is_state_or_dc'] == True) & (df['included_in_analysis'] == False)]['state'])}")  # noqa: E712

# --- Descriptive statistics ---
def describe(s):
    return {
        "mean": s.mean(),
        "median": s.median(),
        "sd": s.std(ddof=1),
        "min": s.min(),
        "max": s.max(),
    }

d_d = describe(an["diabetes_pct"])
d_o = describe(an["obesity_pct"])
print("\nDIABETES prevalence (age-adjusted %, adults 18+), 2023")
print(f"  mean {d_d['mean']:.2f}  median {d_d['median']:.2f}  SD {d_d['sd']:.2f}  "
      f"range {d_d['min']:.1f} to {d_d['max']:.1f}")
print("OBESITY prevalence (age-adjusted %, adults 18+), 2023")
print(f"  mean {d_o['mean']:.2f}  median {d_o['median']:.2f}  SD {d_o['sd']:.2f}  "
      f"range {d_o['min']:.1f} to {d_o['max']:.1f}")

for col, label in [("diabetes_pct", "Diabetes"), ("obesity_pct", "Obesity")]:
    top = an.nlargest(5, col)[["state", col]]
    bot = an.nsmallest(5, col)[["state", col]]
    print(f"\nTop 5 {label} prevalence:")
    for _, row in top.iterrows():
        print(f"  {row['state']}: {row[col]:.1f}%")
    print(f"Bottom 5 {label} prevalence:")
    for _, row in bot.iterrows():
        print(f"  {row['state']}: {row[col]:.1f}%")
    tx = an.loc[an["state"] == "Texas", col].iloc[0]
    print(f"Texas {label}: {tx:.1f}%")

# --- Correlation (Pearson), with Fisher z 95% CI ---
r, p_r = stats.pearsonr(an["obesity_pct"], an["diabetes_pct"])
z = math.atanh(r)
se_z = 1.0 / math.sqrt(n - 3)
ci_lo, ci_hi = math.tanh(z - 1.96 * se_z), math.tanh(z + 1.96 * se_z)
print(f"\nCORRELATION between obesity and diabetes prevalence across states:")
print(f"  Pearson r = {r:.3f}  (95% CI {ci_lo:.3f} to {ci_hi:.3f}),  p = {p_r:.4g}")

# --- Simple linear regression: diabetes ~ obesity ---
res = stats.linregress(an["obesity_pct"], an["diabetes_pct"])
print("\nLINEAR REGRESSION: diabetes prevalence = intercept + slope x obesity prevalence")
print(f"  intercept = {res.intercept:.3f}")
print(f"  slope = {res.slope:.3f} percentage points of diabetes per "
      f"1 percentage point of obesity")
print(f"  R-squared = {res.rvalue ** 2:.3f}")
print(f"  slope p-value = {res.pvalue:.4g}")
print(f"  slope 95% CI = {res.slope - 1.96 * res.stderr:.3f} to "
      f"{res.slope + 1.96 * res.stderr:.3f}")

print("\nINTERPRETATION (plain English):")
print("  States with higher obesity prevalence tend to have higher diabetes")
print("  prevalence, and the association is strong and positive. This is an")
print("  association between state-level averages, not proof that obesity")
print("  causes diabetes in individuals, and not proof that changing a")
print("  state's obesity level would change its diabetes level by the")
print("  regression slope. Other state differences (age, income, health")
print("  care, diet, physical activity) could explain part of the pattern.")

# --- Save summary tables ---
summary = pd.DataFrame([
    {"measure": "diabetes_pct", "n": n, **{k: round(v, 2) for k, v in d_d.items()}},
    {"measure": "obesity_pct", "n": n, **{k: round(v, 2) for k, v in d_o.items()}},
])
summary.to_csv("output/summary_statistics.csv", index=False)
model = pd.DataFrame([
    {"analysis": "pearson_r_obesity_diabetes", "n": n, "estimate": round(r, 3),
     "ci_low": round(ci_lo, 3), "ci_high": round(ci_hi, 3), "p_value": p_r,
     "extra": ""},
    {"analysis": "regression_diabetes_on_obesity", "n": n, "estimate": round(res.slope, 3),
     "ci_low": round(res.slope - 1.96 * res.stderr, 3),
     "ci_high": round(res.slope + 1.96 * res.stderr, 3), "p_value": res.pvalue,
     "extra": f"intercept={res.intercept:.3f}; R-squared={res.rvalue ** 2:.3f}"},
])
model.to_csv("output/model_results.csv", index=False)

top_bottom = []
for col in ["diabetes_pct", "obesity_pct"]:
    for rank, (_, row) in enumerate(an.nlargest(5, col).iterrows(), 1):
        top_bottom.append({"measure": col, "rank": f"top_{rank}",
                           "state": row["state"], "value_pct": row[col]})
    for rank, (_, row) in enumerate(an.nsmallest(5, col).iterrows(), 1):
        top_bottom.append({"measure": col, "rank": f"bottom_{rank}",
                           "state": row["state"], "value_pct": row[col]})
pd.DataFrame(top_bottom).to_csv("output/top_bottom_states.csv", index=False)
print("\nWrote output/summary_statistics.csv, output/model_results.csv and output/top_bottom_states.csv")
