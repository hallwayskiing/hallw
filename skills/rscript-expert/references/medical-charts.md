# Medical Charts Reference

This document provides code snippets and best practices for common medical charts in R.

## 1. Kaplan-Meier Plot
Used for survival analysis to estimate the survival function from lifetime data.
```r
library(survival)
library(survminer)

# Fit survival curve
fit <- survfit(Surv(time, status) ~ group, data = df)

# Plot
ggsurvplot(
  fit,
  data = df,
  pval = TRUE,
  conf.int = TRUE,
  risk.table = TRUE,
  palette = "jco",
  ggtheme = theme_bw()
)
```

## 2. Forest Plot
Used for Meta-analysis or displaying Hazard Ratios/Odds Ratios from regression models.
```r
library(forestplot)

# Structure your data with mean, lower, upper limits and table text
forestplot(
  labeltext = tabletext,
  mean = df$mean,
  lower = df$lower,
  upper = df$upper,
  new_page = TRUE,
  col = fpColors(box = "royalblue", line = "darkblue", summary = "royalblue")
)
```

## 3. ROC Curve
Used for evaluating the diagnostic performance of a binary classifier.
```r
library(pROC)
library(ggplot2)

roc_obj <- roc(df$status, df$prediction)
ggroc(roc_obj) +
  theme_minimal() +
  ggtitle("ROC Curve") +
  annotate("text", x = 0.5, y = 0.5, label = paste0("AUC = ", round(auc(roc_obj), 2)))
```

## 4. Nomogram
Used for visualizing predictive models (e.g., Logistic, Cox).
```r
library(rms)

# Set data distribution
dd <- datadist(df)
options(datadist = 'dd')

# Fit model
fit <- lrm(y ~ x1 + x2 + x3, data = df)

# Draw Nomogram
nom <- nomogram(fit, fun = plogis, lp = FALSE, funlabel = "Risk")
plot(nom)
```

## 5. Decision Curve Analysis (DCA)
Used to evaluate the clinical utility of models by assessing net benefit.
```r
library(dcurves)

dca(cancer ~ model1 + model2, data = df) %>%
  plot() +
  theme_bw()
```

## 6. Calibration Plot
Used to check how well the predicted probabilities match actual outcomes.
```r
library(rms)

# Fit model
fit <- lrm(y ~ x1 + x2, data = df, x = TRUE, y = TRUE)

# Calibrate
cal <- calibrate(fit, method = "boot", B = 1000)
plot(cal)
```
