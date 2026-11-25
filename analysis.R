# Diabetes and obesity by state, United States, 2023 — R analysis.
#
# Data: CDC U.S. Chronic Disease Indicators (CDI), dataset hksd-2xuw,
#   downloaded 2026-11-24 from data.cdc.gov (BRFSS as the underlying source).
#   Tidy file: data/diabetes_obesity_by_state_tidy.csv
#   (made by data/make_tidy.py from the raw CDI download).
# Measures: age-adjusted prevalence (%) among adults aged >= 18, Overall.
#   Diabetes: ever told by a doctor they have diabetes (excluding gestational).
#   Obesity: BMI >= 30, from self-reported height and weight.
# Analytic sample: 50 states + District of Columbia with both measures
#   present, n = 49. Kentucky and Pennsylvania have "No data available"
#   for both measures in 2023 in CDI and are excluded. The "United States"
#   national row and the territories (Guam, Puerto Rico, Virgin Islands)
#   are in the tidy file but excluded from the main analysis.
#
# Run: Rscript analysis.R   (from the project folder)
# Base R only — no extra packages needed.
# Writes: output/summary_statistics_r.csv, output/top_bottom_states_r.csv
#         and prints the results to the console.
# This is an ecological, cross-sectional analysis of state-level
# prevalence. It describes association only — it cannot show that
# obesity causes diabetes, or that one state's obesity level causes
# its diabetes level.

df <- read.csv("data/diabetes_obesity_by_state_tidy.csv",
               stringsAsFactors = FALSE)
# The tidy CSV stores TRUE/FALSE as the text "True"/"False", which
# read.csv reads as character, not logical — so compare to "True".
an <- df[df$included_in_analysis == "True", ]
an <- an[!is.na(an$diabetes_pct) & !is.na(an$obesity_pct), ]
n <- nrow(an)
cat(sprintf("States + DC included in analysis: n = %d\n", n))
excluded <- df$state[df$is_state_or_dc == "True" & df$included_in_analysis == "False"]
cat("States + DC excluded (no data):", paste(excluded, collapse = ", "), "\n")

describe <- function(x) {
  c(mean = mean(x), median = median(x), sd = sd(x),
    min = min(x), max = max(x))
}
d_d <- describe(an$diabetes_pct)
d_o <- describe(an$obesity_pct)
cat("\nDIABETES prevalence (age-adjusted %, adults 18+), 2023\n")
cat(sprintf("  mean %.2f  median %.2f  SD %.2f  range %.1f to %.1f\n",
            d_d["mean"], d_d["median"], d_d["sd"], d_d["min"], d_d["max"]))
cat("OBESITY prevalence (age-adjusted %, adults 18+), 2023\n")
cat(sprintf("  mean %.2f  median %.2f  SD %.2f  range %.1f to %.1f\n",
            d_o["mean"], d_o["median"], d_o["sd"], d_o["min"], d_o["max"]))

show_top_bottom <- function(col, label) {
  ord_desc <- order(-an[[col]])
  ord_asc <- order(an[[col]])
  cat(sprintf("\nTop 5 %s prevalence:\n", label))
  for (i in ord_desc[1:5]) {
    cat(sprintf("  %s: %.1f%%\n", an$state[i], an[[col]][i]))
  }
  cat(sprintf("Bottom 5 %s prevalence:\n", label))
  for (i in ord_asc[1:5]) {
    cat(sprintf("  %s: %.1f%%\n", an$state[i], an[[col]][i]))
  }
  cat(sprintf("Texas %s: %.1f%%\n", label, an[[col]][an$state == "Texas"]))
}
show_top_bottom("diabetes_pct", "Diabetes")
show_top_bottom("obesity_pct", "Obesity")

# --- Correlation (Pearson), cor.test gives r, p-value and Fisher z 95% CI ---
ct <- cor.test(an$obesity_pct, an$diabetes_pct, method = "pearson")
cat("\nCORRELATION between obesity and diabetes prevalence across states:\n")
cat(sprintf("  Pearson r = %.3f  (95%% CI %.3f to %.3f),  p = %.4g\n",
            ct$estimate, ct$conf.int[1], ct$conf.int[2], ct$p.value))

# --- Simple linear regression: diabetes ~ obesity ---
fit <- lm(diabetes_pct ~ obesity_pct, data = an)
s <- summary(fit)
cat("\nLINEAR REGRESSION: diabetes prevalence = intercept + slope x obesity prevalence\n")
cat(sprintf("  intercept = %.3f\n", coef(fit)[1]))
cat(sprintf("  slope = %.3f percentage points of diabetes per 1 percentage point of obesity\n",
            coef(fit)[2]))
cat(sprintf("  R-squared = %.3f\n", s$r.squared))
cat(sprintf("  slope p-value = %.4g\n", coef(s)[2, 4]))
ci <- confint(fit, "obesity_pct", level = 0.95)
cat(sprintf("  slope 95%% CI = %.3f to %.3f\n", ci[1], ci[2]))

cat("\nINTERPRETATION (plain English):\n")
cat("  States with higher obesity prevalence tend to have higher diabetes\n")
cat("  prevalence, and the association is strong and positive. This is an\n")
cat("  association between state-level averages, not proof that obesity\n")
cat("  causes diabetes in individuals, and not proof that changing a\n")
cat("  state's obesity level would change its diabetes level by the\n")
cat("  regression slope. Other state differences (age, income, health\n")
cat("  care, diet, physical activity) could explain part of the pattern.\n")

# --- Save summary tables ---
summary_df <- data.frame(
  measure = c("diabetes_pct", "obesity_pct"),
  n = n,
  mean = round(c(d_d["mean"], d_o["mean"]), 2),
  median = round(c(d_d["median"], d_o["median"]), 2),
  sd = round(c(d_d["sd"], d_o["sd"]), 2),
  min = round(c(d_d["min"], d_o["min"]), 2),
  max = round(c(d_d["max"], d_o["max"]), 2)
)
write.csv(summary_df, "output/summary_statistics_r.csv", row.names = FALSE)
model_df <- data.frame(
  analysis = c("pearson_r_obesity_diabetes", "regression_diabetes_on_obesity"),
  n = n,
  estimate = round(c(ct$estimate, coef(fit)[2]), 3),
  ci_low = round(c(ct$conf.int[1], ci[1]), 3),
  ci_high = round(c(ct$conf.int[2], ci[2]), 3),
  p_value = c(ct$p.value, coef(s)[2, 4]),
  extra = c("", sprintf("intercept=%.3f; R-squared=%.3f", coef(fit)[1], s$r.squared))
)
write.csv(model_df, "output/model_results_r.csv", row.names = FALSE)

top_bottom <- function(col) {
  top <- an[order(-an[[col]]), ][1:5, c("state", col)]
  bot <- an[order(an[[col]]), ][1:5, c("state", col)]
  data.frame(
    measure = col,
    rank = c(paste0("top_", 1:5), paste0("bottom_", 1:5)),
    state = c(top$state, bot$state),
    value_pct = c(top[[col]], bot[[col]])
  )
}
tb <- rbind(top_bottom("diabetes_pct"), top_bottom("obesity_pct"))
write.csv(tb, "output/top_bottom_states_r.csv", row.names = FALSE)
cat("\nWrote output/summary_statistics_r.csv, output/model_results_r.csv and output/top_bottom_states_r.csv\n")
