import base64
from os import listdir
from PIL import Image
from io import BytesIO
import argparse

parser = argparse.ArgumentParser(description='Process JPEGs in imgs folder to GraphML file.')
parser.add_argument(
    '--output', '-o', type=argparse.FileType('w', encoding='UTF-8'),
    metavar='PATH', required=True,
    help="Output file")

args = parser.parse_args()

images = listdir("./imgs")
pairs = {}

# Load image data
n = 0
for image in images:
    with BytesIO() as buffer:
        # save img as png to buffer
        with Image.open("./imgs/" + image, 'r') as im:
            im.save(buffer, format="PNG")

        # reset file pointer to start
        buffer.seek(0)

        # read bytes
        img_bytes = buffer.read()

    pairs[(n, image[:-4])] = base64.b64encode(img_bytes)
    n += 1

print("Loaded images.")

graphml_start = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:java="http://www.yworks.com/xml/yfiles-common/1.0/java" xmlns:sys="http://www.yworks.com/xml/yfiles-common/markup/primitives/2.0" xmlns:x="http://www.yworks.com/xml/yfiles-common/markup/2.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:y="http://www.yworks.com/xml/graphml" xmlns:yed="http://www.yworks.com/xml/yed/3" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://www.yworks.com/xml/schema/graphml/1.1/ygraphml.xsd">
  <key attr.name="Beschreibung" attr.type="string" for="graph" id="d0"/>
  <key for="port" id="d1" yfiles.type="portgraphics"/>
  <key for="port" id="d2" yfiles.type="portgeometry"/>
  <key for="port" id="d3" yfiles.type="portuserdata"/>
  <key attr.name="url" attr.type="string" for="node" id="d4"/>
  <key attr.name="description" attr.type="string" for="node" id="d5"/>
  <key for="node" id="d6" yfiles.type="nodegraphics"/>
  <key for="graphml" id="d7" yfiles.type="resources"/>
  <key attr.name="url" attr.type="string" for="edge" id="d8"/>
  <key attr.name="description" attr.type="string" for="edge" id="d9"/>
  <key for="edge" id="d10" yfiles.type="edgegraphics"/>
  <graph edgedefault="directed" id="G">
    <data key="d0" xml:space="preserve"/>
'''
graphml_mid = '''</graph>
  <data key="d7">
    <y:Resources>
      '''
graphml_end = '''
    </y:Resources>
  </data>
</graphml>
'''

node = '''    <node id="n{nodeid}">
      <data key="d6">
        <y:ImageNode>
          <y:Geometry height="135.0" width="240.0" x="0" y="{y}"/>
          <y:Fill color="#CCCCFF" transparent="false"/>
          <y:BorderStyle color="#000000" type="line" width="1.0"/>
          <y:NodeLabel alignment="center" autoSizePolicy="content" fontFamily="Dialog" fontSize="12" fontStyle="plain" hasBackgroundColor="false" hasLineColor="false" height="18.701171875" horizontalTextPosition="center" iconTextGap="4" modelName="sandwich" modelPosition="s" textColor="#000000" verticalTextPosition="bottom" visible="true" width="36.671875" x="101.6640625" xml:space="preserve" y="139.0">{label}</y:NodeLabel>
          <y:Image alphaImage="true" refid="{refid}"/>
        </y:ImageNode>
      </data>
    </node>
'''
resource = '<y:Resource id="{id}" type="java.awt.image.BufferedImage" xml:space="preserve">{imagedata}</y:Resource>'

final_text = graphml_start

# create alle nodes
for pair in pairs:
    nodeid, label = pair
    refid = nodeid + 1
    y = 145 * nodeid  # put node below the previous

    final_text += node.format(nodeid=nodeid, refid=refid, y=y, label=label)

final_text += graphml_mid
# insert image data
for key, value in pairs.items():
    _id = key[0] + 1
    imagedata = value.decode()
    final_text += resource.format(id=_id, imagedata=imagedata)

final_text += graphml_end

with args.output as f:
    f.write(final_text)

print("Wrote GraphML file.")
