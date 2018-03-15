import json
from io import BytesIO
import zipfile
import numpy
import os
import gzip
import sys
import cPickle


dataset = 'Events-170301.zip'
dictPath='C:\\Users\\ASUS\\Documents\\msr\\AttributeDicts\\'
methodPath='C:\\Users\\ASUS\\Documents\\msr\\TestAttributeDicts\\Tests-TestMethod.txt'

usersWithTests={"Events-170301-2/2016-05-09/1.zip":277675,"Events-170301-2/2016-05-09/10.zip":1317,"Events-170301-2/2016-05-10/1.zip":1211,"Events-170301-2/2016-05-11/10.zip":1961,
                "Events-170301-2/2016-05-11/27.zip":2178,"Events-170301-2/2016-05-12/0.zip":246,"Events-170301-2/2016-06-14/10.zip":11,"Events-170301-2/2016-06-16/1.zip":2,
                "Events-170301-2/2016-07-01/10.zip":6,"Events-170301-2/2016-07-12/0.zip":2610,"Events-170301-2/2016-08-02/0.zip":1,"Events-170301-2/2016-08-03/25.zip":73,
                "Events-170301-2/2016-08-18/159.zip":36995,"Events-170301-2/2016-08-25/0.zip":15,"Events-170301-2/2016-08-31/101.zip":124,"Events-170301-2/2016-09-13/2.zip":133,
                "Events-170301-2/2016-09-26/100.zip":7,"Events-170301-2/2016-09-28/11.zip":2122,"Events-170301-2/2016-09-29/28.zip":1596,"Events-170301-2/2016-12-01/1.zip":6529,
                "Events-170301-2/2016-12-19/13.zip":1096,"Events-170301-2/2016-12-24/10.zip":1004,"Events-170301-2/2017-01-10/1.zip":407,"Events-170301-2/2017-01-16/0.zip":60}

data=[] #contains all the sequences
outcomes=[] #contains the test results corresponding to the sequences
eSequence=[] #sequence of events, each event is a vector

events=[] #contains the events of the current session
allEvents=[] #contains the events of all sessions
currentSession=""
methods=dict()

dictList=dict()
testsWithNoEvents=0

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


dictFile=gzip.open('AllDictionaries.pkl.gz','rb')
dictList=cPickle.load(dictFile)

with open(methodPath,'r') as methodFile: #put the methods in the method dictionary
    lines=methodFile.readlines()
    pairs = []
    elements = []
    for i in range(len(lines)):
        if "\t" in lines[i]:
            elements=lines[i].split("\t")
            if i+1 < len(lines) and "\t" not in lines[i+1]:
                elements[1]+=lines[i+1]
            elements[1] = elements[1][:-1]
            pairs.append(elements)
            elements=[]
    for pair in pairs:
        methods[str(pair[1])]=int(pair[0])

methodF=gzip.open('Methods.pkl.gz','wb')
cPickle.dump(methods,methodF,-1)
methodF.close()

