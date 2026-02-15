# Example PowerShell script demonstrating vision-based diagram conversion
# This converts a Lucidchart PNG export to C4 draw.io format

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Vision-Based Diagram Conversion Example" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check if copilot-api is running
try {
    $null = Invoke-WebRequest -Uri "http://localhost:4141/v1/models" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✓ copilot-api is running" -ForegroundColor Green
}
catch {
    Write-Host "❌ Error: copilot-api is not running on port 4141" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please start copilot-api first:"
    Write-Host "  npx copilot-api@latest start"
    Write-Host ""
    Write-Host "Or if using direct Anthropic API, set ANTHROPIC_API_KEY instead."
    exit 1
}

Write-Host ""

# Set environment variables for copilot-api
$env:ANTHROPIC_BASE_URL = "http://localhost:4141"
$env:ANTHROPIC_API_KEY = "dummy"

# Check if example image exists
$ExampleImage = $args[0]
if (-not $ExampleImage) {
    Write-Host "Usage: .\example_vision_conversion.ps1 <path_to_diagram_image.png>"
    Write-Host ""
    Write-Host "Example:"
    Write-Host "  .\example_vision_conversion.ps1 lucidchart_export.png"
    exit 1
}

if (-not (Test-Path $ExampleImage)) {
    Write-Host "❌ Error: Image file not found: $ExampleImage" -ForegroundColor Red
    exit 1
}

Write-Host "Converting: $ExampleImage"
Write-Host ""

# Convert the image
$BaseName = [System.IO.Path]::GetFileNameWithoutExtension($ExampleImage)
$OutputFile = "c4_$BaseName.drawio"

python main.py $ExampleImage `
    -o $OutputFile `
    --from-image `
    --save-intermediate `
    --verbose

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "✓ Conversion Complete!" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Output file: $OutputFile"
Write-Host "Intermediate file: $($OutputFile -replace '.drawio$','_intermediate.drawio')"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Open $OutputFile in draw.io"
Write-Host "  2. Review and adjust the C4 diagram"
Write-Host "  3. Update descriptions and labels as needed"
Write-Host ""
