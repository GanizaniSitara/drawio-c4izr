#!/usr/bin/env python3
"""
Test script for testing the refactored c4izr implementation.
This script tests basic functionality by converting a simple diagram.
"""

import os
import sys
from c4izr import c4izr
import drawio_serialization
import drawio_utils

def test_conversion():
    """Test basic conversion functionality on TwoBoxes.drawio"""
    print("Testing conversion of TwoBoxes.drawio...")
    
    try:
        # Read the test file
        file_path = "TwoBoxes.drawio"
        if not os.path.exists(file_path):
            print(f"ERROR: Test file {file_path} not found.")
            return False
            
        print(f"Reading file: {file_path}")
        
        # Set up test translator with non-interactive mode
        translator = c4izr()
        translator.interactive = False  # Disable interactive mode for testing
        
        # Parse the file and extract XML
        print("Parsing file...")
        from lxml import etree
        tree = etree.parse(file_path)
        diagrams = tree.findall('.//diagram')
        
        if not diagrams:
            print("ERROR: No diagrams found in the file.")
            return False
            
        xml_data = diagrams[0]
        
        # Extract the XML content
        if hasattr(xml_data, 'text') and xml_data.text and not xml_data.text.isspace():
            xml_string = drawio_serialization.decode_diagram_data(xml_data.text)
        else:
            xml_data = xml_data.find('.//mxGraphModel')
            if xml_data is None:
                print("ERROR: No mxGraphModel found in the diagram.")
                return False
            xml_string = etree.tostring(xml_data, encoding='utf-8').decode('utf-8')
        
        # Translate the XML
        print("Translating XML to C4 format...")
        output_xml = translator.translate(xml_string)
        
        # Verify output XML contains C4 elements
        if "c4Name" not in output_xml or "c4Type" not in output_xml:
            print("ERROR: Output XML does not contain C4 elements.")
            return False
            
        # Write output file
        print("Writing output to test_output.drawio...")
        data = drawio_serialization.encode_diagram_data(output_xml)
        drawio_utils.write_drawio_output(data, "test_output.drawio")
        
        # Verify the output file exists
        if not os.path.exists("test_output.drawio"):
            print("ERROR: Failed to create output file.")
            return False
            
        print("Test completed successfully!")
        print(f"Output file created: test_output.drawio")
        return True
        
    except Exception as e:
        print(f"ERROR: Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_conversion()
    sys.exit(0 if success else 1)