with zipfile.ZipFile(dataset, "r") as zfile:
    for name in zfile.namelist():
        if name.endswith('.zip') and name in usersWithTests.keys(): #for each user
            zfiledata = BytesIO(zfile.read(name))
            with zipfile.ZipFile(zfiledata) as zfile2:
                testNumber = 0
                allEvents.extend(events)
                events = []
                currentSession=""
                for filename2 in zfile2.namelist():
                    if filename2.endswith('.json'):
                        with zfile2.open(filename2) as f:
                            jsonFile = json.load(f)
                            if "TestRunEvent" in jsonFile['$type'] and jsonFile['WasAborted']==False:
                                if currentSession != str(jsonFile['IDESessionUUID']): #if test event begins a new IDESession
                                    if currentSession=="":
                                        for test in jsonFile['Tests']:
                                            outcomes.append(test['Result'])
                                            eSequence.append(methods[str(test['TestMethod'])]) #append the ID of the test method
                                            eventIndex = 0
                                            for i in range(len(events)):
                                                if dictList['IDESessionUUID'][currentSession] == events[i][0]:
                                                    eSequence.append(len(allEvents) + i)  # add the event index in events[] to the sequence. This is unique in each session
                                                    eventIndex += 1
                                            if eventIndex == 0:
                                                testsWithNoEvents += 1
                                            data.append(eSequence)  # add the sequence to the data matrix
                                            eSequence = []
                                            testNumber+=1
                                    else:
                                        allEvents.extend(events)
                                        events=[]
                                        for test in jsonFile['Tests']:
                                            outcomes.append(test['Result'])
                                            eSequence.append(methods[str(test['TestMethod'])])
                                            data.append(eSequence)
                                            eSequence=[]
                                            testNumber+=1
                                        testsWithNoEvents+=1
                                    currentSession=str(jsonFile['IDESessionUUID'])
                                else:
                                    for test in jsonFile['Tests']:
                                        outcomes.append(test['Result']) #add the result of the corresponding test
                                        eSequence.append(methods[str(test['TestMethod'])])
                                        eventIndex = 0
                                        for i in range(len(events)):
                                            if dictList['IDESessionUUID'][currentSession]==events[i][0]:
                                                eSequence.append(len(allEvents)+i) #add the event index in events[] to the sequence. This is unique in each session
                                                eventIndex+=1
                                        if eventIndex == 0:
                                            testsWithNoEvents += 1
                                        data.append(eSequence) #add the sequence to the data matrix
                                        eSequence=[]
                                        testNumber+=1
                                if testNumber==usersWithTests[name]: #this is the last test event of this user
                                    break
                                else: #More test events to come
                                    allEvents.extend(events)
                                    events=[]
                            else: #convert non-test events to vector
                                if currentSession!="" and str(jsonFile['IDESessionUUID'])!=currentSession:
                                    allEvents.extend(events)
                                    events=[]
                                    currentSession=str(jsonFile['IDESessionUUID'])
                                else:
                                    currentSession=str(jsonFile['IDESessionUUID'])

                                eventVector = []
                                eventVector.append(dictList['IDESessionUUID'][str(jsonFile['IDESessionUUID'])])
                                if "Context2" in jsonFile.keys():
                                    if "SST" in jsonFile['Context2']:
                                        eventVector.append(1)
                                    else:
                                        eventVector.append(0)
                                    if "TypeShape" in jsonFile['Context2']:
                                        eventVector.append(1)
                                    else:
                                        eventVector.append(0)
                                eAttributes=set()
                                for key in jsonFile.keys():
                                    if key == "Action":
                                        if "DebuggerEvent" in jsonFile['$type']:
                                            traverseIt(jsonFile[key], "Debugger," + key, eAttributes)
                                        elif "SolutionEvent" in jsonFile['$type']:
                                            traverseIt(jsonFile[key], "Solution," + key, eAttributes)
                                        elif "WindowEvent" in jsonFile['$type']:
                                            traverseIt(jsonFile[key], "Window," + key, eAttributes)
                                        elif "DocumentEvent" in jsonFile['$type']:
                                            traverseIt(jsonFile[key], "Document," + key, eAttributes)
                                        else:
                                            traverseIt(jsonFile[key], "Build," + key, eAttributes)
                                    else:
                                        traverseIt(jsonFile[key], key, eAttributes)
                                for attribute in sorted(dictList.keys()):
                                    if attribute in eAttributes:
                                        if attribute!='IDESessionUUID':
                                            if "-" not in attribute and "_" not in attribute:
                                                if ",Action" in attribute:
                                                    eventVector.append(dictList[attribute][str(jsonFile['Action'])])
                                                else:
                                                    if isinstance(jsonFile[attribute],basestring):
                                                        eventVector.append(dictList[attribute][jsonFile[attribute].encode('utf8')])
                                                    else:
                                                        eventVector.append(
                                                            dictList[attribute][str(jsonFile[attribute])])
                                            else:
                                                elements = attribute.split("-")
                                                val = ""
                                                for i in range(len(
                                                        jsonFile[elements[0]])):  # for each element in the list
                                                    if "_" not in elements[1]:  # the next element is not a dictionary
                                                        val = jsonFile[elements[0]][i][elements[1]]
                                                    else:  # the next element is a dictionary
                                                        dictElements = elements[1].split("_")
                                                        val = jsonFile[elements[0]][i][dictElements[0]][
                                                            dictElements[1]]
                                                    if not isinstance(val, basestring):
                                                        eventVector.append(dictList[attribute][str(val)])
                                                    else:
                                                        eventVector.append(dictList[attribute][val.encode('utf8')])
                                    else:
                                        eventVector.append(-1)
                                if eventVector not in events:
                                    events.append(eventVector)
                                

    #numpy.savetxt("testRelated.csv", numpy.array(data), fmt="%s", delimiter=",", newline='\n')
    print("Tests with no events: "+str(testsWithNoEvents))
    print len(allEvents)
    print len(data)
    print len(outcomes)

    f=gzip.open('Data1.pkl.gz','wb')
    cPickle.dump((allEvents,data,outcomes),f,-1)
    f.close()











