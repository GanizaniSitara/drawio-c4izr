import os
##
#
# NOTE WE'RE USING the GPT Version at the moment not the c4izr.
#
##
from c4izr import c4izr
import subprocess
import lxml.etree as etree
import drawio_serialization
import xml.etree.ElementTree as ET
import drawio_utils

class XMLParseException(Exception):
    # TODO not sure what he exact intent was with this ...
    pass


def drawio_xml(xml_file):
    try:
        tree = etree.parse(xml_file)
        diagrams = tree.findall('.//diagram')
        # TODO need to decide how to handle multiple diagrams in a single file
        # feels like we should inform the user that there are multiple diagrams
        # and then still iterate, perhaps giving choice of the diagram page to process
        if len (diagrams) > 1:
            print(f"WARN - Multiple diagrams found in file: {xml_file}. Converting only the first.")
        xml_data = diagrams[0]

        # NOTE!!
        # sometimes the "plain xml" files create with drawio desktop will still have the text
        # attribute in them with '\n ' as content so we need to check for that as well
        if hasattr(xml_data, 'text') and not xml_data.text.isspace():
            try:
                xml_string = drawio_serialization.decode_diagram_data(xml_data.text)
                return xml_string
            except Exception:
                pass
        else:
            xml_data = xml_data.find('.//mxGraphModel')
        xml_string = ET.tostring(xml_data, encoding='utf-8').decode('utf-8')
        return xml_string
    except Exception as e:
        error_message = f"Error parsing XML file: {xml_file}, {str(e)}"
        raise XMLParseException(error_message)


def do_process(file):
    input_xml = drawio_xml(file)
    translator = c4izr()
    output_xml = translator.translate(input_xml)
    # pretty_output_xml = translator.pretty_print(output_xml)
    # print(pretty_output_xml)
    return output_xml



DRAWIO_EXECUTABLE_PATH = "C:\\Program Files\\draw.io\\draw.io.exe"
DRAWIO_EXISTING_DIAGRAMS_DIR = 'C:\\Solutions\\Python\\AllConcepts\\drawio_github'

def process_file(file_path):
    process = subprocess.Popen([DRAWIO_EXECUTABLE_PATH, file_path])
    process.wait()

    output_xml = do_process(file_path)
    data = drawio_serialization.encode_diagram_data(output_xml)
    drawio_utils.write_drawio_output(data, "output.drawio")

    process = subprocess.Popen([DRAWIO_EXECUTABLE_PATH, 'output.drawio'])
    process.wait()

def process_directory(directory_path):
    for root, _, files in os.walk(directory_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            if os.path.isfile(file_path):
                process_file(file_path)

if __name__ == "__main__":
    process_directory(DRAWIO_EXISTING_DIAGRAMS_DIR)

