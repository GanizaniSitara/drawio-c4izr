"""Tests for the draw.io to C4 conversion.

Assertions parse the output as XML rather than substring-matching raw text, so a test
failure says which element is wrong rather than only that some string is absent.

Two of these are regression guards for bugs that shipped: duplicate element labels used
to make several boxes the main system, and constructing the translator used to attach
another logging handler each time.
"""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

import drawio_serialization
import drawio_utils
from c4izr import (
    C4_BOX_HEIGHT,
    C4_BOX_WIDTH,
    EXTERNAL_SYSTEM_STYLE,
    MAIN_SYSTEM_STYLE,
    c4izr,
    first_candidate,
)

HERE = Path(__file__).resolve().parent

TWO_SYSTEMS = """<mxGraphModel>
  <root>
    <mxCell id="0" />
    <mxCell id="1" parent="0" />
    <mxCell id="2" value="System A" style="rounded=0;whiteSpace=wrap;html=1;" parent="1" vertex="1">
      <mxGeometry x="260" y="170" width="120" height="60" as="geometry" />
    </mxCell>
    <mxCell id="3" value="System B" style="ellipse;whiteSpace=wrap;html=1;" parent="1" vertex="1">
      <mxGeometry x="600" y="160" width="80" height="80" as="geometry" />
    </mxCell>
    <mxCell id="4" style="edgeStyle=none;html=1;" edge="1" parent="1" source="2" target="3">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
  </root>
</mxGraphModel>"""


def vertex(cell_id: str, label: str, x: int = 0, y: int = 0) -> str:
    return (
        f'<mxCell id="{cell_id}" value="{label}" parent="1" vertex="1">'
        f'<mxGeometry x="{x}" y="{y}" width="120" height="60" as="geometry"/>'
        f"</mxCell>"
    )


def model(*cells: str) -> str:
    body = "".join(cells)
    return f'<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/>{body}</root></mxGraphModel>'


def objects(output_xml: str) -> list[ET.Element]:
    return ET.fromstring(output_xml).findall(".//object")


def styles(output_xml: str) -> list[str]:
    return [cell.get("style", "") for cell in ET.fromstring(output_xml).findall(".//object/mxCell")]


class TestMainSystemSelection:
    def test_duplicate_labels_yield_exactly_one_main_system(self) -> None:
        """Regression: identity is the element id, not the label.

        Two boxes sharing a name both used to come out styled as the main system,
        because the comparison was on `value`.
        """
        xml = model(
            vertex("2", "Payments", x=0),
            vertex("3", "Payments", x=400),
            vertex("4", "Ledger", x=800),
        )
        output = c4izr().translate(xml)
        applied = styles(output)
        assert applied.count(MAIN_SYSTEM_STYLE) == 1
        assert applied.count(EXTERNAL_SYSTEM_STYLE) == 2

    def test_default_selector_picks_the_first_vertex(self) -> None:
        xml = model(vertex("2", "First"), vertex("3", "Second"))
        output = c4izr().translate(xml)
        first, second = objects(output)[:2]
        assert first.get("c4Name") == "First"
        assert first.find("mxCell").get("style") == MAIN_SYSTEM_STYLE  # type: ignore[union-attr]
        assert second.find("mxCell").get("style") == EXTERNAL_SYSTEM_STYLE  # type: ignore[union-attr]

    def test_selector_receives_id_label_pairs_in_diagram_order(self) -> None:
        seen: list[tuple[str, str]] = []

        def record(candidates):  # type: ignore[no-untyped-def]
            seen.extend(candidates)
            return candidates[0][0]

        c4izr(selector=record).translate(model(vertex("2", "Alpha"), vertex("3", "Beta")))
        assert seen == [("2", "Alpha"), ("3", "Beta")]

    def test_selector_can_choose_a_later_element(self) -> None:
        xml = model(vertex("2", "Alpha"), vertex("3", "Beta"))
        output = c4izr(selector=lambda candidates: "3").translate(xml)
        chosen = [o for o in objects(output) if o.find("mxCell").get("style") == MAIN_SYSTEM_STYLE]  # type: ignore[union-attr]
        assert [o.get("c4Name") for o in chosen] == ["Beta"]

    def test_unknown_id_from_selector_falls_back_to_first(self) -> None:
        xml = model(vertex("2", "Alpha"), vertex("3", "Beta"))
        output = c4izr(selector=lambda candidates: "does-not-exist").translate(xml)
        assert styles(output).count(MAIN_SYSTEM_STYLE) == 1
        assert objects(output)[0].get("c4Name") == "Alpha"

    def test_interactive_false_keeps_working_for_existing_callers(self) -> None:
        translator = c4izr()
        translator.interactive = False
        assert translator.selector is first_candidate
        assert translator.interactive is False


class TestLogging:
    def test_constructing_the_translator_adds_no_handlers(self) -> None:
        """Regression: __init__ used to attach a StreamHandler every time."""
        before = len(logging.getLogger("c4izr").handlers)
        for _ in range(5):
            c4izr()
        assert len(logging.getLogger("c4izr").handlers) == before


