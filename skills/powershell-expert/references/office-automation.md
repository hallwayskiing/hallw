# Office Automation (Excel & Word)

This reference provides detailed workflows and patterns for automating Microsoft Office using COM objects.

## Excel Automation

### Basic: Create, Write, and Save
```powershell
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false # Keep it hidden for performance
$workbook = $excel.Workbooks.Add()
$sheet = $workbook.Worksheets.Item(1)
$sheet.Cells.Item(1,1) = "Service Name"
$sheet.Cells.Item(1,2) = "Status"

# Batch writing data
$services = Get-Service | Select-Object -First 10
$row = 2
foreach ($s in $services) {
    $sheet.Cells.Item($row, 1) = $s.Name
    $sheet.Cells.Item($row, 2) = $s.Status
    $row++
}

$workbook.SaveAs("C:\Temp\ServiceReport.xlsx")
$excel.Quit()
# Clean up COM objects to prevent ghost processes
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel)
```

### Reading from Excel
```powershell
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$workbook = $excel.Workbooks.Open("C:\Path\To\File.xlsx")
$sheet = $workbook.Worksheets.Item(1)

# Read specific cell (Value2 is generally faster and avoids formatting issues)
$value = $sheet.Cells.Item(1, 1).Value2

# Read the entire used range into a 2D array (extremely fast for large sheets)
$data = $sheet.UsedRange.Value2

# Iterate through data
for ($i = 1; $i -le $data.GetUpperBound(0); $i++) {
    $col1 = $data[$i, 1]
    $col2 = $data[$i, 2]
    # Process row...
}

$workbook.Close($false)
$excel.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($excel)
```

### Formatting and Charts
```powershell
# Formatting headers
$range = $sheet.Range("A1:B1")
$range.Font.Bold = $true
$range.Interior.ColorIndex = 15 # Gray
$range.Columns.AutoFit()

# Adding a Chart
$chartContainer = $workbook.Charts.Add()
$chartContainer.ChartType = 4 # xlLine
```

## Word Automation

### Basic: Create and Append Text
```powershell
$word = New-Object -ComObject Word.Application
$word.Visible = $true
$doc = $word.Documents.Add()
$selection = $word.Selection
$selection.Style = "Title"
$selection.TypeText("System Report")
$selection.TypeParagraph()
$selection.Style = "Normal"
$selection.TypeText("Generated on: $(Get-Date)")
```

### Search & Replace (Template Workflow)
```powershell
# Search and Replace logic for automated templates
function Search-Replace-Word {
    param($Document, $FindText, $ReplaceWith)
    $find = $Document.Content.Find
    $find.Execute($FindText, $false, $true, $false, $false, $false, $true, 1, $false, $ReplaceWith, 2)
}
# Usage: Search-Replace-Word -Document $doc -FindText "<<USER>>" -ReplaceWith $env:USERNAME
```

## Integrated Workflow: Multi-App Reporting
1. **Extract**: Get system logs/metrics using `Get-WinEvent`.
2. **Process**: Use **Excel** to pivot data or generate trend charts.
3. **Report**: Copy the Excel chart and paste it into a **Word** executive summary template.
4. **Distribute**: Export the Word doc as **PDF** via `$doc.ExportAsFixedFormat("C:\Temp\Final.pdf", 17)`.

## Critical Note: Cleanup
Always release COM objects to prevent `EXCEL.EXE` or `WINWORD.EXE` processes from hanging in the background:
```powershell
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($comObject)
[System.GC]::Collect()
[System.GC]::WaitForPendingFinalizers()
```
