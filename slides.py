#!/usr/bin/env python3.9

import os
import random

from flask import Flask, Response, abort

from diagrams import Diagram, Edge
from diagrams.aws.compute import EC2
# from diagrams.aws.database import RDS
from diagrams.aws.network import ELB
from diagrams.aws.storage import SimpleStorageServiceS3 
from diagrams.onprem.client import Users
from diagrams.onprem.monitoring import Splunk
from diagrams.generic.network import Firewall

from diagrams.onprem.compute import Server

DIAGRAM_ATTR = {
    "fontsize": "45",
    "bgcolor": "#999999",
    "margin" : "0.0!",
    "size" : "20!",
}

COMMON_NODE_ATTR = {
    "fontsize" : "35",
    # "fixedsize": "true",            # true | false
    # "imagescale": "true",           # true | false | width | height | both 
    # "labelloc":"b",                 # t | c | b
    # "penwidth": "0",
    "width": "1.5",
    "height": "3.0",
    # "margin" : "1.5"
}

def get_diagram_edge():
    return Edge(color="white", penwidth="5")

def workflow_final():
    with Diagram("",
                 outformat='png',
                 filename='images/diagrams/workflow_final',
                 show=False,
                 graph_attr=DIAGRAM_ATTR,
                 node_attr={'margin' : "5",}
                #  direction="TB",
                 ):
        Users(f'"{random.randrange(0,1000)} Hackers"', **COMMON_NODE_ATTR) \
                >> get_diagram_edge() \
                >> [
                    EC2("server", **COMMON_NODE_ATTR),
                    EC2("server", **COMMON_NODE_ATTR),
                    EC2("server", **COMMON_NODE_ATTR),
                    ] \
                >> get_diagram_edge() \
                >> Splunk("", **COMMON_NODE_ATTR) \
                >> get_diagram_edge() \
                >> SimpleStorageServiceS3("Public S3 Bucket", **COMMON_NODE_ATTR) \
                >> get_diagram_edge() \
                << EC2("server", **COMMON_NODE_ATTR) \
                >> get_diagram_edge() \
                >> Firewall("IPTables", fillcolor='red', **COMMON_NODE_ATTR)

def return_mimetype(path):
    mimetype = 'text/html'
    if path.endswith('.css'):
        mimetype = 'text/css'
    elif path.endswith('.js'):
        mimetype = "application/javascript"
    elif path.endswith('.png'):
        mimetype = "image/png"
    return mimetype


app = Flask(__name__)

@app.route('/')
def hello_world():
    with open('index.html') as indexfile:
        filecontents = indexfile.read()
    with open('slides.md') as slidefile:
        slidecontents = slidefile.read()
    return filecontents.replace('#REPLACEMEWITHSLIDES#', slidecontents)

@app.route("/images/diagrams/<string:filename>")
def diagrams(filename):
    #if os.path.exists(path):
    if filename == 'workflow_final.png':
        print("regenerating workflow image")
        if os.path.exists("images/diagrams/workflow_final.png"):
            try:
                os.unlink("images/diagrams/workflow_final.png")
            except Exception as error_message:
                print(f"Whoops while trying to unlink images/diagrams/workflow_final.png: {error_message}")
        workflow_final()
    else:
        return abort(404)
    
    filecontents = open(f"./images/diagrams/{filename}", 'rb').read()
    mimetype = return_mimetype(filename)
    return Response(filecontents, mimetype=mimetype)
    

@app.route("/<path:path>")
def static_files(path):
    if os.path.exists(path):
        filecontents = open(f"./{path}", 'rb').read()
        mimetype = return_mimetype(path)
        return Response(filecontents, mimetype=mimetype)
    elif path in ("favicon.ico", "apple-touch-icon.png" ):
        return Response("", mimetype='image/ico')
    else:
        return abort(404)


app.run(debug=True)