class TestConversionOutput:
    def test_every_vertex_becomes_a_c4_object(self) -> None:
        output = c4izr().translate(TWO_SYSTEMS)
        vertices = [o for o in objects(output) if o.get("c4Type") == "Software System"]
        assert [o.get("c4Name") for o in vertices] == ["System A", "System B"]
        for element in vertices:
            assert element.get("c4Description")
            assert element.get("placeholders") == "1"
            assert element.get("label")

    def test_element_ids_are_preserved(self) -> None:
        output = c4izr().translate(TWO_SYSTEMS)
        assert {o.get("id") for o in objects(output)} == {"2", "3", "4"}

    def test_root_cells_are_present(self) -> None:
        root = ET.fromstring(c4izr().translate(TWO_SYSTEMS)).find("root")
        assert root is not None
        ids = [cell.get("id") for cell in root.findall("mxCell")]
        assert ids[:2] == ["0", "1"]

    def test_edges_become_relationships_keeping_endpoints(self) -> None:
        output = c4izr().translate(TWO_SYSTEMS)
        edges = [o for o in objects(output) if o.get("c4Type") == "Relationship"]
        assert len(edges) == 1
        cell = edges[0].find("mxCell")
        assert cell is not None
        assert (cell.get("source"), cell.get("target")) == ("2", "3")
        assert cell.get("edge") == "1"

    def test_edge_label_becomes_the_description(self) -> None:
        xml = model(
            vertex("2", "A"),
            vertex("3", "B", x=400),
            '<mxCell id="4" value="Publishes events" edge="1" parent="1" source="2" target="3">'
            '<mxGeometry relative="1" as="geometry"/></mxCell>',
        )
        output = c4izr().translate(xml)
        edge = next(o for o in objects(output) if o.get("c4Type") == "Relationship")
        assert edge.get("c4Description") == "Publishes events"

    def test_unlabelled_edge_gets_a_placeholder_description(self) -> None:
        output = c4izr().translate(TWO_SYSTEMS)
        edge = next(o for o in objects(output) if o.get("c4Type") == "Relationship")
        assert edge.get("c4Description") == "e.g. Makes API calls"


class TestGeometry:
    @pytest.mark.parametrize("spread", [1.0, 1.4, 3.0])
    def test_box_size_is_uniform_regardless_of_spread(self, spread: float) -> None:
        """The spread factor moves elements; it never resizes them.

        The README used to describe it as scaling element sizes, which it has never done.
        """
        xml = model(vertex("2", "A", x=0, y=0), vertex("3", "B", x=400, y=200))
        output = c4izr(scaling_factor=spread).translate(xml)
        geometries = ET.fromstring(output).findall(".//object/mxCell/mxGeometry")
        assert len(geometries) == 2
        for geometry in geometries:
            assert geometry.get("width") == str(C4_BOX_WIDTH)
            assert geometry.get("height") == str(C4_BOX_HEIGHT)

    def test_larger_spread_pushes_elements_further_apart(self) -> None:
        xml = model(vertex("2", "A", x=0, y=0), vertex("3", "B", x=400, y=0))

        def x_positions(spread: float) -> list[float]:
            output = c4izr(scaling_factor=spread).translate(xml)
            return [float(g.get("x", 0)) for g in ET.fromstring(output).findall(".//object/mxCell/mxGeometry")]

        tight, wide = x_positions(1.0), x_positions(3.0)
        assert wide[1] - wide[0] > tight[1] - tight[0]

    def test_spread_of_one_leaves_positions_untouched(self) -> None:
        xml = model(vertex("2", "A", x=0, y=0), vertex("3", "B", x=400, y=200))
        output = c4izr(scaling_factor=1.0).translate(xml)
        geometries = ET.fromstring(output).findall(".//object/mxCell/mxGeometry")
        assert [(g.get("x"), g.get("y")) for g in geometries] == [("0.0", "0.0"), ("400.0", "200.0")]

    def test_non_numeric_geometry_is_carried_through_verbatim(self) -> None:
        xml = model(
            '<mxCell id="2" value="A" parent="1" vertex="1">'
            '<mxGeometry x="not-a-number" y="10" width="120" height="60" as="geometry"/>'
            "</mxCell>"
        )
        geometry = ET.fromstring(c4izr().translate(xml)).find(".//object/mxCell/mxGeometry")
        assert geometry is not None
        assert geometry.get("x") == "not-a-number"

    def test_geometry_attributes_other_than_position_and_size_survive(self) -> None:
        xml = model(
            '<mxCell id="2" value="A" parent="1" vertex="1">'
            '<mxGeometry x="0" y="0" width="120" height="60" as="geometry"/>'
            "</mxCell>"
        )
        geometry = ET.fromstring(c4izr().translate(xml)).find(".//object/mxCell/mxGeometry")
        assert geometry is not None
        assert geometry.get("as") == "geometry"


