"""Make the tidy state-level file from the raw CDC CDI download.

Source: CDC U.S. Chronic Disease Indicators (CDI), dataset hksd-2xuw on
data.cdc.gov. Raw file: data/cdc_cdi_2023_diabetes_obesity_raw.csv
Downloaded 2026-11-24 via the Socrata API, filtered at download to:
  question IN ('Diabetes among adults', 'Obesity among adults')
  AND yearstart = 2023 AND datavaluetype = 'Age-adjusted Prevalence'
  AND stratificationcategory1 = 'Overall'
URL (same filter):
https://data.cdc.gov/resource/hksd-2xuw.csv?$limit=5000&$where=question%20in%20('Diabetes%20among%20adults','Obesity%20among%20adults')%20AND%20yearstart=2023%20AND%20datavaluetype='Age-adjusted%20Prevalence'%20AND%20stratificationcategory1='Overall'

Both measures come from BRFSS (the CDI 'datasource' column).
Definitions (CDC CDI):
- Diabetes among adults: % of adults aged >=18 who report ever having
  been told by a doctor that they have diabetes (excluding gestational).
  Age-adjusted prevalence.
- Obesity among adults: % of adults aged >=18 with BMI >= 30, from
  self-reported height and weight. Age-adjusted prevalence.

This script pivots the raw long file (one row per location x measure)
to one row per location, and flags the analytic sample:
  - 50 states + District of Columbia, with both measures present: n = 49
  - Excluded from the main analysis: the "United States" national row
    (not a state), and Guam, Puerto Rico, Virgin Islands (territories,
    not states; their values are kept in the tidy file for reference).
  - Kentucky and Pennsylvania have "No data available" for both measures
    in 2023 in CDI, so they have no values and are excluded.
Run: python3 data/make_tidy.py
"""
import csv

RAW = "data/cdc_cdi_2023_diabetes_obesity_raw.csv"
OUT = "data/diabetes_obesity_by_state_tidy.csv"

STATES_DC = {
    "Alabama","Alaska","Arizona","Arkansas","California","Colorado",
    "Connecticut","Delaware","District of Columbia","Florida","Georgia",
    "Hawaii","Idaho","Illinois","Indiana","Iowa","Kansas","Kentucky",
    "Louisiana","Maine","Maryland","Massachusetts","Michigan","Minnesota",
    "Mississippi","Missouri","Montana","Nebraska","Nevada","New Hampshire",
    "New Jersey","New Mexico","New York","North Carolina","North Dakota",
    "Ohio","Oklahoma","Oregon","Pennsylvania","Rhode Island",
    "South Carolina","South Dakota","Tennessee","Texas","Utah","Vermont",
    "Virginia","Washington","West Virginia","Wisconsin","Wyoming",
}

rows = {}
with open(RAW, newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        loc = r["locationdesc"]
        q = r["question"]
        val = r["datavalue"].strip() if r["datavalue"] else ""
        lo = r["lowconfidencelimit"].strip() if r["lowconfidencelimit"] else ""
        hi = r["highconfidencelimit"].strip() if r["highconfidencelimit"] else ""
        foot = r["datavaluefootnote"].strip() if r["datavaluefootnote"] else ""
        d = rows.setdefault(loc, {"state": loc, "abbr": r["locationabbr"]})
        if q == "Diabetes among adults":
            d["diabetes_pct"] = val
            d["diabetes_low"] = lo
            d["diabetes_high"] = hi
            d["diabetes_footnote"] = foot
        elif q == "Obesity among adults":
            d["obesity_pct"] = val
            d["obesity_low"] = lo
            d["obesity_high"] = hi
            d["obesity_footnote"] = foot

fields = ["state","abbr","diabetes_pct","diabetes_low","diabetes_high",
          "diabetes_footnote","obesity_pct","obesity_low","obesity_high",
          "obesity_footnote","is_state_or_dc","included_in_analysis"]
with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for loc in sorted(rows):
        d = rows[loc]
        is_sd = loc in STATES_DC
        included = is_sd and bool(d.get("diabetes_pct")) and bool(d.get("obesity_pct"))
        w.writerow({
            "state": loc, "abbr": d["abbr"],
            "diabetes_pct": d.get("diabetes_pct",""),
            "diabetes_low": d.get("diabetes_low",""),
            "diabetes_high": d.get("diabetes_high",""),
            "diabetes_footnote": d.get("diabetes_footnote",""),
            "obesity_pct": d.get("obesity_pct",""),
            "obesity_low": d.get("obesity_low",""),
            "obesity_high": d.get("obesity_high",""),
            "obesity_footnote": d.get("obesity_footnote",""),
            "is_state_or_dc": str(is_sd),
            "included_in_analysis": str(included),
        })
n = sum(1 for d in rows.values())
n_inc = sum(1 for loc in rows if loc in STATES_DC and rows[loc].get("diabetes_pct") and rows[loc].get("obesity_pct"))
print(f"locations in tidy file: {n}")
print(f"included in main analysis (50 states + DC, both measures present): {n_inc}")
print(f"wrote {OUT}")
