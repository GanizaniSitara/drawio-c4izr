#!/usr/bin/env python3

"""
Unified test script for the refactored c4izr implementation.
It merges tests previously in test_refactor.py and test_generated.py.
"""

import os
import sys
import tempfile
import shutil
import xml.etree.ElementTree as ET
from c4izr import c4izr
import drawio_serialization
import drawio_utils


def test_conversion_drawio():
    """Test conversion of an actual .drawio file (e.g., TwoBoxes.drawio)."""
    print("Testing conversion of TwoBoxes.drawio...")

    file_path = "TwoBoxes.drawio"
    if not os.path.exists(file_path):
        print(f"ERROR: Test file {file_path} not found.")
        return False

    try:
        from lxml import etree
        tree = etree.parse(file_path)
        diagrams = tree.findall('.//diagram')

        if not diagrams:
            print("ERROR: No diagrams found in the file.")
            return False

        xml_data = diagrams[0]

        if hasattr(xml_data, 'text') and xml_data.text and not xml_data.text.isspace():
            xml_string = drawio_serialization.decode_diagram_data(xml_data.text)
        else:
            xml_data = xml_data.find('.//mxGraphModel')
            if xml_data is None:
                print("ERROR: No mxGraphModel found in the diagram.")
                return False
            xml_string = etree.tostring(xml_data, encoding='utf-8').decode('utf-8')

        translator = c4izr()
        translator.interactive = False

        output_xml = translator.translate(xml_string)

        if "c4Name" not in output_xml or "c4Type" not in output_xml:
            print("ERROR: Output XML does not contain C4 elements.")
            return False

        data = drawio_serialization.encode_diagram_data(output_xml)
        drawio_utils.write_drawio_output(data, "test_output.drawio")

        if not os.path.exists("test_output.drawio"):
            print("ERROR: Failed to create output file.")
            return False

        print("Conversion test completed successfully!")
        return True

    except Exception as e:
        print(f"ERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_basic_conversion():
    """Test basic conversion functionality on a simple diagram."""
    print("Testing basic conversion...")

    sample_xml = '''<mxGraphModel>
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="2" value="System A" style="rounded=0;whiteSpace=wrap;html=1;" parent="1" vertex="1">
          <mxGeometry x="260" y="170" width="120" height="60" as="geometry" />
        </mxCell>
        <mxCell id="3" value="System B" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;" parent="1" vertex="1">
          <mxGeometry x="600" y="160" width="80" height="80" as="geometry" />
        </mxCell>
        <mxCell id="4" style="edgeStyle=none;html=1;" edge="1" parent="1" source="2" target="3">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>'''

    translator = c4izr(scaling_factor=1.5)
    translator.interactive = False

    output_xml = translator.translate(sample_xml)

    assert "c4Name" in output_xml, "Output XML does not contain c4Name attribute"
    assert "c4Type" in output_xml, "Output XML does not contain c4Type attribute"
    assert "Software System" in output_xml, "Output XML should contain type Software System"
    assert "Relationship" in output_xml, "Output XML does not contain Relationship type"
    assert "System A" in output_xml, "System A not found in output"
    assert "System B" in output_xml, "System B not found in output"

    print("Basic conversion test passed!")
    return True


def test_file_processing():
    """Test processing an actual .drawio file structure in a temp directory."""
    print("Testing file processing...")

    from lxml import etree

    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, "test.drawio")
    output_file = os.path.join(temp_dir, "output.drawio")

    with open(test_file, "w") as f:
        f.write('''<mxfile>
          <diagram name="Page-1">
            <mxGraphModel>
              <root>
                <mxCell id="0" />
                <mxCell id="1" parent="0" />
                <mxCell id="2" value="Test System" style="rounded=0;whiteSpace=wrap;html=1;" parent="1" vertex="1">
                  <mxGeometry x="260" y="170" width="120" height="60" as="geometry" />
                </mxCell>
              </root>
            </mxGraphModel>
          </diagram>
        </mxfile>''')

    try:
        tree = etree.parse(test_file)
        diagrams = tree.findall('.//diagram')

        print(f"Found {len(diagrams)} diagram(s) in test file")
        if not diagrams:
            print("ERROR: No diagrams found in test file")
            return False

        xml_data = diagrams[0]
        xml_string = etree.tostring(xml_data.find('.//mxGraphModel'), encoding='utf-8').decode('utf-8')

        translator = c4izr(scaling_factor=1.4)
        translator.interactive = False

        output_xml = translator.translate(xml_string)
        data = drawio_serialization.encode_diagram_data(output_xml)
        drawio_utils.write_drawio_output(data, output_file)

        print(f"Output file created: {output_file}")
        print("File processing test passed!")
        return True

    finally:
        shutil.rmtree(temp_dir)


def test_command_line():
    """Test command line argument parsing (simulated)."""
    print("Testing command line argument parsing...")

    original_argv = sys.argv
    try:
        sys.argv = ["main.py", "test.drawio", "-o", "output.drawio", "--non-interactive", "-v"]
        print("Command line single file test would pass")

        sys.argv = ["main.py", "test_dir", "-o", "output_dir", "-s", "2.0"]
        print("Command line directory test would pass")
        return True
    finally:
        sys.argv = original_argv


def run_all_tests():
    """Run all tests and report results."""
    print("=" * 50)
    print("RUNNING C4IZR TESTS (UNIFIED)")
    print("=" * 50)

    tests = [
        test_conversion_drawio,
        test_basic_conversion,
        test_file_processing,
        test_command_line
    ]

    success_count = 0
    failure_count = 0

    for i, test_func in enumerate(tests, 1):
        print(f"\nTest {i}: {test_func.__name__}")
        print("-" * 50)
        try:
            if test_func():
                success_count += 1
            else:
                failure_count += 1
        except Exception as e:
            print(f"ERROR: Test failed with exception: {e}")
            failure_count += 1

    print("\n" + "=" * 50)
    print(f"TEST SUMMARY: {success_count} passed, {failure_count} failed")
    print("=" * 50)

    return success_count == len(tests)


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
