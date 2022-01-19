import argparse
import json
from collections import defaultdict

from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description='Process GraphML to Video Map JSON.')
parser.add_argument(
    '--input', '-i', type=argparse.FileType('r'),
    metavar='PATH', required=True,
    help="Input file")
parser.add_argument(
    '--output', '-o', type=argparse.FileType('w', encoding='UTF-8'),
    metavar='PATH', required=True,
    help="Output file")

args = parser.parse_args()

# Edge color definitions
def_color = "#000000"
alt_color = "#FF6600"

# Load graphml file
with args.input as file:
    soup = BeautifulSoup(file, "lxml")

# Initialize graph dictionary
graph = defaultdict(dict)

# Put all nodes into a dict with their label
node_dict = {}
for node in soup.findAll("node"):
    node_id = node["id"]
    label = node.find("y:nodelabel").text.strip()
    node_dict[node_id] = label

# Go over every edge
for edge in soup.findAll("edge"):
    # Get source and target node
    source_label = node_dict.get(edge["source"])
    target_label = node_dict.get(edge["target"])

    # Find default and alt targets by line color
    color = edge.find("y:linestyle")["color"]

    if color == def_color:
        # if there's already a dict there, add default entry
        if graph[source_label]:
            this = graph[source_label]
            this["def"] = target_label
        else:
            # otherwise add a new dict entry
            graph[source_label] = {"def": target_label}

        print("Processed {} [def]-> {}...".format(source_label, target_label))

    elif color == alt_color:
        if graph[source_label]:
            this = graph[source_label]
            this["alt"] = target_label
        else:
            graph[source_label] = {"alt": target_label}

        print("Processed {} [alt]-> {}...".format(source_label, target_label))

    else:
        print("Error on edge {}".format(edge["id"]))
        break

print("Verifying nodes and edges...")
for name, node in graph.items():
    try:
        assert node["def"]
        assert node["alt"]
    except KeyError:
        print("Node '{}' is missing an edge!".format(name))
        exit(1)

# convert dict to json
graph_json = json.dumps(graph, indent=2)

# save plaintext json
with args.output as file:
    file.write(graph_json)

print("Wrote Video Map.")
