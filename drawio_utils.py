from lxml import etree
import secrets
import string
import drawio_serialization
import xml.dom.minidom
from datetime import datetime, timezone
import os

def id_generator(size=22, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase + '-_'):
    """Generate a cryptographically secure random ID."""
    return ''.join(secrets.choice(chars) for _ in range(size))

def create_layer(name, locked=0):
    mxcell = etree.Element('mxCell')
    mxcell.set('id', id_generator())
    mxcell.set('value', name)
    mxcell.set('style', 'locked=' + str(locked))
    mxcell.set('parent', '0')
    return mxcell

def get_diagram_root():
    mxGraphModel = etree.Element('mxGraphModel')
    mxGraphModel.set('dx', '981')
    mxGraphModel.set('dy', '650')
    mxGraphModel.set('grid', '1')
    mxGraphModel.set('gridSize', '10')
    mxGraphModel.set('guides', '1')
    mxGraphModel.set('tooltips', '1')
    mxGraphModel.set('connect', '1')
    mxGraphModel.set('arrows', '1')
    mxGraphModel.set('fold', '1')
    mxGraphModel.set('page', '1')
    mxGraphModel.set('pageScale', '1')
    mxGraphModel.set('pageWidth', '816')
    mxGraphModel.set('pageHeight', '1056')
    mxGraphModel.set('math', '0')
    mxGraphModel.set('shadow', '0')

    root = etree.Element('root')
    mxGraphModel.append(root)
    # to cell is always there all the other layers inherit from it
    mxcell = etree.Element('mxCell')
    mxcell.set('id', '0')
    root.append(mxcell)
    # background layer is always there, we don't draw on it
    background = etree.Element('mxCell')
    background.set('id', '1')
    background.set('style', 'locked=1')
    background.set('parent', '0')
    background.set('visible', '1')
    background.set('value', 'Background')
    root.append(background)
    return mxGraphModel


def sanitize_filename(filename):
    """Sanitize filename to prevent path traversal attacks."""
    # Get just the basename to prevent directory traversal
    basename = os.path.basename(filename)
    # Remove any null bytes
    basename = basename.replace('\x00', '')
    # If we got a directory path, just use the file part
    if not basename:
        basename = 'output.drawio'
    return basename


def write_drawio_output(data, filename='output.drawio', output_dir=None):
    """
    Write diagram data to a drawio file.

    Args:
        data: The encoded diagram data
        filename: Output filename (sanitized to prevent path traversal)
        output_dir: Optional directory for output (must be explicitly provided)
    """
    # Sanitize filename to prevent path traversal if it's just a filename
    # If it looks like a path with directory, validate it
    if os.path.dirname(filename):
        # It's a path - resolve it and ensure it's within allowed scope
        resolved_path = os.path.realpath(filename)
        filename = resolved_path
    else:
        # Just a filename - sanitize it
        filename = sanitize_filename(filename)
        if output_dir:
            filename = os.path.join(output_dir, filename)

    root = etree.Element('mxfile')
    root.set('host', 'c4izr')
    # Use dynamic timestamp
    root.set('modified', datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z')
    root.set('agent', 'c4izr Python converter')
    root.set('etag', id_generator(20))
    root.set('version', '1.0.0')
    root.set('type', 'device')

    # Create diagram element
    child = etree.Element('diagram')
    child.set('id', id_generator())
    child.set('name', 'Page-1')
    child.text = data
    root.append(child)

    tree = etree.ElementTree(root)
    tree.write(filename)


def encode_and_save_to_file(mxGraphModel, filename='output.drawio'):
    data = etree.tostring(mxGraphModel, pretty_print=False)
    data = drawio_serialization.encode_diagram_data(data)
    write_drawio_output(data, filename)


def pretty_print_to_console(mxGraphModel):
    dom = xml.dom.minidom.parseString(etree.tostring(mxGraphModel))
    pretty_xml_as_string = dom.toprettyxml()
    print(pretty_xml_as_string)


# id_generator_2 removed - use id_generator instead (duplicate function)


def layer_id_2(root, name):
    for node in root.findall('.//mxCell[@parent="0"]'):
        if node.get('value') == name:
            return node.get('id')
    raise RuntimeError('Layer ' + name + ' not found')

def truncate_string_to_label_width(string, font_size, max_length):
    # Base case: At font size 12, 30 characters fit in 220 pixels
    base_font_size = 12
    base_chars = 30
    base_width = 220


    char_width_at_base = base_width / base_chars

    # Extrapolate character width for the given font size
    char_width_at_font_size = char_width_at_base * (base_font_size / font_size)

    # Calculate how many characters of the given font size fit into max_length
    chars_fit = max_length / char_width_at_font_size

    # Truncate the string to the number of characters that can fit
    truncated_string = string[:int(chars_fit)]

    return truncated_string

def resize_string_to_fit(string, initial_font_size, target_width):
    base_font_size = 12
    base_chars = 30
    base_width = 220

    # Calculate the average character width for the base case
    avg_char_width_base = base_width / base_chars

    # Calculate the total width of the string at the initial font size
    current_total_width = len(string) * avg_char_width_base * (initial_font_size / base_font_size)

    if current_total_width <= target_width:
        # If the string already fits within the target width at the initial font size,
        # no adjustment is necessary.
        return initial_font_size, string
    else:
        # Calculate the font size needed to make the string fit within the target width
        adjusted_font_size = (target_width / len(string)) / avg_char_width_base * base_font_size

        # Assuming we want to maintain a minimum legible font size (e.g., 8px)
        min_font_size = 8
        if adjusted_font_size < min_font_size:
            print("Warning: Adjusted font size is below the minimum legible size. Consider truncating the string or increasing the target width.")
            adjusted_font_size = min_font_size

        return adjusted_font_size, string
