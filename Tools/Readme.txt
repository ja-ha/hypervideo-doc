This folder contains two python 3 scripts to help build the videoMap.json for "Hypervideo Doc".
Required python packages are listed in requirements.txt.

------------------------------
imgsToGraph.py:
This script takes images from the "imgs" folder and places them as nodes in a GraphML file.
Useful for the following workflow:
 - Take the first frame of every videoclip you want to have in the project and export it as JPEG to "imgs". Filename should be: CLIPNAME.jpg (and corresponding: CLIPNAME.mp4)
 - Now run "python imgsToGraph.py -o OUTPUT.graphml"
 - Use yED or another graph editor to make your Video Map.

Usage:
"python imgsToGraph.py -o OUTPUT.graphml"

------------------------------
makeJson.py:
This takes a GraphML file as input, checks it for Video Map completeness and converts it to Video Map JSON.

Usage:
"python makeJson.py -i INFILE -o OUTFILE"