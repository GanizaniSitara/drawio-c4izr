"""Convert draw.io diagrams into a consistent C4 representation.

The conversion rewrites every vertex as a C4 `object` with `c4Name`, `c4Type` and
`c4Description`, gives it a standard box size and colour, and distinguishes the main
system from its external dependencies. Edges become C4 relationships.

Two things are worth knowing before changing this module:

- The main system is identified by element **id**, never by label. Comparing labels
  meant two boxes sharing a name were both styled as the main system; the old code
  warned about that instead of fixing it.
- Nothing here installs a logging handler. The class used to attach a StreamHandler in
  its constructor, so every extra instance multiplied every log line. Handlers belong to
  the application; `main.py` sets one up.
"""

from __future__ import annotations

import logging
import uuid
import xml.dom.minidom
import xml.etree.ElementTree as ET
from collections.abc import Callable, Sequence

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Standard C4 box, in draw.io units. Uniform sizing is the point of the tool, so this is
# deliberately not affected by the spread factor.
C4_BOX_WIDTH = 240
C4_BOX_HEIGHT = 120

_POINTS = (
    "points=[[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0.25,0],[1,0.5,0],[1,0.75,0],"
    "[0.75,1,0],[0.5,1,0],[0.25,1,0],[0,0.75,0],[0,0.5,0],[0,0.25,0]];"
)
_BOX_STYLE = (
    "rounded=1;whiteSpace=wrap;html=1;labelBackgroundColor=none;fillColor={fill};"
    "fontColor=#ffffff;align=center;arcSize=10;strokeColor={stroke};metaEdit=1;"
    "resizable=0;" + _POINTS
)
MAIN_SYSTEM_STYLE = _BOX_STYLE.format(fill="#1061B0", stroke="#0D5091")
EXTERNAL_SYSTEM_STYLE = _BOX_STYLE.format(fill="#8C8496", stroke="#736782")

RELATIONSHIP_STYLE = (
    "endArrow=blockThin;html=1;fontSize=10;fontColor=#404040;strokeWidth=1;endFill=1;"
    "strokeColor=#828282;elbow=vertical;metaEdit=1;endSize=14;startSize=14;jumpStyle=arc;"
    "jumpSize=16;rounded=0;edgeStyle=orthogonalEdgeStyle;"
)

VERTEX_LABEL = (
    '<font style="font-size: 16px"><b>%c4Name%</b></font>'
    "<div>[%c4Type%]</div><br>"
    '<div><font style="font-size: 11px">'
    '<font color="#cccccc">%c4Description%</font></div>'
)
EDGE_LABEL = (
    '<div style="text-align: left">'
    '<div style="text-align: center"><b>%c4Description%</b></div>'
    '<div style="text-align: center">[%c4Technology%]</div></div>'
)

# A candidate main system, as offered to a selector: (element id, label).
Candidate = tuple[str, str]
Selector = Callable[[Sequence[Candidate]], str]


def first_candidate(candidates: Sequence[Candidate]) -> str:
    """Default selector: take the first vertex found, without prompting."""
    return candidates[0][0]


