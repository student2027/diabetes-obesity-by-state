# Diabetes and Obesity by State — United States, 2023

A new data analysis project using **real CDC data only** — no simulated
data, no invented numbers.

**Question:** How much does diagnosed diabetes and obesity prevalence vary
across US states, and do states with higher obesity prevalence also have
higher diabetes prevalence?

**Answer in one line:** Yes, strongly — Pearson r = 0.753 (95% CI 0.598 to
0.853, p < 0.001, n = 49 states + DC). Diabetes ranged from 7.8%
(Vermont) to 15.1% (Mississippi and West Virginia); obesity ranged from
24.3% (DC) to 42.2% (West Virginia). This is an association between
state-level averages, not proof of cause.

## How this differs from the earlier BRFSS project

There is already a BRFSS 2023 project (`r-diabetes-brfss` /
`sas-diabetes-brfss`) on diabetes vs physical activity. That one used a
**simulated individual-level sample (n = 2,000)** because the full BRFSS
microdata file is very large. This project is different in three ways:
it is **state-level** (not individual-level), it uses **real published
CDC prevalence estimates** (not a simulated sample), and it asks about
**obesity** (not physical activity) as the other variable.

## Data

- **Source:** CDC U.S. Chronic Disease Indicators (CDI), dataset
  `hksd-2xuw`, data.cdc.gov — https://data.cdc.gov/resource/hksd-2xuw.csv
  (landing page: https://www.cdc.gov/cdi/overview.html).
  Downloaded 24 November 2026 via the Socrata API, filtered at download to
  2023, age-adjusted prevalence, Overall, for the two questions
  "Diabetes among adults" and "Obesity among adults".
- **Underlying survey:** BRFSS (CDC telephone survey of US adults).
- **Measures:** age-adjusted % of adults aged 18+.
  Diabetes = ever told by a doctor they have diabetes (excluding
  gestational only). Obesity = BMI ≥ 30, from self-reported height
  and weight.
- **Analytic sample:** n = 49 (50 states + DC, both measures present).
  Kentucky and Pennsylvania have "No data available" for both measures
  in 2023 in CDI and are excluded. The US national row (diabetes 10.7%,
  obesity 33.0%) and the territories Guam, Puerto Rico and Virgin Islands
  are in the tidy file but are not in the main analysis.

## Files

| File | What it is |
|---|---|
| `data/cdc_cdi_2023_diabetes_obesity_raw.csv` | Raw CDI download, as downloaded (110 rows) |
| `data/make_tidy.py` | Pivots the raw long file to the tidy file |
| `data/diabetes_obesity_by_state_tidy.csv` | Tidy file, one row per location (55 rows) |
| `analysis.R` | Full analysis, base R only |
| `analysis.py` | Full analysis, pandas / scipy |
| `brief.py` | Builds the charts and the 2-page brief PDF |
| `results.md` | Full results, methods, limitations, full state table |
| `output/diabetes-obesity-by-state-brief.pdf` | 2-page brief (Letter) |
| `output/fig_diabetes_by_state.png` | Diabetes bar chart (top 10 + bottom 5) |
| `output/fig_obesity_by_state.png` | Obesity bar chart (top 10 + bottom 5) |
| `output/fig_scatter.png` | Scatter: diabetes vs obesity, with regression line |
| `output/summary_statistics.csv` | Descriptive statistics |
| `output/model_results.csv` | Correlation and regression |
| `output/top_bottom_states.csv` | Top/bottom 5 for each measure |

## How to run

From the project folder:

```bash
# 1. (Re)make the tidy file from the raw download — optional, it already exists
python3 data/make_tidy.py

# 2. Run the analysis in Python
python3 analysis.py

# 3. Run the same analysis in R (base R only, no extra packages)
Rscript analysis.R

# 4. Rebuild the charts and the 2-page brief PDF
python3 brief.py
```

Both analysis scripts load `data/diabetes_obesity_by_state_tidy.csv`,
describe diabetes and obesity prevalence (mean, median, SD, range,
top/bottom 5), compute the Pearson correlation with a 95% CI, and fit
the simple linear regression of diabetes prevalence on obesity
prevalence. They print the same results to the console and write the
same summary tables to `output/`.

## Headline findings (from the real runs)

- Diabetes: mean 10.38%, median 10.10%, range 7.8–15.1%.
  Highest: Mississippi 15.1%, West Virginia 15.1%, Louisiana 14.6%.
  Lowest: Vermont 7.8%, Montana 7.9%, New Hampshire 7.9%.
- Obesity: mean 33.94%, median 34.50%, range 24.3–42.2%.
  Highest: West Virginia 42.2%, Mississippi 41.0%, Arkansas 40.9%.
  Lowest: District of Columbia 24.3%, Colorado 24.7%, Hawaii 26.8%.
- Texas: diabetes 12.1%, obesity 34.6%.
- Correlation: r = 0.753 (95% CI 0.598–0.853), p = 4.44 × 10⁻¹⁰.
- Regression: diabetes = −0.812 + 0.330 × obesity; R² = 0.567;
  slope 95% CI 0.245–0.414 (R, t-distribution; Python's normal
  approximation gives 0.247–0.412).

See `results.md` for the full table, methods and limitations, and
`output/diabetes-obesity-by-state-brief.pdf` for the 2-page brief.
