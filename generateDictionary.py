import json
from io import BytesIO
import zipfile

dataset = 'Events-170301.zip'
path="C:\\Users\\ASUS\\Documents\\msr\\AttributeDicts\\"
dictList=dict()
#dictIndex=0
timeAttributes=['Targets-StartedAt','Actions-ExecutedAt','Duration','Selections-SelectedAfter','Targets-Duration']

def traverseIt(key,attrName,attributes): #apply for every key of jsonFile
    if type(key) is dict and attrName!="Context2":
        for k in key.keys():
            traverseIt(key[k],attrName+"_"+k,attributes)
    elif type(key) is list:
        for i in range(len(key)):
            if type(key[i]) is dict:
                for k in key[i].keys():
                    traverseIt(key[i][k],attrName+"-"+k,attributes)
    else:
        if attrName != "TriggeredAt" and attrName != "Context2":
            attributes.add(attrName)

def generateDictionaries():
    with zipfile.ZipFile(dataset, "r") as zfile:
        with open("attributes.txt","r") as attfile:
            for line in attfile:
                line=line[:len(line)-1]
                attrDict=dict()
                if line=='Reason':
                    with open(path + line + ".txt", "w") as attributeFile:
                        index=0
                        for name in zfile.namelist():
                            if name.endswith('.zip'):
                                zfiledata = BytesIO(zfile.read(name))
                                with zipfile.ZipFile(zfiledata) as zfile2:
                                    for filename2 in zfile2.namelist():
                                        if filename2.endswith('.json'):
                                            with zfile2.open(filename2) as f:
                                                jsonFile = json.load(f)
                                                if "DebuggerEvent" in jsonFile['$type']:
                                                    attributes=set()
                                                    for key in jsonFile.keys(): #get all attributes from json file
                                                        if key=="Action":
                                                            if "DebuggerEvent" in jsonFile['$type']:
                                                                traverseIt(jsonFile[key], "Debugger,"+key, attributes)
                                                            elif "SolutionEvent" in jsonFile['$type']:
                                                                traverseIt(jsonFile[key], "Solution," + key, attributes)
                                                            elif "WindowEvent" in jsonFile['$type']:
                                                                traverseIt(jsonFile[key], "Window," + key, attributes)
                                                            elif "DocumentEvent" in jsonFile['$type']:
                                                                traverseIt(jsonFile[key], "Document," + key, attributes)
                                                            else:
                                                                traverseIt(jsonFile[key], "Build," + key, attributes)
                                                        else:
                                                            traverseIt(jsonFile[key],key,attributes)
                                                    if line in attributes: #if line is among those attributes
                                                        print line
                                                        if "-" not in line and "_" not in line: #if line is a single attribute
                                                            try:
                                                                key=""
                                                                if ",Action" in line:
                                                                    key=jsonFile['Action'].encode('utf8')
                                                                else:
                                                                    if not isinstance(jsonFile[line],basestring):
                                                                        key=str(jsonFile[line])
                                                                    else:
                                                                        key=jsonFile[line].encode('utf8')
                                                                if not attrDict.has_key(key):
                                                                    attrDict[key] = index
                                                                    attributeFile.write(str(index) + "\t" + key + "\n")
                                                                    index += 1
                                                            except UnicodeEncodeError:
                                                                print name
                                                                print filename2
                                                                print key
                                                        else:
                                                            elements=line.split("-")
                                                            val=""
                                                            for i in range(len(jsonFile[elements[0]])): #for each element in the list
                                                                if "_" not in elements[1]: #the next element is not a dictionary
                                                                    val=jsonFile[elements[0]][i][elements[1]]
                                                                else: #the next element is a dictionary
                                                                    dictElements=elements[1].split("_")
                                                                    val=jsonFile[elements[0]][i][dictElements[0]][dictElements[1]]
                                                                try:
                                                                    key=""
                                                                    if not isinstance(val, basestring):
                                                                        key = str(val)
                                                                    else:
                                                                        key = val.encode('utf8')
                                                                    if not attrDict.has_key(key): #val is not in dictionary
                                                                        attrDict[key]=index
                                                                        attributeFile.write(str(index)+"\t"+key+"\n")
                                                                        index+=1
                                                                except UnicodeEncodeError:
                                                                    print name
                                                                    print filename2
                                                                    print key
                            #dictList[line] = attrDict

generateDictionaries()


