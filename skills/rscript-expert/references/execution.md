# R Execution Guide

This document provides guidelines for executing R code and interacting with the R environment using system tools.

## 1. Execution Mode

Since tool execution is typically non-interactive (call and wait), follow these patterns:

### Single Command Execution
Use `Rscript -e "code"` for quick calculations or simple tasks.
```powershell
Rscript -e "options(warn=-1); data <- c(1, 2, 3); print(mean(data))"
```

### Script-Based Execution
For complex workflows, write code to a `.R` file first, then execute it.
1. Write to `workspace/script.R`.
2. Execute: `Rscript workspace/script.R`.

## 2. Environment Path (Windows)

Rscript may not be in the system PATH. If execution fails:
- Search for the R installation path (e.g., `C:\Program Files\R\R-x.x.x\bin\x64\Rscript.exe`).
- Use the absolute path to call Rscript.

## 3. Data Exchange and Output

To ensure the AI agent can read results:
- **Use stdout**: Always use `print()`, `cat()`, or `message()` to output final results.
- **Suppress Noise**: Use `options(warn=-1)` at the start of scripts to prevent warnings from cluttering the output.
- **Structured Data**: For large outputs, save to CSV or JSON and read the file in a subsequent step.

## 4. Best Practices for AI Interaction

- **Clean Workspace**: Use `rm(list = ls())` at the start if you are running a standalone script to ensure reproducibility.
- **Library Checks**: Check if packages are installed before loading: `if (!require('pkg')) install.packages('pkg')`.
- **Error Handling**: Use `tryCatch()` for fragile operations to provide informative error messages.
