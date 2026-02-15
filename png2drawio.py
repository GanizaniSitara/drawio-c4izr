#!/usr/bin/env python3
"""
Convert structured diagram data (from vision analysis) to draw.io XML format.
"""

import xml.etree.ElementTree as ET
import uuid
from typing import Dict, List


class DiagramToDrawIO:
    """Convert structured diagram data to draw.io XML."""

    def __init__(self, canvas_width: int = 1600, canvas_height: int = 1200):
        """
        Initialize the converter.

        Args:
            canvas_width: Width of the draw.io canvas
            canvas_height: Height of the draw.io canvas
        """
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

    def convert(self, diagram_data: Dict) -> str:
        """
        Convert structured diagram data to draw.io XML.

        Args:
            diagram_data: Dictionary with 'elements' and 'connections' keys

        Returns:
            XML string in draw.io format
        """
        # Create root mxGraphModel
        root = ET.Element("mxGraphModel", {
            "dx": "1418",
            "dy": "948",
            "grid": "1",
            "gridSize": "10",
            "guides": "1",
            "tooltips": "1",
            "connect": "1",
            "arrows": "1",
            "fold": "1",
            "page": "1",
            "pageScale": "1",
            "pageWidth": str(self.canvas_width),
            "pageHeight": str(self.canvas_height),
            "math": "0",
            "shadow": "0"
        })

        graph_root = ET.SubElement(root, "root")

        # Add required base cells
        ET.SubElement(graph_root, "mxCell", {"id": "0"})
        ET.SubElement(graph_root, "mxCell", {"id": "1", "parent": "0"})

        # Track element IDs for connections
        element_id_map = {}

        # Add all elements (boxes, shapes, etc.)
        elements = diagram_data.get("elements", [])
        for elem in elements:
            drawio_id = self._add_element(graph_root, elem)
            element_id_map[elem["id"]] = drawio_id

        # Add all connections (arrows, edges)
        connections = diagram_data.get("connections", [])
        for conn in connections:
            self._add_connection(graph_root, conn, element_id_map)

        return ET.tostring(root, encoding='unicode', method='xml')

    def _add_element(self, parent: ET.Element, element: Dict) -> str:
        """Add a diagram element (box, shape) to the XML."""
        elem_id = str(uuid.uuid4())
        elem_type = element.get("type", "box")
        label = element.get("label", "")
        description = element.get("description", "")

        # Combine label and description
        full_label = label
        if description and description != label:
            full_label = f"{label}\n{description}"

        # Get position and size
        pos = element.get("position", {})
        size = element.get("size", {})

        x = pos.get("x", 100)
        y = pos.get("y", 100)
        width = size.get("width", 120)
        height = size.get("height", 60)

        # Normalize positions (vision model might give relative values)
        x = self._normalize_coordinate(x, self.canvas_width)
        y = self._normalize_coordinate(y, self.canvas_height)

        # Choose style based on element type
        style = self._get_style_for_type(elem_type, element.get("style_hints", ""))

        # Create mxCell for the element
        mxcell = ET.SubElement(parent, "mxCell", {
            "id": elem_id,
            "value": full_label,
            "style": style,
            "vertex": "1",
            "parent": "1"
        })

        # Add geometry
        ET.SubElement(mxcell, "mxGeometry", {
            "x": str(x),
            "y": str(y),
            "width": str(width),
            "height": str(height),
            "as": "geometry"
        })

        return elem_id

    def _add_connection(self, parent: ET.Element, connection: Dict, id_map: Dict[str, str]) -> str:
        """Add a connection (arrow, edge) to the XML."""
        conn_id = str(uuid.uuid4())
        label = connection.get("label", "")
        conn_type = connection.get("type", "arrow")

        # Map source and target from vision IDs to draw.io IDs
        source_id = id_map.get(connection.get("source"))
        target_id = id_map.get(connection.get("target"))

        if not source_id or not target_id:
            # Skip connections with missing endpoints
            return conn_id

        # Choose style based on connection type
        style = self._get_connection_style(conn_type)

        # Create mxCell for the connection
        mxcell = ET.SubElement(parent, "mxCell", {
            "id": conn_id,
            "value": label,
            "style": style,
            "edge": "1",
            "parent": "1",
            "source": source_id,
            "target": target_id
        })

        # Add geometry
        ET.SubElement(mxcell, "mxGeometry", {
            "relative": "1",
            "as": "geometry"
        })

        return conn_id

    def _normalize_coordinate(self, value: float, max_value: int) -> float:
        """
        Normalize coordinate value.

        If value is between 0-1, treat as relative and scale to canvas.
        Otherwise, use as absolute pixel value.
        """
        if 0 <= value <= 1:
            # Relative position (0-1 range) → scale to canvas
            return value * max_value
        else:
            # Absolute pixel position
            return value

    def _get_style_for_type(self, elem_type: str, style_hints: str) -> str:
        """Get draw.io style string based on element type."""
        styles = {
            "box": "rounded=0;whiteSpace=wrap;html=1;",
            "person": "shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;outlineConnect=0;",
            "database": "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;",
            "cylinder": "shape=cylinder3;whiteSpace=wrap;html=1;boundedLbl=1;backgroundOutline=1;size=15;",
            "cloud": "ellipse;shape=cloud;whiteSpace=wrap;html=1;",
            "other": "rounded=1;whiteSpace=wrap;html=1;",
        }

        base_style = styles.get(elem_type, styles["box"])

        # Add color hints if mentioned in style_hints
        if "blue" in style_hints.lower():
            base_style += "fillColor=#dae8fc;strokeColor=#6c8ebf;"
        elif "green" in style_hints.lower():
            base_style += "fillColor=#d5e8d4;strokeColor=#82b366;"
        elif "red" in style_hints.lower():
            base_style += "fillColor=#f8cecc;strokeColor=#b85450;"
        elif "gray" in style_hints.lower() or "grey" in style_hints.lower():
            base_style += "fillColor=#f5f5f5;strokeColor=#666666;"

        return base_style

    def _get_connection_style(self, conn_type: str) -> str:
        """Get draw.io style string for connection type."""
        styles = {
            "arrow": "endArrow=classic;html=1;rounded=0;",
            "bidirectional": "endArrow=classic;startArrow=classic;html=1;rounded=0;",
            "dashed": "endArrow=classic;html=1;rounded=0;dashed=1;",
            "other": "endArrow=classic;html=1;rounded=0;",
        }
        return styles.get(conn_type, styles["arrow"])


def main():
    """Example usage."""
    import json
    import sys

    if len(sys.argv) < 2:
        print("Usage: python png2drawio.py <json_file>")
        print("  or: python png2drawio.py -  (read from stdin)")
        sys.exit(1)

    # Read JSON input
    if sys.argv[1] == "-":
        diagram_data = json.load(sys.stdin)
    else:
        with open(sys.argv[1], 'r') as f:
            diagram_data = json.load(f)

    # Convert to draw.io
    converter = DiagramToDrawIO()
    drawio_xml = converter.convert(diagram_data)

    # Output
    print(drawio_xml)


if __name__ == "__main__":
    main()
