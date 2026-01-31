

# c4izr.py - Converts draw.io diagrams to common C4 representation



import xml.etree.ElementTree as ET

import uuid

import sys

import logging



class c4izr:

    def __init__(self, scaling_factor=1.4):

        self.interactive = True

        self.scaling_factor = scaling_factor

        self.logger = logging.getLogger('c4izr')

        

        # Configure logging

        handler = logging.StreamHandler(sys.stdout)

        formatter = logging.Formatter('%(levelname)s - %(message)s')

        handler.setFormatter(formatter)

        self.logger.addHandler(handler)

        self.logger.setLevel(logging.INFO)



    def translate(self, input_xml):
        """
        Translate a draw.io XML string to C4 format.
        
        Args:
            input_xml (str): XML string from draw.io
            
        Returns:
            str: Translated XML in C4 format
        """
        try:
            input_tree = ET.ElementTree(ET.fromstring(input_xml))
            input_root = input_tree.getroot()
        except ET.ParseError as e:
            self.logger.error(f"Failed to parse input XML: {e}")
            raise ValueError(f"Invalid XML format: {e}")

        output_root = ET.Element("mxGraphModel", input_root.attrib)
        new_root = ET.SubElement(output_root, "root")

        # Add the required <mxCell> elements at the top
        ET.SubElement(new_root, "mxCell", id="0")
        ET.SubElement(new_root, "mxCell", id="1", parent="0")

        existing_ids = {elem.get('id') for elem in input_root.findall('.//mxCell')}

        # Calculate the center of the diagram
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        
        # Find all boxes (vertices) in the diagram
        vertices = input_root.findall('.//mxCell[@vertex="1"]')
        if not vertices:
            self.logger.warning("No elements found in the diagram")
            return ET.tostring(output_root, encoding='unicode', method='xml')
            
        for mxcell in vertices:
            mxgeometry = mxcell.find('mxGeometry')
            if mxgeometry is not None:
                try:
                    x = float(mxgeometry.get("x", 0))
                    y = float(mxgeometry.get("y", 0))
                    width = float(mxgeometry.get("width", 0))
                    height = float(mxgeometry.get("height", 0))
                    
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x + width)
                    max_y = max(max_y, y + height)
                except (ValueError, TypeError) as e:
                    self.logger.warning(f"Invalid geometry value for element {mxcell.get('id')}: {e}")

        # Ensure we have valid bounds
        if min_x == float('inf') or min_y == float('inf') or max_x == float('-inf') or max_y == float('-inf'):
            self.logger.warning("Could not determine diagram bounds, using defaults")
            min_x = min_y = 0
            max_x = max_y = 500
            
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        # Select main system
        system = None
        if self.interactive:
            self.logger.info(f"Center of the diagram: ({center_x}, {center_y})")
            self.logger.info(f"Found:")

            for ix, mxcell in enumerate(vertices, 1):
                cell_value = mxcell.get('value', '')
                system = cell_value if system is None else system
                self.logger.info(f" {ix}. {cell_value}")

            def has_duplicates(input_list):
                return len(input_list) != len(set(input_list))

            def wait_for_number_or_default():
                while True:
                    try:
                        key = input().strip().lower()
                        if key.isdigit():
                            num = int(key)
                            if 1 <= num <= len(vertices):
                                return num
                            else:
                                self.logger.error(f"Please enter a number between 1 and {len(vertices)}")
                        elif key == '':
                            return 1
                        else:
                            self.logger.error("Please enter a valid number or press Enter for default")
                    except (EOFError, KeyboardInterrupt):
                        self.logger.info("Input interrupted. Using default value 1.")
                        return 1

            if has_duplicates([mxcell.get('value', '') for mxcell in vertices]):
                self.logger.warning("Duplicate system names found. Selecting duplicated system will mark all of them as main system.")

            self.logger.info(f"Select main system by entering the number: (default: 1)")
            selected = wait_for_number_or_default()

            system = vertices[selected - 1].get('value', '')
            self.logger.info(f"Selected: {system}")
        else:
            # In non-interactive mode, select the first system
            system = vertices[0].get('value', '')
            self.logger.info(f"Non-interactive mode: automatically selected {system} as main system")

        # Process all vertices (elements with vertex="1")
        for mxcell in vertices:
            self._process_vertex(mxcell, new_root, system, center_x, center_y)

        # Process all edges (elements with edge="1")
        for mxcell in input_root.findall('.//mxCell[@edge="1"]'):
            self._process_edge(mxcell, new_root)

        return ET.tostring(output_root, encoding='unicode', method='xml')

    def translate_multiple(self, input_xml_list):
        """
        Translate multiple draw.io XML strings to C4 format.
        
        Args:
            input_xml_list (list): List of XML strings from draw.io
            
        Returns:
            list: List of translated XML strings in C4 format
        """
        return [self.translate(input_xml) for input_xml in input_xml_list]



    def _process_vertex(self, mxcell, new_root, system, center_x, center_y):

        """Process a vertex element and add it to the new root."""

        try:

            object_elem = ET.SubElement(new_root, "object")

            object_elem.set("id", mxcell.attrib.get("id", str(uuid.uuid4())))



            object_elem.set("placeholders", "1")

            object_elem.set("c4Name", mxcell.get("value", ""))

            object_elem.set("c4Type", "Software System")

            object_elem.set("c4Description", f"Description of {mxcell.get('value', '').lower()}.")



            label = ('<font style="font-size: 16px"><b>%c4Name%</b></font>'

                    '<div>[%c4Type%]</div><br>'

                    '<div><font style="font-size: 11px">'

                    '<font color="#cccccc">%c4Description%</font></div>')



            object_elem.set("label", label)



            # Apply C4 style based on whether this is the main system

            if mxcell.get("value") == system:

                style = "rounded=1;whiteSpace=wrap;html=1;labelBackgroundColor=none;fillColor=#1061B0;fontColor=#ffffff;align=center;arcSize=10;strokeColor=#0D5091;metaEdit=1;resizable=0;points=[[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0.25,0],[1,0.5,0],[1,0.75,0],[0.75,1,0],[0.5,1,0],[0.25,1,0],[0,0.75,0],[0,0.5,0],[0,0.25,0]];"

            else:

                style = "rounded=1;whiteSpace=wrap;html=1;labelBackgroundColor=none;fillColor=#8C8496;fontColor=#ffffff;align=center;arcSize=10;strokeColor=#736782;metaEdit=1;resizable=0;points=[[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0.25,0],[1,0.5,0],[1,0.75,0],[0.75,1,0],[0.5,1,0],[0.25,1,0],[0,0.75,0],[0,0.5,0],[0,0.25,0]];"



            object_mxcell = ET.SubElement(object_elem, "mxCell", {

                "style": style,

                "vertex": "1",

                "parent": "1"

            })

            

            # Handle geometry with scaling and positioning

            mxgeometry = mxcell.find('mxGeometry')

            if mxgeometry is not None:

                # Create a new geometry element

                new_geometry = ET.Element('mxGeometry')

                

                # Standard C4 box dimensions

                new_geometry.set("width", "240")

                new_geometry.set("height", "120")

                

                # Apply scaling relative to center

                if mxgeometry.get("x") is not None:

                    try:

                        x = float(mxgeometry.get("x"))

                        dx = x - center_x

                        x_new = center_x + dx * self.scaling_factor

                        new_geometry.set("x", str(x_new))

                    except (ValueError, TypeError):

                        new_geometry.set("x", mxgeometry.get("x"))

                        self.logger.warning(f"Could not scale x coordinate for element {mxcell.get('id')}")

                

                if mxgeometry.get("y") is not None:

                    try:

                        y = float(mxgeometry.get("y"))

                        dy = y - center_y

                        y_new = center_y + dy * self.scaling_factor

                        new_geometry.set("y", str(y_new))

                    except (ValueError, TypeError):

                        new_geometry.set("y", mxgeometry.get("y"))

                        self.logger.warning(f"Could not scale y coordinate for element {mxcell.get('id')}")

                

                # Copy any other relevant attributes

                for attr in mxgeometry.attrib:

                    if attr not in ['x', 'y', 'width', 'height']:

                        new_geometry.set(attr, mxgeometry.get(attr))

                

                object_mxcell.append(new_geometry)

        except Exception as e:

            self.logger.error(f"Error processing vertex {mxcell.get('id')}: {e}")

            # Continue processing other elements



    def _process_edge(self, mxcell, new_root):

        """Process an edge element and add it to the new root."""

        try:

            # Skip edges without proper source or target

            if 'source' not in mxcell.attrib or 'target' not in mxcell.attrib:

                self.logger.warning(f"Floating edge (arrow) {mxcell.get('id')}")

                new_root.append(mxcell)

                return



            object_elem = ET.SubElement(new_root, "object")

            object_elem.set("id", mxcell.attrib.get('id', str(uuid.uuid4())))



            object_elem.set("placeholders", "1")

            object_elem.set("c4Type", "Relationship")

            object_elem.set("c4Technology", "e.g. JSON/HTTP")

            object_elem.set("c4Description", "e.g. Makes API calls")

            

            # Use the edge label if available

            if 'value' in mxcell.attrib and mxcell.get('value'):

                object_elem.set("c4Description", mxcell.get('value'))



            label = ('<div style="text-align: left">'

                    '<div style="text-align: center"><b>%c4Description%</b></div>'

                    '<div style="text-align: center">[%c4Technology%]</div></div>')



            object_elem.set("label", label)



            # Create the edge cell with C4 styling

            object_mxcell = ET.SubElement(object_elem, "mxCell", {

                "style": "endArrow=blockThin;html=1;fontSize=10;fontColor=#404040;strokeWidth=1;endFill=1;strokeColor=#828282;elbow=vertical;metaEdit=1;endSize=14;startSize=14;jumpStyle=arc;jumpSize=16;rounded=0;edgeStyle=orthogonalEdgeStyle;",

                "edge": "1",

                "parent": "1",

                "source": mxcell.get("source"),

                "target": mxcell.get("target")

            })

            

            # Copy all geometry information

            for mxgeometry in mxcell.findall('mxGeometry'):

                object_mxcell.append(mxgeometry)

        except Exception as e:

            self.logger.error(f"Error processing edge {mxcell.get('id')}: {e}")

            # Continue processing other elements



    def pretty_print(self, xml_string):

        """Format XML string with proper indentation for better readability."""

        try:

            import xml.dom.minidom

            dom = xml.dom.minidom.parseString(xml_string)

            return '\n'.join([line for line in dom.toprettyxml(indent="  ").split('\n') if line.strip() and not line.startswith('<?xml')])

        except Exception as e:

            self.logger.error(f"Error formatting XML: {e}")

            return xml_string



    @staticmethod

    def filter_string(input_string):

        """Filter out exit and entry points from style strings."""

        try:

            elements = input_string.split(';')

            filtered_elements = [elem for elem in elements if not elem.startswith('exit') and not elem.startswith('entry')]

            return ';'.join(filtered_elements) + ';'

        except Exception as e:

            logging.error(f"Error filtering string: {e}")

            return input_string



