param(
    [string]$TargetSymbol = ""
)

$fileMapping = @{
    "NQ" = "NQ-USD"
    "ES" = "ES-USD"
    "BTC" = "BTC-USD"
    "CL" = "CL-USD"
    "GC" = "GC-USD"
    "YM" = "YM-USD"
    "ZN" = "ZN-USD"
    "6E" = "6E-USD"
}

$dataDir = "c:\NQData"
$files = Get-ChildItem -Path $dataDir -Filter "*.csv" | Sort-Object Name

# Filter if specific symbol requested
if ($TargetSymbol -ne "") {
    $files = $files | Where-Object { $_.Name -like "$TargetSymbol*" }
}

$total = $files.Count
$idx = 0

Write-Host "Starting batch ingestion of $total files..."

foreach ($f in $files) {
    $idx++
    $fileName = $f.Name
    $filePath = $f.FullName

    # Determine symbol
    $symbolKey = $null
    foreach ($k in $fileMapping.Keys) {
        if ($fileName.StartsWith($k + "_")) {
            $symbolKey = $k
            break
        }
    }

    if (-not $symbolKey) {
        Write-Host "[$idx/$total] Skipping unknown file: $fileName"
        continue
    }

    $symbol = $fileMapping[$symbolKey]
    
    # Skip already imported NQ 2024 and 2025
    if ($fileName -eq "NQ_1min_ON_2024.csv" -or $fileName -eq "NQ_1min_ON_2025.csv") {
        Write-Host "[$idx/$total] Already imported: $fileName -> $symbol"
        continue
    }

    Write-Host "[$idx/$total] Ingesting $fileName into $symbol..."
    cmd /c "type `"$filePath`" | docker exec -i jesse python /home/research_scripts/stream_ingest.py $symbol"
}

Write-Host "Batch ingestion completed!"