class TestEdgeCases:
    def test_diagram_with_no_vertices_returns_a_bare_model(self) -> None:
        output = c4izr().translate(model())
        assert objects(output) == []
        root = ET.fromstring(output).find("root")
        assert root is not None
        assert [cell.get("id") for cell in root.findall("mxCell")] == ["0", "1"]

    def test_floating_edge_is_kept_rather_than_dropped(self) -> None:
        """An edge with no source/target cannot become a relationship, but losing it
        silently would quietly change the diagram."""
        xml = model(
            vertex("2", "A"),
            '<mxCell id="9" edge="1" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>',
        )
        root = ET.fromstring(c4izr().translate(xml)).find("root")
        assert root is not None
        assert "9" in [cell.get("id") for cell in root.findall("mxCell")]

    def test_vertex_without_geometry_still_converts(self) -> None:
        xml = model('<mxCell id="2" value="A" parent="1" vertex="1"/>')
        converted = objects(c4izr().translate(xml))
        assert len(converted) == 1
        assert converted[0].find("mxCell/mxGeometry") is None

    def test_invalid_xml_raises_valueerror(self) -> None:
        with pytest.raises(ValueError, match="Invalid XML format"):
            c4izr().translate("<mxGraphModel><root>")

    def test_model_attributes_are_carried_to_the_output(self) -> None:
        xml = '<mxGraphModel grid="1" pageWidth="850"><root><mxCell id="0"/></root></mxGraphModel>'
        root = ET.fromstring(c4izr().translate(xml))
        assert root.get("grid") == "1"
        assert root.get("pageWidth") == "850"

    def test_translate_multiple_converts_each_input(self) -> None:
        outputs = c4izr().translate_multiple([TWO_SYSTEMS, model(vertex("2", "Solo"))])
        assert len(outputs) == 2
        assert objects(outputs[1])[0].get("c4Name") == "Solo"


class TestStyleFiltering:
    def test_exit_and_entry_declarations_are_stripped(self) -> None:
        filtered = c4izr.filter_string("rounded=1;exitX=0.5;entryY=0;html=1;")
        assert "exitX" not in filtered
        assert "entryY" not in filtered
        assert "rounded=1" in filtered
        assert "html=1" in filtered


class TestSerialisation:
    def test_encode_decode_round_trips(self) -> None:
        original = TWO_SYSTEMS
        encoded = drawio_serialization.encode_diagram_data(original)
        assert drawio_serialization.decode_diagram_data(encoded) == original

    def test_round_trip_survives_non_ascii_labels(self) -> None:
        original = model(vertex("2", "Zahlungsverkehr"))
        encoded = drawio_serialization.encode_diagram_data(original)
        assert drawio_serialization.decode_diagram_data(encoded) == original


class TestPrettyPrint:
    def test_pretty_print_indents_valid_xml(self) -> None:
        printed = c4izr().pretty_print("<a><b/></a>")
        assert "\n" in printed
        assert "<?xml" not in printed

    def test_pretty_print_returns_unparseable_input_unchanged(self) -> None:
        assert c4izr().pretty_print("not xml at all") == "not xml at all"


class TestEndToEnd:
    @pytest.mark.parametrize("fixture", ["TwoBoxes.drawio", "SimpleBoxes.drawio"])
    def test_committed_diagram_converts_and_writes(self, fixture: str, tmp_path: Path) -> None:
        """Full path on a real file, with output in tmp_path rather than the repo root."""
        from lxml import etree

        source = HERE / fixture
        assert source.exists(), f"fixture {fixture} is missing"

        tree = etree.parse(str(source))
        diagrams = tree.findall(".//diagram")
        assert diagrams, "fixture contains no diagram"

        diagram = diagrams[0]
        if diagram.text and not diagram.text.isspace():
            xml_string = drawio_serialization.decode_diagram_data(diagram.text)
        else:
            graph_model = diagram.find(".//mxGraphModel")
            assert graph_model is not None
            xml_string = etree.tostring(graph_model, encoding="utf-8").decode("utf-8")

        output_xml = c4izr().translate(xml_string)
        converted = objects(output_xml)
        assert converted, "conversion produced no C4 objects"
        assert styles(output_xml).count(MAIN_SYSTEM_STYLE) == 1

        destination = tmp_path / "converted.drawio"
        data = drawio_serialization.encode_diagram_data(output_xml)
        drawio_utils.write_drawio_output(data, str(destination))
        assert destination.exists()
        assert destination.stat().st_size > 0


class TestOptionalModulesImport:
    def test_vision_modules_import_without_an_api_key(self) -> None:
        """The vision path needs a key and a network call to run, so this only proves
        the modules are importable and have not drifted syntactically."""
        pytest.importorskip("anthropic")
        import png2drawio
        import vision_diagram_parser

        assert hasattr(vision_diagram_parser, "VisionDiagramParser")
        assert hasattr(png2drawio, "DiagramToDrawIO")
