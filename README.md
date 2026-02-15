# drawio-c4izr

## Project Description

drawio-c4izr converts draw.io diagrams to common C4 representation and standardizes existing C4 diagrams into a unified C4 format. This tool has been enhanced with multiple new features including **vision-based image conversion**, interactive diagram element selection, improved logging, custom mapping configurations, and auto-backup of outputs.

## Current Features

- **🆕 Vision AI Integration**: Convert ANY diagram image (PNG/JPG) to C4 draw.io format
  - Works with Lucidchart exports, screenshots, hand-drawn diagrams
  - Uses Claude Opus vision via GitHub Copilot (copilot-api proxy) or direct Anthropic API
  - Automatically extracts boxes, connections, labels, and spatial layout
- Converts draw.io diagrams into standardized C4 representations
- Interactive selection of the main system when multiple diagram elements are present
- Processes both individual files and directories
- Modularized conversion logic with enhanced logging and error reporting
- Supports custom mapping configurations for C4 properties
- Auto-backup and versioning of output files
- Comprehensive test suites to validate conversion functionality

## Upcoming Features

- Web-based preview mode for interactive conversion
- Batch image processing capabilities
- Additional enhancements based on user feedback

## Installation

```bash
# Install Python dependencies
pip install -r requirements.txt
```

For **vision-based image conversion** setup (Lucidchart, PNG diagrams, etc.), see [VISION_SETUP.md](VISION_SETUP.md).

## How to Use

### Convert draw.io Files

Use drawio-c4izr by providing a single .drawio file or a directory containing multiple diagrams:

```cmd
# Convert a single draw.io file
python main.py path\to\diagram.drawio

# Convert all .drawio files in a directory
python main.py path\to\directory\
```

If you prefer non-interactive mode, specify the flag:

```cmd
python main.py path\to\diagram.drawio --non-interactive
```

You can also adjust scaling, logging, and output settings:

```cmd
python main.py path\to\diagram.drawio --scaling-factor=1.6 --verbose
```

### 🆕 Convert Image Files (PNG, JPG) to C4 Diagrams

Convert any diagram image (Lucidchart exports, screenshots, etc.) to C4 draw.io format:

```cmd
# Basic usage
python main.py diagram.png -o output.drawio --from-image

# With verbose output to see what's detected
python main.py diagram.png -o output.drawio --from-image -v

# Save intermediate draw.io (before C4 conversion) for debugging
python main.py diagram.png -o output.drawio --from-image --save-intermediate

# Auto-open in draw.io after conversion
python main.py diagram.png -o output.drawio --from-image --open-output
```

**Prerequisites for image conversion:**
- Set up copilot-api proxy (for GitHub Copilot users) OR Anthropic API key
- See detailed setup instructions in [VISION_SETUP.md](VISION_SETUP.md)

**Quick setup for GitHub Copilot users:**
```bash
# 1. Start copilot-api proxy
npx copilot-api@latest start

# 2. Set environment variables
export ANTHROPIC_BASE_URL=http://localhost:4141
export ANTHROPIC_API_KEY=dummy

# 3. Convert your image
python main.py lucidchart_export.png -o c4_diagram.drawio --from-image
```

---

## How Vision Conversion Works

When you use the `--from-image` flag, the conversion happens in three stages:

```
┌─────────────────┐
│  Input Image    │  (PNG/JPG from Lucidchart, screenshots, etc.)
│  (Lucidchart)   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│  Stage 1: Vision AI Analysis                            │
│  (vision_diagram_parser.py)                             │
│                                                          │
│  • Claude Opus vision model analyzes the image          │
│  • Extracts: boxes, labels, connections, positions      │
│  • Identifies: element types (person, database, box)    │
│  • Preserves: spatial layout and relationships          │
│  • Output: Structured JSON data                         │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │  Structured Data (JSON) │
         │  {                      │
         │    elements: [...],     │
         │    connections: [...]   │
         │  }                      │
         └────────┬───────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  Stage 2: draw.io XML Generation                        │
│  (png2drawio.py)                                        │
│                                                          │
│  • Converts JSON to draw.io mxGraphModel XML            │
│  • Maps positions to draw.io coordinates                │
│  • Applies appropriate shapes and styles                │
│  • Creates mxCell elements for boxes and arrows         │
│  • Output: Valid draw.io XML                            │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │  draw.io XML (generic)  │
         └────────┬───────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│  Stage 3: C4 Standardization                            │
│  (c4izr.py - existing converter)                        │
│                                                          │
│  • Applies C4 styling and conventions                   │
│  • Adds C4 metadata (c4Name, c4Type, c4Description)     │
│  • Distinguishes main system vs external systems        │
│  • Standardizes box sizes (240x120)                     │
│  • Applies C4 color scheme (blue/gray)                  │
│  • Formats labels with C4 template                      │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │  C4 draw.io Output      │
         │  Ready to edit!         │
         └─────────────────────────┘
```

### Key Components

- **vision_diagram_parser.py**: Interfaces with Claude Opus vision API (via copilot-api or direct)
- **png2drawio.py**: Transforms extracted structure into draw.io's XML format
- **c4izr.py**: Your existing converter that applies C4 standards
- **copilot-api**: Optional proxy that lets you use GitHub Copilot subscription instead of paying for Anthropic API

### Why This Approach?

1. **Leverages existing code**: Reuses your proven c4izr converter for C4 standardization
2. **Clean separation**: Vision extraction → Generic draw.io → C4 styling
3. **Debuggable**: Use `--save-intermediate` to see the draw.io XML before C4 conversion
4. **Cost-effective**: Works with GitHub Copilot subscription (via copilot-api proxy)
5. **Format agnostic**: Vision stage works with any diagram image format

For detailed setup instructions, see [VISION_SETUP.md](VISION_SETUP.md).
