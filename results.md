# Diabetes and Obesity by State, United States, 2023

**Question:** How much does diagnosed diabetes and obesity prevalence vary
across US states, and do states with higher obesity prevalence also have
higher diabetes prevalence?

**This is a new, different project from the BRFSS 2023 simulated-sample
project** (diabetes vs physical activity, n = 2,000). That project used a
simulated individual-level sample. This project uses real, published
state-level prevalence estimates from the CDC — no simulated data, no
invented numbers.

## Data source (real CDC data only)

- **Source:** CDC U.S. Chronic Disease Indicators (CDI), dataset `hksd-2xuw`,
  on CDC's open data portal, data.cdc.gov.
  - Landing page: https://www.cdc.gov/cdi/overview.html
  - Dataset: https://data.cdc.gov/resource/hksd-2xuw.csv
  - Downloaded: 24 November 2026, via the Socrata API, filtered at download to:
    `question IN ('Diabetes among adults', 'Obesity among adults')`
    `AND yearstart = 2023 AND datavaluetype = 'Age-adjusted Prevalence'`
    `AND stratificationcategory1 = 'Overall'`
  - Raw file kept as downloaded: `data/cdc_cdi_2023_diabetes_obesity_raw.csv`
    (110 rows: 55 locations × 2 measures, 30 KB).
- **Underlying survey:** Behavioral Risk Factor Surveillance System (BRFSS),
  a CDC telephone survey of US adults. The CDI `datasource` column is
  "BRFSS" for both measures.
- **Year:** 2023 (both measures).
- **Measures, age-adjusted prevalence (%) among adults aged 18+, Overall:**
  - *Diabetes among adults:* % of adults who report ever having been told
    by a doctor that they have diabetes (excluding gestational diabetes only).
  - *Obesity among adults:* % of adults with BMI ≥ 30, from self-reported
    height and weight.
- **Tidy file:** `data/diabetes_obesity_by_state_tidy.csv`, made by
  `data/make_tidy.py` (pivots the raw long file to one row per location).
  It has 55 rows: 50 states + DC, the "United States" national row, and
  3 territories (Guam, Puerto Rico, Virgin Islands).

## Analytic sample

- **Included in the main analysis: n = 49** — the 50 states plus the
  District of Columbia, with both measures present.
- **Excluded — no data:** Kentucky and Pennsylvania. CDI reports
  "No data available" for both measures for both states in 2023.
- **Excluded — not states:** the "United States" national row
  (diabetes 10.7%, obesity 33.0%) and the territories Guam (diabetes 16.2%,
  obesity 33.5%), Puerto Rico (16.1%, 36.7%) and Virgin Islands (12.2%,
  31.5%). Their values are kept in the tidy file for reference; they are
  not in any headline number, correlation or regression.

## Results

All numbers below are copied from the actual runs of `analysis.py`
(Python, pandas/scipy) and `analysis.R` (base R). The two scripts gave
identical results, except for the regression slope confidence interval,
where Python used a normal approximation (0.247 to 0.412) and R used the
standard t-distribution interval (0.245 to 0.414). The R interval is
reported as primary below.

### Descriptive statistics (n = 49)

| Measure | Mean | Median | SD | Range |
|---|---|---|---|---|
| Diabetes prevalence (%) | 10.38 | 10.10 | 1.87 | 7.8 to 15.1 |
| Obesity prevalence (%) | 33.94 | 34.50 | 4.28 | 24.3 to 42.2 |

### Diabetes — highest and lowest

Highest 5: Mississippi 15.1%, West Virginia 15.1%, Louisiana 14.6%,
Alabama 14.0%, Arkansas 13.1%.
Lowest 5: Vermont 7.8%, Montana 7.9%, New Hampshire 7.9%, Colorado 8.0%,
Utah 8.1%.
Texas: 12.1% (95% CI 11.0–13.3). US national figure: 10.7%.

### Obesity — highest and lowest

Highest 5: West Virginia 42.2%, Mississippi 41.0%, Arkansas 40.9%,
Louisiana 40.2%, Alabama 39.9%.
Lowest 5: District of Columbia 24.3%, Colorado 24.7%, Hawaii 26.8%,
Massachusetts 27.4%, California 27.9%.
Texas: 34.6% (95% CI 32.9–36.4). US national figure: 33.0%.

The same five states — West Virginia, Mississippi, Arkansas, Louisiana
and Alabama — lead both lists, in a different order.

### Correlation

Pearson correlation between obesity prevalence and diabetes prevalence
across the 49 states + DC:

- **r = 0.753 (95% CI 0.598 to 0.853), p = 4.44 × 10⁻¹⁰**

