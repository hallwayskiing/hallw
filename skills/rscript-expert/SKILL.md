---
name: rscript-expert
description: Expert guidance for R programming and medical data visualization. Use when creating R scripts for data analysis, statistical modeling, or drawing medical charts (Kaplan-Meier, Forest plots, ROC curves, Nomograms).
---

# RScript Expert

This skill provides expert guidance on R programming, specifically tailored for data analysis and medical research visualization.

## Core R Programming

### Basic Syntax & Data Structures
- **Atomic Vectors**: `logical`, `integer`, `double`, `character`. Created via `c()`.
- **Lists**: `list()`, can hold different types.
- **Data Frames & Tibbles**: `data.frame()`, `tibble::tibble()`.
- **Missing Values**: Represented as `NA`. Check with `is.na()`.
- **Pipes**: Use `|>` (native) or `%>%` (magrittr) for cleaner code.

### Control Flow & Functions
- **Conditionals**: `if (cond) { ... } else { ... }`.
- **Loops**: `for (i in seq_along(x)) { ... }`.
- **Vectorized Functions**: `ifelse(test, yes, no)`, `lapply()`, `sapply()`.
- **Defining Functions**: `my_func <- function(arg1, arg2) { return(result) }`.

### Tidyverse Essentials
- **dplyr**: `filter()`, `select()`, `mutate()`, `group_by()`, `summarize()`.
- **tidyr**: `pivot_longer()`, `pivot_wider()`.
- **ggplot2**: Layered grammar of graphics (`ggplot() + geom_*()`).

## Medical Data Visualization

For detailed drawing methods of specific medical charts, refer to:
- [Medical Charts Reference](references/medical-charts.md)

### Supported Charts
- **Survival Analysis**: Kaplan-Meier plots (`survminer`).
- **Regression Results**: Forest plots for OR/HR (`forestplot`).
- **Model Evaluation**: ROC curves (`pROC`), Nomograms (`rms`).
- **Clinical Utility**: Decision Curve Analysis (DCA).

## Execution and Interaction

To execute R code effectively in this environment, refer to:
- [Execution Guide](references/execution.md)

### Quick Tips
- **Suppression**: Use `options(warn=-1)` to hide warnings.
- **Path**: Use absolute paths for `Rscript` if not in PATH.
- **Output**: Print results to stdout to ensure the agent can read them.

## Workflow Guidelines

1. **Environment Setup**: Load necessary libraries (`library()`).
2. **Data Preparation**: Clean and format data using tidyverse.
3. **Statistical Analysis**: Run survival models (`survdiff`, `coxph`) or regressions.
4. **Visualization**: Use high-quality plotting packages for publication-ready figures.
5. **Output**: Save plots using `ggsave()` with appropriate resolution (DPI).
