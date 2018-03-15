import json
from io import BytesIO
import zipfile
import numpy

dataset = 'Events-170301.zip'
"""row=[]
data=[]

eventTypes=dict()"""
attributes=set()

def traverseIt(key,attrName): #apply for every key of jsonFile
    if type(key) is dict and attrName!="Context2": #exclude SST and TypeShape
        for k in key.keys():
            traverseIt(key[k],attrName+"_"+k)
    elif type(key) is list:
        for i in range(len(key)):
            if type(key[i]) is dict:
                for k in key[i].keys():
                    traverseIt(key[i][k],attrName+"-"+k)
    else:
        if attrName != "TriggeredAt" and attrName != "Context2":
            attributes.add(attrName)

with zipfile.ZipFile(dataset, "r") as zfile:
    for name in zfile.namelist():
        if name.endswith('.zip'):
            zfiledata = BytesIO(zfile.read(name))
            with zipfile.ZipFile(zfiledata) as zfile2:
                for filename2 in zfile2.namelist():
                    if filename2.endswith('.json'):
                        with zfile2.open(filename2) as f:
                            jsonFile = json.load(f)
                            for key in jsonFile.keys():
                                if key == "Action":
                                    if "DebuggerEvent" in jsonFile['$type']:
                                        traverseIt(jsonFile[key], "Debugger," + key, attributes)
                                    elif "SolutionEvent" in jsonFile['$type']:
                                        traverseIt(jsonFile[key], "Solution," + key, attributes)
                                    elif "WindowEvent" in jsonFile['$type']:
                                        traverseIt(jsonFile[key], "Window," + key, attributes)
                                    elif "DocumentEvent" in jsonFile['$type']:
                                        traverseIt(jsonFile[key], "Document," + key, attributes)
                                    else:
                                        traverseIt(jsonFile[key], "Build," + key, attributes)
                                else:
                                    traverseIt(jsonFile[key], key, attributes)


with open("attributes.txt","w") as file:
    for attr in sorted(attributes):
        file.write(attr+"\n")
