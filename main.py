
from c4izr import c4izr

input_xml = '''
<mxGraphModel dx="1418" dy="948" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
  <root>
    <mxCell id="0" />
    <mxCell id="1" parent="0" />
    <mxCell id="Gn2PjE0u4oeQyPnQltGL-1" value="" style="triangle;whiteSpace=wrap;html=1;rotation=-90;fillColor=#f5f5f5;fontColor=#333333;strokeColor=none;" parent="1" vertex="1">
      <mxGeometry x="220" y="60" width="40" height="80" as="geometry" />
    </mxCell>
    <mxCell id="Gn2PjE0u4oeQyPnQltGL-2" value="Project-Specific" style="shape=trapezoid;perimeter=trapezoidPerimeter;whiteSpace=wrap;html=1;fixedSize=1;" parent="1" vertex="1">
      <mxGeometry x="180" y="120" width="120" height="20" as="geometry" />
    </mxCell>
    <mxCell id="Gn2PjE0u4oeQyPnQltGL-3" value="Org-Specific" style="shape=trapezoid;perimeter=trapezoidPerimeter;whiteSpace=wrap;html=1;fixedSize=1;" parent="1" vertex="1">
      <mxGeometry x="160" y="140" width="160" height="20" as="geometry" />
    </mxCell>
    <mxCell id="Gn2PjE0u4oeQyPnQltGL-4" value="Sectors-Specific" style="shape=trapezoid;perimeter=trapezoidPerimeter;whiteSpace=wrap;html=1;fixedSize=1;size=40;verticalAlign=top;" parent="1" vertex="1">
      <mxGeometry x="120" y="160" width="240" height="40" as="geometry" />
    </mxCell>
    <mxCell id="Gn2PjE0u4oeQyPnQltGL-5" value="System Baseline" style="shape=trapezoid;perimeter=trapezoidPerimeter;whiteSpace=wrap;html=1;fixedSize=1;" parent="1" vertex="1">
      <mxGeometry x="100" y="200" width="280" height="20" as="geometry" />
    </mxCell>
    <mxCell id="Gn2PjE0u4oeQyPnQltGL-6" value="leveraging &amp;amp;&lt;br&gt;superceding&lt;br&gt;if/as required" style="endArrow=classic;html=1;rounded=0;startArrow=oval;startFill=0;" parent="1" edge="1">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="90" y="130" as="sourcePoint" />
        <mxPoint x="90" y="210" as="targetPoint" />
      </mxGeometry>
    </mxCell>
    <mxCell id="Gn2PjE0u4oeQyPnQltGL-7" value="" style="shape=trapezoid;perimeter=trapezoidPerimeter;whiteSpace=wrap;html=1;fixedSize=1;dashed=1;fillColor=none;" parent="1" vertex="1">
      <mxGeometry x="120" y="180" width="240" height="20" as="geometry" />
    </mxCell>
    <mxCell id="Gn2PjE0u4oeQyPnQltGL-8" value="" style="endArrow=none;dashed=1;html=1;strokeWidth=1;rounded=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;exitX=0.5;exitY=1;exitDx=0;exitDy=0;" parent="1" edge="1">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="200" y="200" as="sourcePoint" />
        <mxPoint x="200" y="180" as="targetPoint" />
      </mxGeometry>
    </mxCell>
    <mxCell id="Gn2PjE0u4oeQyPnQltGL-9" value="Education" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;dashed=1;fontStyle=2;fontSize=10;" parent="1" vertex="1">
      <mxGeometry x="130" y="180" width="60" height="20" as="geometry" />
    </mxCell>
    <mxCell id="Gn2PjE0u4oeQyPnQltGL-10" value="Government" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;dashed=1;fontStyle=2;fontSize=10;" parent="1" vertex="1">
      <mxGeometry x="210" y="180" width="60" height="20" as="geometry" />
    </mxCell>
    <mxCell id="Gn2PjE0u4oeQyPnQltGL-11" value="" style="endArrow=none;dashed=1;html=1;strokeWidth=1;rounded=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;exitX=0.5;exitY=1;exitDx=0;exitDy=0;" parent="1" edge="1">
      <mxGeometry width="50" height="50" relative="1" as="geometry">
        <mxPoint x="280" y="200" as="sourcePoint" />
        <mxPoint x="280" y="180" as="targetPoint" />
      </mxGeometry>
    </mxCell>
    <mxCell id="Gn2PjE0u4oeQyPnQltGL-12" value="Other" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;dashed=1;fontStyle=2;fontSize=10;" parent="1" vertex="1">
      <mxGeometry x="280" y="180" width="60" height="20" as="geometry" />
    </mxCell>
  </root>
</mxGraphModel>
'''