### Simple linear regression: diabetes on obesity

Diabetes prevalence = intercept + slope × obesity prevalence:

- **Intercept = -0.812**
- **Slope = 0.330** percentage points of diabetes per 1 percentage point
  of obesity (95% CI 0.245 to 0.414, t-distribution, R)
- **R-squared = 0.567** — obesity prevalence alone accounts for 56.7% of
  the variation in diabetes prevalence across states in this simple model.
- **Slope p-value = 4.44 × 10⁻¹⁰**

### Interpretation (plain English)

States with higher obesity prevalence tend to have higher diabetes
prevalence, and the association is strong and positive. This is an
association between state-level averages, not proof that obesity causes
diabetes in individuals, and not proof that changing a state's obesity
level would change its diabetes level by 0.33 points. Other differences
between states — age, income, race/ethnicity, health care, diet, physical
activity — could explain part of the pattern, and this simple regression
does not control for any of them.

## Methods

1. Downloaded the CDI file from data.cdc.gov (see source above).
2. Kept the 2023, age-adjusted, Overall rows for the two questions.
3. Pivoted to one row per location (`data/make_tidy.py`).
4. Restricted the analysis to the 50 states + DC with both values (n = 49).
5. Computed descriptive statistics, top/bottom 5, Pearson correlation
   with Fisher-z 95% CI, and ordinary least-squares regression of
   diabetes on obesity, in both R and Python.

## Limitations

- **Ecological:** state averages only; the state-level association does
  not prove the same link holds for individuals.
- **Cross-sectional, one year (2023):** no trend, no timing, no causality.
- **Self-reported:** diagnosis, height and weight are self-reported in
  BRFSS; height and weight are often misreported and some diabetes is
  undiagnosed.
- **No adjustment:** the regression controls for nothing except
  age-adjustment of the prevalences themselves.
- **Missing states:** Kentucky and Pennsylvania have no 2023 values in
  CDI, so the picture is incomplete.
- **Model-based? No** — these CDI values are survey prevalence estimates,
  not PLACES model-based small-area estimates. Do not confuse the two.

## Files

| File | What it is |
|---|---|
| `data/cdc_cdi_2023_diabetes_obesity_raw.csv` | Raw CDI download, as downloaded (110 rows) |
| `data/make_tidy.py` | Script that pivots the raw file to the tidy file |
| `data/diabetes_obesity_by_state_tidy.csv` | Tidy file, one row per location (55 rows) |
| `analysis.R` | Full analysis, base R only — run `Rscript analysis.R` |
| `analysis.py` | Full analysis, pandas/scipy — run `python3 analysis.py` |
| `brief.py` | Builds the charts and the 2-page brief PDF |
| `output/diabetes-obesity-by-state-brief.pdf` | 2-page brief (Letter) |
| `output/fig_diabetes_by_state.png` | Diabetes bar chart (top 10 + bottom 5) |
| `output/fig_obesity_by_state.png` | Obesity bar chart (top 10 + bottom 5) |
| `output/fig_scatter.png` | Scatter: diabetes vs obesity, with regression line |
| `output/summary_statistics.csv` | Descriptive statistics (from Python; R version in `summary_statistics_r.csv`) |
| `output/model_results.csv` | Correlation and regression (Python; R version in `model_results_r.csv`) |
| `output/top_bottom_states.csv` | Top/bottom 5 for each measure (Python; R version in `top_bottom_states_r.csv`) |

## Verification

- `python3 analysis.py` — exit 0 (R 4.3.3 / Python 3.12.3, 24 Nov 2026).
- `Rscript analysis.R` — exit 0. First run failed only because the tidy
  CSV stores True/False as text and R read it as character; fixed by
  comparing to the string `"True"` (see the comment in `analysis.R`).
  After the fix, R and Python gave identical descriptive statistics,
  top/bottom lists, correlation (r = 0.753, CI 0.598–0.853, p = 4.44e-10),
  intercept (-0.812), slope (0.330) and R-squared (0.567).
- Brief PDF: 2 pages, Letter, verified with `pdfinfo`. Every number in
  the brief was checked against the script output above.

## Full state table (n = 49, age-adjusted %, 2023)

