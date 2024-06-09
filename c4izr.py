
# TODO we could add layout logic for boxes we'll know will overlap given the scaling factor
# check both horizontally and vertically

import xml.etree.ElementTree as ET
import uuid

class c4izr:
    def __init__(self, scaling_factor=1.4):
        self.interactive = True
        self.scaling_factor = scaling_factor

    def translate(self, input_xml):
        input_tree = ET.ElementTree(ET.fromstring(input_xml))
        input_root = input_tree.getroot()

        output_root = ET.Element("mxGraphModel", input_root.attrib)
        new_root = ET.SubElement(output_root, "root")

        # Add the required <mxCell> elements at the top
        ET.SubElement(new_root, "mxCell", id="0")
        ET.SubElement(new_root, "mxCell", id="1", parent="0")

        existing_ids = {elem.get('id') for elem in input_root.findall('.//mxCell')}

        # Calculate the center of the diagram
        min_x = min_y = float('inf')
        max_x = max_y = float('-inf')
        for mxcell in input_root.findall('.//mxCell[@vertex="1"]'):
            mxgeometry = mxcell.find('mxGeometry')
            if mxgeometry is not None:
                x = float(mxgeometry.get("x", 0))
                y = float(mxgeometry.get("y", 0))
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x + float(mxgeometry.get("width", 0)))
                max_y = max(max_y, y + float(mxgeometry.get("height", 0)))
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2


        if self.interactive:
            print(f"DEBUG -Center of the diagram: ({center_x}, {center_y})")
            print(f"Found:")
            system = None

            systems_list = input_root.findall('.//mxCell[@vertex="1"]')

            for ix, mxcell in enumerate(systems_list, 1):
                system = mxcell.get('value', '') if system is None else system
                print(f" {ix}. {mxcell.get('value', '')}")

            def has_duplicates(input_list):
                return len(input_list) != len(set(input_list))

            def wait_for_number_or_default():
                while True:
                    key = input().strip().lower()
                    if key.isdigit():
                        return int(key)
                    elif key == '':
                        return 1

            if has_duplicates([mxcell.get('value', '') for mxcell in systems_list]):
                print("WARNING: Duplicate system names found. Selecting duplicated system will mark all of them as main system.")

            print(f"USER - select main system by entering the number: (default: 1)")
            selected = wait_for_number_or_default()

            system = systems_list[selected - 1].get('value', '')
            print(f"DEBUG - selected {system}")

            # print("Press Enter to continue...")
            # while True:
            #     key = input().strip().lower()
            #     if key == '':
            #         break


        for mxcell in input_root.findall('.//mxCell[@vertex="1"]'):

            object_elem = ET.SubElement(new_root, "object")
            object_elem.set("id", mxcell.attrib.get("id"))

            object_elem.set("placeholders", "1")
            object_elem.set("c4Name", mxcell.get("value", ""))
            object_elem.set("c4Type", "Software System")
            object_elem.set("c4Description", f"Description of {mxcell.get('value', '').lower()}.")

            label = ('<font style="font-size: 16px"><b>%c4Name%</b></font>'
                     '<div>[%c4Type%]</div><br>'
                     '<div><font style="font-size: 11px">'
                     '<font color="#cccccc">%c4Description%</font></div>')

            object_elem.set("label", label)

            if mxcell.get("value") == system:
                style = "rounded=1;whiteSpace=wrap;html=1;labelBackgroundColor=none;fillColor=#1061B0;fontColor=#ffffff;align=center;arcSize=10;strokeColor=#0D5091;metaEdit=1;resizable=0;points=[[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0.25,0],[1,0.5,0],[1,0.75,0],[0.75,1,0],[0.5,1,0],[0.25,1,0],[0,0.75,0],[0,0.5,0],[0,0.25,0]];"
            else:
                style = "rounded=1;whiteSpace=wrap;html=1;labelBackgroundColor=none;fillColor=#8C8496;fontColor=#ffffff;align=center;arcSize=10;strokeColor=#736782;metaEdit=1;resizable=0;points=[[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0.25,0],[1,0.5,0],[1,0.75,0],[0.75,1,0],[0.5,1,0],[0.25,1,0],[0,0.75,0],[0,0.5,0],[0,0.25,0]];"

            object_mxcell = ET.SubElement(object_elem, "mxCell", {
                "style": style,
                "vertex": "1",
                "parent": "1"
            })
            mxgeometry = mxcell.find('mxGeometry')
            if mxgeometry is not None:
                mxgeometry.set("width", "240")
                mxgeometry.set("height", "120")
                if mxgeometry.get("x") is not None:
                    x = float(mxgeometry.get("x"))
                    dx = x - center_x
                    x_new = center_x + dx * self.scaling_factor
                    mxgeometry.set("x", str(x_new))
                if mxgeometry.get("y") is not None:
                    y = float(mxgeometry.get("y"))
                    dy = y - center_y
                    y_new = center_y + dy * self.scaling_factor
                    mxgeometry.set("y", str(y_new))
                object_mxcell.append(mxgeometry)

        for mxcell in input_root.findall('.//mxCell[@edge="1"]'):
            if not mxcell.get("source") in mxcell.attrib or not mxcell.get("target") in mxcell.attrib:
                print(f"DEBUG - Floating edge (arrow) {mxcell.get('id')}")
                new_root.append(mxcell)
                continue

            object_elem = ET.SubElement(new_root, "object")
            object_elem.set("id", mxcell.attrib['id'])

            object_elem.set("placeholders", "1")
            object_elem.set("c4Type", "Relationship")
            object_elem.set("c4Technology", "e.g. JSON/HTTP")
            object_elem.set("c4Description", "e.g. Makes API calls")

            label = ('<div style="text-align: left">'
                     '<div style="text-align: center"><b>%c4Description%</b></div>'
                     '<div style="text-align: center">[%c4Technology%]</div></div>')

            object_elem.set("label", label)


            object_mxcell = ET.SubElement(object_elem, "mxCell", {
                "style": "endArrow=blockThin;html=1;fontSize=10;fontColor=#404040;strokeWidth=1;endFill=1;strokeColor=#828282;elbow=vertical;metaEdit=1;endSize=14;startSize=14;jumpStyle=arc;jumpSize=16;rounded=0;edgeStyle=orthogonalEdgeStyle;",
                "edge": "1",
                "parent": "1",
                "source": mxcell.get("source"),
                "target": mxcell.get("target")
            })
            for mxgeometry in mxcell.findall('mxGeometry'):
                object_mxcell.append(mxgeometry)

        for mxcell in input_root.findall('./mxCell'):
            new_root.append(mxcell)

        return ET.tostring(output_root, encoding='unicode', method='xml')

    def pretty_print(self, xml_string):
        import xml.dom.minidom
        dom = xml.dom.minidom.parseString(xml_string)
        return '\n'.join([line for line in dom.toprettyxml(indent="  ").split('\n') if line.strip() and not line.startswith('<?xml')])

    def filter_string(input_string):
        elements = input_string.split(';')
        filtered_elements = [elem for elem in elements if not elem.startswith('exit') and not elem.startswith('entry')]
        return ';'.join(filtered_elements) + ';'

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

    import os
    import drawio_serialization, drawio_utils
    data = drawio_serialization.encode_diagram_data(output_xml)
    drawio_utils.write_drawio_output(data, "output.drawio")
    DRAWIO_EXECUTABLE_PATH = "C:\\Program Files\\draw.io\\draw.io.exe"
    os.system(f'"{DRAWIO_EXECUTABLE_PATH}" output.drawio')
