import os
import shutil
import platform
##
#
# NOTE: This is a legacy runner script. Consider using main.py instead.
#
##
from c4izr import c4izr
import subprocess
import lxml.etree as etree
import drawio_serialization
import xml.etree.ElementTree as ET
import drawio_utils


class XMLParseException(Exception):
    """Exception raised when XML parsing fails."""
    pass


def get_drawio_executable_path():
    """Get the draw.io executable path for the current platform."""
    # First try to find it in PATH
    drawio_path = shutil.which("draw.io") or shutil.which("drawio")
    if drawio_path:
        return drawio_path

    # Fall back to platform-specific default locations
    if platform.system() == "Windows":
        return r"C:\Program Files\draw.io\draw.io.exe"
    elif platform.system() == "Darwin":
        return "/Applications/draw.io.app/Contents/MacOS/draw.io"
    else:  # Linux and others
        return "/usr/bin/drawio"


def drawio_xml(xml_file):
    try:
        # Create a secure XML parser that prevents XXE attacks
        parser = etree.XMLParser(
            resolve_entities=False,  # Disable entity resolution
            no_network=True,         # Disable network access
            dtd_validation=False,    # Disable DTD validation
            load_dtd=False           # Don't load external DTDs
        )
        tree = etree.parse(xml_file, parser)
        diagrams = tree.findall('.//diagram')
        if len(diagrams) > 1:
            print(f"WARN - Multiple diagrams found in file: {xml_file}.")
            for i, diagram in enumerate(diagrams):
                print(f"{i + 1}: {diagram.get('name', 'Unnamed Diagram')}")
            choice = input("Enter the number of the diagram to convert (or 'all' to process all): ").strip().lower()
            if choice == 'all':
                return [ET.tostring(diagram.find('.//mxGraphModel'), encoding='utf-8').decode('utf-8') for diagram in diagrams]
            else:
                try:
                    index = int(choice) - 1
                    if 0 <= index < len(diagrams):
                        xml_data = diagrams[index]
                    else:
                        print("Invalid choice. Defaulting to the first diagram.")
                        xml_data = diagrams[0]
                except ValueError:
                    print("Invalid input. Defaulting to the first diagram.")
                    xml_data = diagrams[0]
        else:
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



# Use platform-independent path detection
DRAWIO_EXECUTABLE_PATH = get_drawio_executable_path()
DRAWIO_EXISTING_DIAGRAMS_DIR = os.environ.get('DRAWIO_DIAGRAMS_DIR', os.path.expanduser('~/drawio_diagrams'))


def ask_user_to_translate():
    response = input("Do you want to translate the file to C4? (yes/no, default is yes): ").strip().lower()
    return response in ('', 'yes', 'y')


def process_file(file_path):
    """Process a single drawio file."""
    drawio_path = get_drawio_executable_path()

    if not os.path.isfile(drawio_path):
        print(f"Warning: draw.io executable not found at {drawio_path}")
        print("Skipping file preview. Set the path in DRAWIO_EXECUTABLE_PATH environment variable.")
    else:
        print("Instructions: The original drawio file will be opened for review. Please review the file and close it when done.")
        try:
            process = subprocess.Popen([drawio_path, file_path])
            process.wait()
        except FileNotFoundError:
            print(f"Error: Could not find draw.io executable at {drawio_path}")
        except PermissionError:
            print(f"Error: Permission denied to execute {drawio_path}")

    if not ask_user_to_translate():
        return

    try:
        output_xml = do_process(file_path)
        data = drawio_serialization.encode_diagram_data(output_xml)
        drawio_utils.write_drawio_output(data, "output.drawio")

        if os.path.isfile(drawio_path):
            try:
                process = subprocess.Popen([drawio_path, 'output.drawio'])
                process.wait()
            except (FileNotFoundError, PermissionError) as e:
                print(f"Error opening output file: {e}")
    except XMLParseException as e:
        print(f"Error processing file: {e}")
    except ValueError as e:
        print(f"Error translating file: {e}")

def process_directory(directory_path):
    for root, _, files in os.walk(directory_path):
        for filename in files:
            file_path = os.path.join(root, filename)
            if os.path.isfile(file_path):
                process_file(file_path)

if __name__ == "__main__":
    process_directory(DRAWIO_EXISTING_DIAGRAMS_DIR)