if __name__ == "__main__":

    # Usage example

    input_xml = '''<mxGraphModel dx="1418" dy="948" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="850" pageHeight="1100" math="0" shadow="0">

  <root>

    <mxCell id="0" />

    <mxCell id="1" parent="0" />

    <mxCell id="3" style="edgeStyle=none;html=1;" parent="1" source="2" target="4" edge="1">

      <mxGeometry relative="1" as="geometry">

        <mxPoint x="320" y="380" as="targetPoint" />

      </mxGeometry>

    </mxCell>

    <mxCell id="6" style="edgeStyle=none;html=1;" parent="1" source="2" target="5" edge="1">

      <mxGeometry relative="1" as="geometry" />

    </mxCell>

    <mxCell id="2" value="System A" style="rounded=0;whiteSpace=wrap;html=1;" parent="1" vertex="1">

      <mxGeometry x="260" y="170" width="120" height="60" as="geometry" />

    </mxCell>

    <mxCell id="8" style="edgeStyle=none;html=1;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" parent="1" source="4" target="7" edge="1">

      <mxGeometry relative="1" as="geometry" />

    </mxCell>

    <mxCell id="4" value="System C" style="rounded=1;whiteSpace=wrap;html=1;" parent="1" vertex="1">

      <mxGeometry x="260" y="350" width="120" height="60" as="geometry" />

    </mxCell>

    <mxCell id="5" value="System B" style="ellipse;whiteSpace=wrap;html=1;aspect=fixed;" parent="1" vertex="1">

      <mxGeometry x="600" y="160" width="80" height="80" as="geometry" />

    </mxCell>

    <mxCell id="7" value="System D" style="rhombus;whiteSpace=wrap;html=1;" parent="1" vertex="1">

      <mxGeometry x="280" y="490" width="80" height="80" as="geometry" />

    </mxCell>

  </root>

</mxGraphModel>

'''



    translator = c4izr()

    output_xml = translator.translate(input_xml)

    pretty_output_xml = translator.pretty_print(output_xml)

    print(pretty_output_xml)



    import subprocess
    import shutil
    import platform
    import drawio_serialization
    import drawio_utils

    data = drawio_serialization.encode_diagram_data(output_xml)
    drawio_utils.write_drawio_output(data, "output.drawio")

    # Use platform-independent path lookup to find draw.io executable
    drawio_path = shutil.which("draw.io") or shutil.which("drawio")
    if drawio_path is None:
        # Fall back to common installation locations
        if platform.system() == "Windows":
            drawio_path = "C:\\Program Files\\draw.io\\draw.io.exe"
        elif platform.system() == "Darwin":
            drawio_path = "/Applications/draw.io.app/Contents/MacOS/draw.io"
        else:
            drawio_path = "/usr/bin/drawio"

    # Use subprocess with list arguments to avoid command injection vulnerability
    if drawio_path:
        try:
            subprocess.run([drawio_path, "output.drawio"], check=False)
        except FileNotFoundError:
            print(f"Warning: draw.io executable not found at {drawio_path}")
