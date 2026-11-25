"""Build the 2-page brief PDF for diabetes and obesity by state, 2023.

Reads data/diabetes_obesity_by_state_tidy.csv, recomputes the same
statistics as analysis.py / analysis.R (correlation and regression),
draws the charts with matplotlib, and builds the PDF with reportlab.
Run: python3 brief.py   (from the project folder)
Output: output/diabetes-obesity-by-state-brief.pdf
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.platypus import (Image, KeepTogether, Paragraph,
                                SimpleDocTemplate, Spacer)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT

df = pd.read_csv("data/diabetes_obesity_by_state_tidy.csv")
an = df[df["included_in_analysis"] == True].copy()  # noqa: E712
an["diabetes_pct"] = pd.to_numeric(an["diabetes_pct"])
an["obesity_pct"] = pd.to_numeric(an["obesity_pct"])
an = an.dropna(subset=["diabetes_pct", "obesity_pct"]).sort_values("diabetes_pct")
n = len(an)
r, p_r = stats.pearsonr(an["obesity_pct"], an["diabetes_pct"])
reg = stats.linregress(an["obesity_pct"], an["diabetes_pct"])

# --- Figure 1: diabetes prevalence, top 10 + bottom 5 (readable at this size) ---
an_d = an.sort_values("diabetes_pct")
plot_d = pd.concat([an_d.head(5), an_d.tail(10)])
fig, ax = plt.subplots(figsize=(7.4, 2.4))
colors = ["#d95f02" if s == "Texas" else "#4a7fb5" for s in plot_d["state"]]
ax.barh(plot_d["abbr"], plot_d["diabetes_pct"], color=colors, height=0.65)
ax.set_xlabel("Diagnosed diabetes, age-adjusted % of adults 18+, 2023")
ax.set_title("Diagnosed diabetes: highest 10 and lowest 5 states (n = 49 states + DC)",
             fontsize=10, loc="left")
ax.set_xlim(0, 17)
for i, v in enumerate(plot_d["diabetes_pct"]):
    ax.text(v + 0.2, i, f"{v:.1f}", va="center", fontsize=8)
ax.tick_params(labelsize=8)
plt.tight_layout()
plt.savefig("output/fig_diabetes_by_state.png", dpi=200)
plt.close()

# --- Figure 2: obesity prevalence, top 10 + bottom 5 ---
an_o = an.sort_values("obesity_pct")
plot_o = pd.concat([an_o.head(5), an_o.tail(10)])
fig, ax = plt.subplots(figsize=(7.4, 2.4))
colors = ["#d95f02" if s == "Texas" else "#5a9e6f" for s in plot_o["state"]]
ax.barh(plot_o["abbr"], plot_o["obesity_pct"], color=colors, height=0.65)
ax.set_xlabel("Obesity (BMI >= 30), age-adjusted % of adults 18+, 2023")
ax.set_title("Obesity: highest 10 and lowest 5 states (n = 49 states + DC)",
             fontsize=10, loc="left")
ax.set_xlim(0, 47)
for i, v in enumerate(plot_o["obesity_pct"]):
    ax.text(v + 0.4, i, f"{v:.1f}", va="center", fontsize=8)
ax.tick_params(labelsize=8)
plt.tight_layout()
plt.savefig("output/fig_obesity_by_state.png", dpi=200)
plt.close()

# --- Figure 3: scatter, diabetes vs obesity, with regression line ---
fig, ax = plt.subplots(figsize=(5.2, 2.4))
ax.scatter(an["obesity_pct"], an["diabetes_pct"], s=28, color="#4a7fb5")
xs = np.linspace(an["obesity_pct"].min(), an["obesity_pct"].max(), 50)
ax.plot(xs, reg.intercept + reg.slope * xs, color="#d95f02", lw=1.5)
offsets = {"West Virginia": (-72, 2), "Mississippi": (6, -14),
           "Vermont": (6, 2), "Colorado": (6, 6), "Texas": (6, 4)}
for s, off in offsets.items():
    row = an[an["state"] == s].iloc[0]
    ax.annotate(s, (row["obesity_pct"], row["diabetes_pct"]),
                fontsize=7, xytext=off, textcoords="offset points")
ax.set_xlabel("Obesity %")
ax.set_ylabel("Diabetes %")
ax.set_title(f"Diabetes vs obesity, n = {n}", fontsize=10, loc="left")
ax.text(0.03, 0.94, f"r = {r:.2f}, R\u00b2 = {reg.rvalue**2:.2f}", transform=ax.transAxes, fontsize=8, va="top")
plt.tight_layout()
plt.savefig("output/fig_scatter.png", dpi=200)
plt.close()
print(f"Charts written. r={r:.3f} slope={reg.slope:.3f} R2={reg.rvalue**2:.3f}")

# --- PDF ---
styles = getSampleStyleSheet()
h1 = ParagraphStyle("h1", parent=styles["Title"], fontSize=17, leading=20,
                    spaceAfter=2)
sub = ParagraphStyle("sub", parent=styles["Normal"], fontSize=10, leading=13,
                     spaceAfter=6)
h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=11, leading=13,
                    spaceBefore=4, spaceAfter=2)
body = ParagraphStyle("body", parent=styles["Normal"], fontSize=9,
                      leading=12, spaceAfter=3, alignment=TA_LEFT)
small = ParagraphStyle("small", parent=styles["Normal"], fontSize=8,
                       leading=10.5, spaceAfter=3)
bul = ParagraphStyle("bul", parent=body, leftIndent=12, bulletIndent=4,
                     spaceAfter=2)

doc = SimpleDocTemplate(
    "output/diabetes-obesity-by-state-brief.pdf", pagesize=LETTER,
    leftMargin=0.6 * inch, rightMargin=0.6 * inch,
    topMargin=0.5 * inch, bottomMargin=0.5 * inch,
    title="Diabetes and Obesity by State, United States, 2023")
story = []
story.append(Paragraph("Diabetes and Obesity by State", h1))
story.append(Paragraph(
    "United States, 2023 &mdash; age-adjusted prevalence among adults aged 18 and over "
    "&mdash; November 2026", sub))
story.append(Paragraph(
    "<b>Question.</b> How much does diagnosed diabetes and obesity vary across "
    "US states, and do states with higher obesity prevalence also have higher "
    "diabetes prevalence?", body))
story.append(Paragraph("Headline findings", h2))
story.append(Paragraph(
    "&bull; <b>Diabetes ranged from 7.8% (Vermont) to 15.1% (Mississippi and "
    "West Virginia)</b> across 49 states + DC. Mean 10.4%, median 10.1%. "
    "The five highest were Mississippi 15.1%, West Virginia 15.1%, Louisiana "
    "14.6%, Alabama 14.0% and Arkansas 13.1%.", bul))
story.append(Paragraph(
    "&bull; <b>Obesity ranged from 24.3% (District of Columbia) to 42.2% "
    "(West Virginia).</b> Mean 33.9%, median 34.5%. The five highest were "
    "West Virginia 42.2%, Mississippi 41.0%, Arkansas 40.9%, Louisiana 40.2% "
    "and Alabama 39.9% &mdash; the same five states lead both lists, in a "
    "different order.", bul))
story.append(Paragraph(
    "&bull; <b>Texas sits above the middle for diabetes and near the middle "
    "for obesity:</b> diabetes 12.1% (US national figure 10.7%) and obesity "
    "34.6% (US 33.0%).", bul))
story.append(Paragraph(
    "&bull; <b>The two are strongly associated:</b> Pearson r = 0.753 "
    "(95% CI 0.598 to 0.853, p &lt; 0.001, n = 49). In a simple regression, "
    "each 1-point higher obesity prevalence is associated with 0.33 points "
    "higher diabetes prevalence (95% CI 0.245 to 0.414, R&sup2; = 0.567). "
    "That is an association, not proof of cause.", bul))
story.append(Image("output/fig_diabetes_by_state.png", width=7.3 * inch,
                   height=2.36 * inch))
story.append(Paragraph(
    "Figure 1. Diagnosed diabetes, age-adjusted % of adults 18+, 2023: the "
    "10 highest and 5 lowest states. Texas is highlighted in orange "
    "(12.1%). Source: CDC Chronic Disease "
    "Indicators, BRFSS 2023.", small))
story.append(Image("output/fig_obesity_by_state.png", width=7.3 * inch,
                   height=2.36 * inch))
story.append(Paragraph(
    "Figure 2. Obesity (BMI &ge; 30), age-adjusted % of adults 18+, 2023: the "
    "10 highest and 5 lowest states. Texas is not in either group; its value "
    "is 34.6% (see text). Source: CDC Chronic Disease "
    "Indicators, BRFSS 2023.", small))
story.append(KeepTogether([
    Paragraph("What the scatter shows", h2),
    Image("output/fig_scatter.png", width=5.2 * inch, height=2.4 * inch),
    Paragraph(
        "Figure 3. Each dot is one state (or DC). States further right have higher "
        "obesity; states higher up have higher diabetes. The line is the regression "
        "line. No state breaks the pattern strongly &mdash; the relationship is "
        "fairly steady across the whole range.", small),
]))
story.append(Paragraph("Methods, in plain English", h2))
story.append(Paragraph(
    "Data come from the CDC U.S. Chronic Disease Indicators (CDI) on "
    "data.cdc.gov, dataset hksd-2xuw, downloaded 24 November 2026. Both "
    "measures are age-adjusted prevalence for 2023, for all adults, from the "
    "Behavioral Risk Factor Surveillance System (BRFSS), a telephone survey. "
    "Diabetes means adults who said a doctor had ever told them they have "
    "diabetes (not counting gestational diabetes only). Obesity means BMI "
    "of 30 or more, from self-reported height and weight. The analysis "
    "covers 49 jurisdictions: the 50 states plus DC, minus Kentucky and "
    "Pennsylvania, for which CDI reports &lsquo;No data available&rsquo; "
    "for both measures in 2023. The US national row and the territories "
    "(Guam, Puerto Rico, Virgin Islands) are in the data file but are not "
    "in the main analysis. The same steps were run in R (base R, "
    "<i>analysis.R</i>) and in Python (pandas/scipy, <i>analysis.py</i>) "
    "and gave identical results.", body))
story.append(Paragraph("Limitations", h2))
story.append(Paragraph(
    "&bull; <b>Ecological:</b> these are state averages. A state-level "
    "association does not prove the same link holds for individuals "
    "(ecological fallacy).", bul))
story.append(Paragraph(
    "&bull; <b>Cross-sectional, one year:</b> 2023 only. Nothing here shows "
    "change over time, or which came first.", bul))
story.append(Paragraph(
    "&bull; <b>Self-reported:</b> both measures come from people reporting "
    "their own diagnosis, height and weight. Height and weight are often "
    "misreported, and some diabetes is undiagnosed.", bul))
story.append(Paragraph(
    "&bull; <b>No adjustment:</b> the regression does not control for age "
    "structure beyond age-adjustment, income, race/ethnicity, health care, "
    "diet or physical activity, which differ across states and could "
    "explain part of the association. Two states are missing entirely, so "
    "the picture is incomplete.", bul))
story.append(Paragraph(
    "Source: Centers for Disease Control and Prevention, U.S. Chronic Disease "
    "Indicators, https://data.cdc.gov/resource/hksd-2xuw.csv (dataset "
    "hksd-2xuw). Full data, code and results: "
    "data/diabetes_obesity_by_state_tidy.csv, analysis.R, analysis.py, "
    "results.md.", small))
doc.build(story)
print("Wrote output/diabetes-obesity-by-state-brief.pdf")