input_xml2 = '''
<mxGraphModel dx="1418" dy="948" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="1169" pageHeight="827" math="0" shadow="0">
  <root>
    <mxCell id="0" />
    <mxCell id="1" parent="0" />
    <mxCell id="MXxEXB5ajVTIcHnTvGKl-4" value="Conn A-B" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="MXxEXB5ajVTIcHnTvGKl-2" target="MXxEXB5ajVTIcHnTvGKl-3">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    <mxCell id="MXxEXB5ajVTIcHnTvGKl-2" value="System A" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="280" y="240" width="120" height="60" as="geometry" />
    </mxCell>
    <mxCell id="MXxEXB5ajVTIcHnTvGKl-6" value="Conn B-C" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="MXxEXB5ajVTIcHnTvGKl-3" target="MXxEXB5ajVTIcHnTvGKl-5">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    <mxCell id="MXxEXB5ajVTIcHnTvGKl-8" value="Conn B-D" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;" edge="1" parent="1" source="MXxEXB5ajVTIcHnTvGKl-3" target="MXxEXB5ajVTIcHnTvGKl-7">
      <mxGeometry relative="1" as="geometry" />
    </mxCell>
    <mxCell id="MXxEXB5ajVTIcHnTvGKl-3" value="System B" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="480" y="240" width="120" height="60" as="geometry" />
    </mxCell>
    <mxCell id="MXxEXB5ajVTIcHnTvGKl-10" value="Conn C-A" style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;entryX=0.5;entryY=0;entryDx=0;entryDy=0;" edge="1" parent="1" source="MXxEXB5ajVTIcHnTvGKl-5" target="MXxEXB5ajVTIcHnTvGKl-2">
      <mxGeometry relative="1" as="geometry">
        <mxPoint x="740" y="160" as="targetPoint" />
        <Array as="points">
          <mxPoint x="740" y="160" />
          <mxPoint x="340" y="160" />
        </Array>
      </mxGeometry>
    </mxCell>
    <mxCell id="MXxEXB5ajVTIcHnTvGKl-5" value="System C" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="680" y="240" width="120" height="60" as="geometry" />
    </mxCell>
    <mxCell id="MXxEXB5ajVTIcHnTvGKl-7" value="System D" style="rounded=0;whiteSpace=wrap;html=1;" vertex="1" parent="1">
      <mxGeometry x="480" y="380" width="120" height="60" as="geometry" />
    </mxCell>
  </root>
</mxGraphModel>
'''

if __name__ == "__main__":

    translator = c4izr()
    output_xml = translator.translate(input_xml)
    print(output_xml)

    import subprocess
    import drawio_serialization, drawio_utils

    DRAWIO_EXECUTABLE_PATH = "C:\\Program Files\\draw.io\\draw.io.exe"

    data = drawio_serialization.encode_diagram_data(output_xml)
    drawio_utils.write_drawio_output(data, "output.drawio")

    process = subprocess.Popen([f'{DRAWIO_EXECUTABLE_PATH}', f'output.drawio'])
    process.wait()