class c4izr:
    """Rewrites a draw.io diagram into a uniform C4 representation."""

    def __init__(
        self,
        scaling_factor: float = 1.4,
        selector: Selector | None = None,
    ) -> None:
        """
        Args:
            scaling_factor: how far apart to push elements, relative to the diagram
                centre. It scales SPACING, not element size - boxes are always
                C4_BOX_WIDTH x C4_BOX_HEIGHT.
            selector: given the candidate systems as (id, label) pairs, returns the id of
                the main one. Defaults to taking the first, non-interactively. main.py
                passes a console prompt.
        """
        self.scaling_factor = scaling_factor
        self.selector: Selector = selector or first_candidate
        self.logger = logger

    @property
    def interactive(self) -> bool:
        """Deprecated. True when a selector other than the default is in use.

        Kept so existing callers doing `translator.interactive = False` still work.
        """
        return self.selector is not first_candidate

    @interactive.setter
    def interactive(self, value: bool) -> None:
        if not value:
            self.selector = first_candidate

    def translate(self, input_xml: str) -> str:
        """Translate one draw.io XML string into C4 form.

        Raises:
            ValueError: if the input is not parseable XML.
        """
        try:
            input_root = ET.fromstring(input_xml)
        except ET.ParseError as exc:
            self.logger.error(f"Failed to parse input XML: {exc}")
            raise ValueError(f"Invalid XML format: {exc}") from exc

        output_root = ET.Element("mxGraphModel", input_root.attrib)
        new_root = ET.SubElement(output_root, "root")
        # Attributes as an explicit dict: passing parent="0" as a keyword shadows
        # SubElement's own `parent` parameter, which reads as a bug even though the C
        # accelerator happens to treat it as an attribute.
        ET.SubElement(new_root, "mxCell", {"id": "0"})
        ET.SubElement(new_root, "mxCell", {"id": "1", "parent": "0"})

        vertices = input_root.findall('.//mxCell[@vertex="1"]')
        if not vertices:
            self.logger.warning("No elements found in the diagram")
            return ET.tostring(output_root, encoding="unicode", method="xml")

        center_x, center_y = self._diagram_centre(vertices)
        main_system_id = self._choose_main_system(vertices, center_x, center_y)

        for mxcell in vertices:
            self._process_vertex(mxcell, new_root, main_system_id, center_x, center_y)

        for mxcell in input_root.findall('.//mxCell[@edge="1"]'):
            self._process_edge(mxcell, new_root)

        return ET.tostring(output_root, encoding="unicode", method="xml")

    def translate_multiple(self, input_xml_list: Sequence[str]) -> list[str]:
        """Translate several draw.io XML strings."""
        return [self.translate(input_xml) for input_xml in input_xml_list]

    def _diagram_centre(self, vertices: Sequence[ET.Element]) -> tuple[float, float]:
        """Bounding-box centre of every vertex that has usable geometry."""
        min_x = min_y = float("inf")
        max_x = max_y = float("-inf")

        for mxcell in vertices:
            mxgeometry = mxcell.find("mxGeometry")
            if mxgeometry is None:
                continue
            try:
                x = float(mxgeometry.get("x", 0))
                y = float(mxgeometry.get("y", 0))
                width = float(mxgeometry.get("width", 0))
                height = float(mxgeometry.get("height", 0))
            except (ValueError, TypeError) as exc:
                self.logger.warning(f"Invalid geometry value for element {mxcell.get('id')}: {exc}")
                continue
            min_x, min_y = min(min_x, x), min(min_y, y)
            max_x, max_y = max(max_x, x + width), max(max_y, y + height)

        if float("inf") in (min_x, min_y) or float("-inf") in (max_x, max_y):
            self.logger.warning("Could not determine diagram bounds, using defaults")
            min_x = min_y = 0.0
            max_x = max_y = 500.0

        return (min_x + max_x) / 2, (min_y + max_y) / 2

    def _choose_main_system(
        self,
        vertices: Sequence[ET.Element],
        center_x: float,
        center_y: float,
    ) -> str:
        """Ask the selector which vertex id is the main system."""
        candidates: list[Candidate] = [
            (mxcell.get("id") or str(uuid.uuid4()), mxcell.get("value", "")) for mxcell in vertices
        ]
        self.logger.debug(f"Centre of the diagram: ({center_x}, {center_y})")

        chosen = self.selector(candidates)
        known_ids = {candidate_id for candidate_id, _ in candidates}
        if chosen not in known_ids:
            self.logger.warning(f"Selector returned unknown id {chosen!r}; using the first element")
            chosen = candidates[0][0]

        label = next(label for candidate_id, label in candidates if candidate_id == chosen)
        self.logger.info(f"Main system: {label} (id {chosen})")
        return chosen

    def _process_vertex(
        self,
        mxcell: ET.Element,
        new_root: ET.Element,
        main_system_id: str,
        center_x: float,
        center_y: float,
    ) -> None:
        """Rewrite one vertex as a C4 object and append it to new_root."""
        try:
            element_id = mxcell.attrib.get("id") or str(uuid.uuid4())
            name = mxcell.get("value", "")

            object_elem = ET.SubElement(new_root, "object")
            object_elem.set("id", element_id)
            object_elem.set("placeholders", "1")
            object_elem.set("c4Name", name)
            object_elem.set("c4Type", "Software System")
            object_elem.set("c4Description", f"Description of {name.lower()}.")
            object_elem.set("label", VERTEX_LABEL)

            # Identity is the id, never the label: two boxes sharing a name must not both
            # come out styled as the main system.
            is_main = element_id == main_system_id
            object_mxcell = ET.SubElement(
                object_elem,
                "mxCell",
                {
                    "style": MAIN_SYSTEM_STYLE if is_main else EXTERNAL_SYSTEM_STYLE,
                    "vertex": "1",
                    "parent": "1",
                },
            )

            mxgeometry = mxcell.find("mxGeometry")
            if mxgeometry is not None:
                object_mxcell.append(self._scaled_geometry(mxgeometry, element_id, center_x, center_y))
        except Exception as exc:
            self.logger.error(f"Error processing vertex {mxcell.get('id')}: {exc}")

    def _scaled_geometry(
        self,
        mxgeometry: ET.Element,
        element_id: str,
        center_x: float,
        center_y: float,
    ) -> ET.Element:
        """Standard C4 box size, with position pushed out from the diagram centre."""
        new_geometry = ET.Element("mxGeometry")
        new_geometry.set("width", str(C4_BOX_WIDTH))
        new_geometry.set("height", str(C4_BOX_HEIGHT))

        for axis, centre in (("x", center_x), ("y", center_y)):
            raw = mxgeometry.get(axis)
            if raw is None:
                continue
            try:
                moved = centre + (float(raw) - centre) * self.scaling_factor
                new_geometry.set(axis, str(moved))
            except (ValueError, TypeError):
                new_geometry.set(axis, raw)
                self.logger.warning(f"Could not scale {axis} coordinate for element {element_id}")

        for attr, value in mxgeometry.attrib.items():
            if attr not in ("x", "y", "width", "height"):
                new_geometry.set(attr, value)

        return new_geometry

    def _process_edge(self, mxcell: ET.Element, new_root: ET.Element) -> None:
        """Rewrite one edge as a C4 relationship and append it to new_root."""
        try:
            if "source" not in mxcell.attrib or "target" not in mxcell.attrib:
                self.logger.warning(f"Floating edge (arrow) {mxcell.get('id')}")
                new_root.append(mxcell)
                return

            object_elem = ET.SubElement(new_root, "object")
            object_elem.set("id", mxcell.attrib.get("id") or str(uuid.uuid4()))
            object_elem.set("placeholders", "1")
            object_elem.set("c4Type", "Relationship")
            object_elem.set("c4Technology", "e.g. JSON/HTTP")
            object_elem.set("c4Description", mxcell.get("value") or "e.g. Makes API calls")
            object_elem.set("label", EDGE_LABEL)

            object_mxcell = ET.SubElement(
                object_elem,
                "mxCell",
                {
                    "style": RELATIONSHIP_STYLE,
                    "edge": "1",
                    "parent": "1",
                    "source": mxcell.get("source", ""),
                    "target": mxcell.get("target", ""),
                },
            )

            for mxgeometry in mxcell.findall("mxGeometry"):
                object_mxcell.append(mxgeometry)
        except Exception as exc:
            self.logger.error(f"Error processing edge {mxcell.get('id')}: {exc}")

    def pretty_print(self, xml_string: str) -> str:
        """Indent an XML string for reading. Returns it unchanged if it will not parse."""
        try:
            dom = xml.dom.minidom.parseString(xml_string)
        except Exception as exc:
            self.logger.error(f"Error formatting XML: {exc}")
            return xml_string
        lines = dom.toprettyxml(indent="  ").split("\n")
        return "\n".join(line for line in lines if line.strip() and not line.startswith("<?xml"))

    @staticmethod
    def filter_string(input_string: str) -> str:
        """Strip exit/entry point declarations out of a draw.io style string."""
        try:
            kept = [element for element in input_string.split(";") if not element.startswith(("exit", "entry"))]
            return ";".join(kept) + ";"
        except Exception as exc:
            logger.error(f"Error filtering string: {exc}")
            return input_string
