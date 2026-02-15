#!/usr/bin/env python3
"""
Vision-based diagram parser using Anthropic's Claude Opus with vision capabilities.
Extracts structured diagram information from PNG/JPG images.
"""

import base64
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
import anthropic


class VisionDiagramParser:
    """Parse diagram images using Claude's vision capabilities."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize the vision parser.

        Args:
            api_key: Anthropic API key. If None, will use ANTHROPIC_API_KEY env var.
                    For copilot-api proxy, this can be any non-empty string (e.g., "dummy").
            base_url: Base URL for API. If None, will use ANTHROPIC_BASE_URL env var.
                     For copilot-api proxy: http://localhost:4141
                     For direct Anthropic API: leave as None (uses default)
        """
        self.base_url = base_url or os.environ.get("ANTHROPIC_BASE_URL")
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "dummy")

        # Create client with custom base URL if using copilot-api proxy
        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        self.client = anthropic.Anthropic(**client_kwargs)

    def parse_diagram(self, image_path: str, model: str = "claude-opus-4-5-20251101") -> Dict:
        """
        Parse a diagram image and extract structured information.

        Args:
            image_path: Path to the diagram image (PNG, JPG, etc.)
            model: Claude model to use (default: opus-4.5)

        Returns:
            Dictionary containing:
                - elements: List of boxes/shapes with labels and positions
                - connections: List of arrows/edges with labels
                - metadata: Additional diagram information
        """
        # Read and encode image
        image_data = self._encode_image(image_path)
        media_type = self._get_media_type(image_path)

        # Create the prompt for diagram analysis
        prompt = self._create_diagram_analysis_prompt()

        # Call Claude with vision
        message = self.client.messages.create(
            model=model,
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )

        # Extract JSON response
        response_text = message.content[0].text

        # Parse JSON from response (may be wrapped in markdown code blocks)
        diagram_data = self._extract_json(response_text)

        return diagram_data

    def _encode_image(self, image_path: str) -> str:
        """Encode image file to base64."""
        with open(image_path, "rb") as image_file:
            return base64.standard_b64encode(image_file.read()).decode("utf-8")

    def _get_media_type(self, image_path: str) -> str:
        """Determine media type from file extension."""
        ext = Path(image_path).suffix.lower()
        media_types = {
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        return media_types.get(ext, 'image/png')

    def _create_diagram_analysis_prompt(self) -> str:
        """Create the prompt for diagram analysis."""
        return """Analyze this architecture/system diagram and extract all elements in a structured format.

Please provide a JSON response with the following structure:

{
  "elements": [
    {
      "id": "unique_id",
      "type": "box|cylinder|person|cloud|database|other",
      "label": "element label/name",
      "description": "any additional text or description",
      "position": {"x": estimated_x, "y": estimated_y},
      "size": {"width": estimated_width, "height": estimated_height},
      "style_hints": "any visual styling cues (color, shape, icons, etc.)"
    }
  ],
  "connections": [
    {
      "id": "unique_id",
      "source": "source_element_id",
      "target": "target_element_id",
      "label": "connection label/description",
      "type": "arrow|bidirectional|dashed|other",
      "direction": "left-to-right|top-to-bottom|etc"
    }
  ],
  "metadata": {
    "diagram_type": "C4|UML|flowchart|network|other",
    "title": "diagram title if present",
    "layers": "description of any grouping/layers",
    "notes": "any other relevant information"
  }
}

Guidelines:
1. Assign each box/shape a unique ID (e.g., "elem_1", "elem_2")
2. Estimate positions relative to the diagram (0,0 is top-left)
3. Identify element types based on visual appearance:
   - Person icons/stick figures → "person"
   - Cylindrical shapes → "database" or "cylinder"
   - Cloud shapes → "cloud"
   - Regular rectangles → "box"
4. Extract ALL visible text labels
5. Identify all arrows/connections between elements
6. Note any grouping, boundaries, or swim lanes in metadata
7. Preserve the spatial layout as accurately as possible

Return ONLY the JSON, no additional text."""

    def _extract_json(self, text: str) -> Dict:
        """Extract JSON from response text (handles markdown code blocks)."""
        # Remove markdown code blocks if present
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]

        text = text.strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {text}")


def main():
    """Example usage of VisionDiagramParser."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python vision_diagram_parser.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]

    # Parse diagram
    parser = VisionDiagramParser()
    print(f"Analyzing diagram: {image_path}")

    result = parser.parse_diagram(image_path)

    # Pretty print results
    print("\n" + "="*80)
    print("DIAGRAM ANALYSIS RESULTS")
    print("="*80)
    print(json.dumps(result, indent=2))

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Elements found: {len(result.get('elements', []))}")
    print(f"Connections found: {len(result.get('connections', []))}")
    print(f"Diagram type: {result.get('metadata', {}).get('diagram_type', 'unknown')}")


if __name__ == "__main__":
    main()
