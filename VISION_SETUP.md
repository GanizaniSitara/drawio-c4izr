# Vision-Based Diagram Conversion Setup

This guide explains how to set up the vision-based diagram conversion feature that converts PNG/JPG images (e.g., Lucidchart exports) to draw.io C4 diagrams.

## Overview

The workflow is:
```
Lucidchart/Any PNG → [Vision AI] → draw.io XML → [c4izr] → C4 draw.io
```

## Setup Options

You have two options for accessing vision AI capabilities:

### Option 1: Using copilot-api Proxy (Recommended for GitHub Copilot Users)

This option uses your existing GitHub Copilot subscription without additional API costs.

#### Prerequisites
- GitHub account with Copilot subscription (Individual, Business, or Enterprise)
- Node.js/Bun installed
- Python 3.8+

#### Step 1: Install copilot-api
```bash
# Using npx (easiest)
npx copilot-api@latest auth

# Or install globally
npm install -g copilot-api
```

#### Step 2: Authenticate with GitHub
```bash
npx copilot-api@latest auth
```
This will open your browser for GitHub OAuth authentication.

#### Step 3: Start the proxy server
```bash
# Start on default port 4141
npx copilot-api@latest start

# Or specify custom port
npx copilot-api@latest start --port 8080

# With rate limiting (recommended to avoid quota issues)
npx copilot-api@latest start --rate-limit 2
```

Keep this terminal window open while using the vision features.

#### Step 4: Configure environment variables
```bash
# Set the base URL to point to the copilot-api proxy
export ANTHROPIC_BASE_URL=http://localhost:4141

# API key can be anything (proxy handles auth via GitHub)
export ANTHROPIC_API_KEY=dummy
```

On Windows (PowerShell):
```powershell
$env:ANTHROPIC_BASE_URL="http://localhost:4141"
$env:ANTHROPIC_API_KEY="dummy"
```

On Windows (CMD):
```cmd
set ANTHROPIC_BASE_URL=http://localhost:4141
set ANTHROPIC_API_KEY=dummy
```

#### Step 5: Install Python dependencies
```bash
pip install -r requirements.txt
```

### Option 2: Direct Anthropic API (Paid)

Use this if you have your own Anthropic API key.

#### Step 1: Get API key
Sign up at https://console.anthropic.com and get your API key.

#### Step 2: Set environment variable
```bash
export ANTHROPIC_API_KEY=your_api_key_here
# Don't set ANTHROPIC_BASE_URL - use default
```

#### Step 3: Install Python dependencies
```bash
pip install -r requirements.txt
```

## Usage

Once set up, convert any diagram image to C4 format:

### Basic Usage
```bash
# Convert a Lucidchart PNG export to C4 draw.io
python main.py diagram.png -o output.drawio --from-image
```

### Advanced Options
```bash
# Verbose output to see what's detected
python main.py diagram.png -o output.drawio --from-image -v

# Save intermediate draw.io (before C4 conversion) for debugging
python main.py diagram.png -o output.drawio --from-image --save-intermediate

# Use a specific Claude model
python main.py diagram.png -o output.drawio --from-image --model claude-opus-4-5-20251101

# Non-interactive mode (auto-select first system as main)
python main.py diagram.png -o output.drawio --from-image --non-interactive

# Auto-open in draw.io after conversion
python main.py diagram.png -o output.drawio --from-image --open-output
```

### Supported Image Formats
- PNG (.png)
- JPEG (.jpg, .jpeg)
- GIF (.gif)
- WebP (.webp)

## How It Works

1. **Vision Analysis**: Claude analyzes the image and extracts:
   - All boxes/shapes with labels
   - All connections/arrows
   - Spatial layout and positioning
   - Visual hints (colors, shapes, icons)

2. **draw.io Generation**: Converts the extracted structure to valid draw.io XML format

3. **C4 Conversion**: Applies C4 styling and conventions using the existing c4izr logic

## Troubleshooting

### "Anthropic API key required" Error
**Solution**: Make sure environment variables are set:
```bash
# For copilot-api users
export ANTHROPIC_BASE_URL=http://localhost:4141
export ANTHROPIC_API_KEY=dummy

# For direct API users
export ANTHROPIC_API_KEY=your_real_key
```

### "Connection refused" Error
**Solution**: Make sure copilot-api proxy is running:
```bash
npx copilot-api@latest start
```

### "Rate limit exceeded" Error
**Solution**:
- For copilot-api: Add rate limiting when starting the proxy:
  ```bash
  npx copilot-api@latest start --rate-limit 2
  ```
- For direct API: Wait a few moments between requests

### Poor Detection Quality
**Solution**:
- Use higher quality images (avoid compression artifacts)
- Ensure text is readable in the image
- Try using `--save-intermediate` to see what was detected
- Use `-v` for verbose output to see element counts

### Vision Not Finding All Elements
**Solution**:
- Ensure diagram elements have clear boundaries
- Text labels should be clearly visible
- Try using `--model claude-opus-4-5-20251101` for best vision performance

## Rate Limits

### GitHub Copilot via copilot-api
- Free tier: ~15 requests per minute (varies by plan)
- Use `--rate-limit` flag to avoid hitting limits
- Consider `--wait` flag to queue requests instead of failing

### Direct Anthropic API
- Tier 1: 50 requests per minute
- Tier 2+: Higher limits based on usage
- See https://docs.anthropic.com/en/api/rate-limits

## Cost Considerations

### Using copilot-api (GitHub Copilot)
- **Cost**: Included in your GitHub Copilot subscription
- **Best for**: Occasional use, already have Copilot

### Direct Anthropic API
- **Cost**: ~$0.015 per image (using Claude Opus 4.5)
- **Best for**: High volume, automation, CI/CD pipelines

## Examples

### Convert Lucidchart Export
```bash
# Export your Lucidchart diagram as PNG
# Then convert to C4 draw.io
python main.py lucidchart_diagram.png -o c4_output.drawio --from-image -v
```

### Batch Processing (Future Enhancement)
Currently, vision mode processes single images. For batch processing, use a shell loop:
```bash
for img in diagrams/*.png; do
    python main.py "$img" -o "output/$(basename $img .png).drawio" --from-image --non-interactive
done
```

## Support

- For copilot-api issues: https://github.com/ericc-ch/copilot-api/issues
- For c4izr/drawio-c4izr issues: Create an issue in this repository
- For Anthropic API issues: https://support.anthropic.com

## Security Notes

⚠️ **Important**:
- The copilot-api proxy is an **unofficial** tool not endorsed by GitHub
- It may violate GitHub's Terms of Service - use at your own risk
- Your GitHub token provides access to your Copilot quota
- Don't share your GitHub token or API keys
- Tokens are stored locally in `~/.local/share/copilot-api`

## Advanced Configuration

### Running copilot-api as a Service

For production use, you might want to run copilot-api as a background service:

**Using PM2 (Node.js process manager):**
```bash
npm install -g pm2
pm2 start "npx copilot-api@latest start --rate-limit 2" --name copilot-api
pm2 save
pm2 startup
```

**Using Docker:**
```bash
docker run -d -p 4141:4141 --name copilot-api copilot-api
```

### Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | API key (or "dummy" for copilot-api) | `sk-ant-...` or `dummy` |
| `ANTHROPIC_BASE_URL` | Base URL for API endpoint | `http://localhost:4141` |

## Next Steps

After successful conversion:
1. Open the generated `.drawio` file in draw.io
2. Review the C4 diagram structure
3. Adjust descriptions, labels, and relationships as needed
4. Export to your preferred format (PNG, SVG, PDF)
