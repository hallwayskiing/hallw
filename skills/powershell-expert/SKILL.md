---
name: powershell-expert
description: Advanced PowerShell automation for complex workflows, including parallel processing, .NET interop, high-performance file operations, and Microsoft Office automation (Excel & Word). Use when needing efficient, scalable, or non-obvious PowerShell solutions.
---

# PowerShell Expert

This skill provides advanced workflows and tricky patterns for PowerShell automation.

## Core Workflows

### 1. High-Performance Parallel Processing
Use `ForEach-Object -Parallel` in PowerShell 7+ for I/O bound or CPU-intensive tasks. This is significantly faster than sequential processing for network or disk operations.

```powershell
# Efficiently processing files in parallel
Get-ChildItem -Path "C:\Logs" -Filter "*.log" | ForEach-Object -Parallel {
    $content = Get-Content $_.FullName
    if ($content -match "ERROR") {
        [PSCustomObject]@{
            File = $_.Name
            Timestamp = (Get-Item $_.FullName).LastWriteTime
        }
    }
} -ThrottleLimit 10
```

### 2. Tricky Pipeline Techniques
Use `ValueFromPipelineByPropertyName` to create flexible functions that accept objects from various sources without manual mapping.

```powershell
function Set-LogStatus {
    param(
        [Parameter(ValueFromPipelineByPropertyName)]
        [string]$Path,

        [Parameter(ValueFromPipelineByPropertyName)]
        [string]$Status
    )
    process {
        Add-Content -Path $Path -Value "$(Get-Date): $Status"
    }
}

# Example usage with custom objects mapping automatically
[PSCustomObject]@{ Path = "C:\temp\log.txt"; Status = "Success" } | Set-LogStatus
```

### 3. .NET and COM Interop
Directly accessing .NET classes for performance or functionality not exposed by cmdlets.

```powershell
# Fast file reading using .NET
[System.IO.File]::ReadAllLines("C:\largefile.txt")

# GUID Generation
[System.Guid]::NewGuid()
```

### 4. Microsoft Office Automation
For automating Excel and Word, creating reports, and document generation, see the specialized guide:
- [Office Automation Reference](references/office-automation.md)

## Expert Patterns

### Efficient Large Dataset Handling
**Avoid `+=` with arrays**, which creates a new copy of the array every time. Instead, use `System.Collections.Generic.List[object]` or `StringBuilder` for strings.

```powershell
$list = [System.Collections.Generic.List[object]]::new()
1..10000 | ForEach-Object { $list.Add($_) }
```

### Advanced Error Handling
Use `Try/Catch` with `$_` and custom error records for robust automation.

```powershell
try {
    Stop-Service "NonExistentService" -ErrorAction Stop
} catch {
    Write-Error "Failed to stop service: $($_.Exception.Message)"
}
```

## Tricky One-Liners

- **Recursive Search & Replace**:
  `Get-ChildItem -Recurse -Filter "*.txt" | ForEach-Object { (Get-Content $_.FullName) -replace 'old','new' | Set-Content $_.FullName }`
- **Memory Usage Check**:
  `Get-Process | Sort-Object WorkingSet64 -Descending | Select-Object Name, @{N='Memory(MB)';E={$_.WorkingSet64 / 1MB}} -First 10`

## Performance Tips
- Use `Select-String` instead of `Get-Content | Where-Object` for searching large files.
- Prefer `Get-ChildItem -Filter` over `Where-Object` for filesystem searches.
- Use `$null = ...` to suppress output for better performance in loops.
