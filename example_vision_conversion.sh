#!/bin/bash
# Example script demonstrating vision-based diagram conversion
# This converts a Lucidchart PNG export to C4 draw.io format

set -e  # Exit on error

echo "=========================================="
echo "Vision-Based Diagram Conversion Example"
echo "=========================================="
echo ""

# Check if copilot-api is running
if ! curl -s http://localhost:4141/v1/models > /dev/null 2>&1; then
    echo "❌ Error: copilot-api is not running on port 4141"
    echo ""
    echo "Please start copilot-api first:"
    echo "  npx copilot-api@latest start"
    echo ""
    echo "Or if using direct Anthropic API, set ANTHROPIC_API_KEY instead."
    exit 1
fi

echo "✓ copilot-api is running"
echo ""

# Set environment variables for copilot-api
export ANTHROPIC_BASE_URL=http://localhost:4141
export ANTHROPIC_API_KEY=dummy

# Check if example image exists
EXAMPLE_IMAGE="$1"
if [ -z "$EXAMPLE_IMAGE" ]; then
    echo "Usage: $0 <path_to_diagram_image.png>"
    echo ""
    echo "Example:"
    echo "  $0 lucidchart_export.png"
    exit 1
fi

if [ ! -f "$EXAMPLE_IMAGE" ]; then
    echo "❌ Error: Image file not found: $EXAMPLE_IMAGE"
    exit 1
fi

echo "Converting: $EXAMPLE_IMAGE"
echo ""

# Convert the image
OUTPUT_FILE="c4_$(basename "$EXAMPLE_IMAGE" .png).drawio"

python main.py "$EXAMPLE_IMAGE" \
    -o "$OUTPUT_FILE" \
    --from-image \
    --save-intermediate \
    --verbose

echo ""
echo "=========================================="
echo "✓ Conversion Complete!"
echo "=========================================="
echo ""
echo "Output file: $OUTPUT_FILE"
echo "Intermediate file: ${OUTPUT_FILE%.drawio}_intermediate.drawio"
echo ""
echo "Next steps:"
echo "  1. Open $OUTPUT_FILE in draw.io"
echo "  2. Review and adjust the C4 diagram"
echo "  3. Update descriptions and labels as needed"
echo ""