| State | Diabetes % | 95% CI | Obesity % | 95% CI |
|---|---|---|---|---|
| Alabama | 14.0 | 12.7–15.3 | 39.9 | 37.8–42.0 |
| Alaska | 8.2 | 7.4–9.2 | 35.3 | 33.4–37.2 |
| Arizona | 9.9 | 9.2–10.7 | 32.6 | 31.1–34.1 |
| Arkansas | 13.1 | 12.0–14.3 | 40.9 | 39.0–42.8 |
| California | 10.6 | 9.8–11.4 | 27.9 | 26.6–29.2 |
| Colorado | 8.0 | 7.3–8.7 | 24.7 | 23.5–25.9 |
| Connecticut | 8.4 | 7.6–9.3 | 29.6 | 28.0–31.2 |
| Delaware | 11.1 | 9.8–12.6 | 36.0 | 33.6–38.6 |
| District of Columbia | 8.2 | 7.1–9.5 | 24.3 | 22.2–26.6 |
| Florida | 10.1 | 9.1–11.1 | 29.8 | 28.1–31.7 |
| Georgia | 11.5 | 10.7–12.3 | 35.3 | 33.6–37.0 |
| Hawaii | 9.5 | 8.7–10.5 | 26.8 | 25.2–28.5 |
| Idaho | 8.7 | 7.9–9.6 | 31.1 | 29.6–32.8 |
| Illinois | 10.9 | 9.9–12.1 | 36.0 | 34.1–37.9 |
| Indiana | 11.7 | 11.1–12.4 | 38.4 | 37.1–39.7 |
| Iowa | 9.9 | 9.2–10.7 | 38.4 | 36.9–39.8 |
| Kansas | 10.5 | 9.7–11.3 | 36.7 | 35.3–38.1 |
| Louisiana | 14.6 | 13.4–15.8 | 40.2 | 38.3–42.1 |
| Maine | 9.0 | 8.4–9.7 | 32.9 | 31.4–34.5 |
| Maryland | 10.9 | 10.2–11.7 | 34.1 | 32.8–35.4 |
| Massachusetts | 8.5 | 7.8–9.4 | 27.4 | 26.0–28.9 |
| Michigan | 10.9 | 10.1–11.8 | 35.6 | 34.1–37.1 |
| Minnesota | 9.3 | 8.6–10.0 | 33.2 | 32.1–34.4 |
| Mississippi | 15.1 | 13.7–16.6 | 41.0 | 38.9–43.2 |
| Missouri | 10.7 | 9.9–11.7 | 35.5 | 33.8–37.2 |
| Montana | 7.9 | 7.2–8.7 | 30.4 | 28.9–32.0 |
| Nebraska | 9.7 | 9.0–10.3 | 37.0 | 35.8–38.2 |
| Nevada | 10.8 | 8.9–13.0 | 31.0 | 28.0–34.1 |
| New Hampshire | 7.9 | 7.1–8.8 | 32.9 | 30.9–35.0 |
| New Jersey | 9.1 | 8.4–9.9 | 28.7 | 27.2–30.2 |
| New Mexico | 10.8 | 9.3–12.6 | 36.6 | 33.8–39.5 |
| New York | 9.5 | 8.9–10.1 | 28.1 | 27.0–29.2 |
| North Carolina | 11.0 | 9.8–12.3 | 34.0 | 31.8–36.2 |
| North Dakota | 8.9 | 8.1–9.7 | 36.1 | 34.4–37.9 |
| Ohio | 11.5 | 10.8–12.2 | 36.8 | 35.5–38.2 |
| Oklahoma | 11.3 | 10.5–12.1 | 39.4 | 37.8–40.9 |
| Oregon | 9.5 | 8.7–10.5 | 33.5 | 31.8–35.1 |
| Rhode Island | 10.0 | 9.1–11.0 | 32.3 | 30.4–34.3 |
| South Carolina | 12.7 | 11.9–13.6 | 36.2 | 34.7–37.8 |
| South Dakota | 10.7 | 8.9–12.8 | 36.6 | 33.4–40.0 |
| Tennessee | 12.7 | 11.7–13.8 | 38.0 | 36.2–39.9 |
| Texas | 12.1 | 11.0–13.3 | 34.6 | 32.9–36.4 |
| Utah | 8.1 | 7.5–8.7 | 30.9 | 29.8–32.2 |
| Vermont | 7.8 | 7.0–8.7 | 29.5 | 27.8–31.2 |
| Virginia | 10.4 | 9.5–11.4 | 34.5 | 32.8–36.4 |
| Washington | 8.6 | 8.2–9.0 | 30.8 | 30.0–31.6 |
| West Virginia | 15.1 | 13.9–16.3 | 42.2 | 40.1–44.2 |
| Wisconsin | 9.6 | 9.0–10.2 | 35.9 | 34.5–37.2 |
| Wyoming | 9.4 | 8.5–10.5 | 33.6 | 31.6–35.7 |

Kentucky and Pennsylvania: no data available in CDI for 2023 (both measures).
