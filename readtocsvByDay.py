
import json
from io import BytesIO
import zipfile
import time
import numpy

dataset = 'Events-170301.zip'
day=""
event= dict()
successCounter=0
failedCounter=0
errorCounter=0
ignoreCounter=0
foundOne=False #whether that day already counts as having a test
eventHeader=['ActivityEvent','CommandEvent','CompletionEvent','BuildEvent','DebuggerEvent','DocumentEvent','EditEvent','FindEvent','IDEStateEvent'
             ,'SolutionEvent','WindowEvent','VersionControlEvent','UserProfileEvent','NavigationEvent','SystemEvent']
data=[]
row = []
foundOne=False

with zipfile.ZipFile(dataset, "r") as zfile:
    for name in zfile.namelist():
        if name.endswith('.zip'):
            zfiledata = BytesIO(zfile.read(name))
            with zipfile.ZipFile(zfiledata) as zfile2:
                for filename2 in zfile2.namelist():
                    if filename2.endswith('.json'):
                        with zfile2.open(filename2) as f:
                            jsonFile = json.load(f)
                            if "TestRunEvent" in jsonFile['$type']: #and jsonFile['WasAborted']==False:
                                if foundOne==True:
                                    for type in eventHeader:  # these are non-test events after the latest test event
                                        if type in event and event[type] >= 1:
                                            row.append(str(event[type]))
                                            #event[type] = 0
                                        else:
                                            row.append("0")
                                    data.append(row)
                                row = []
                                foundOne = False
                                row.append(str(name))  #the path name of the file, which identifies user
                                row.append(str(filename2)) #name of test event
                                row.append(str(jsonFile['TriggeredAt'])) # datetime of test event
                                if foundOne==False:
                                    foundOne=True
                                if str(jsonFile['TriggeredAt'])[:10] != day:
                                    day=str(jsonFile['TriggeredAt'])[:10]
                                    for type in eventHeader:
                                        row.append("0") #no non-test events before this in the day
                                else:
                                    for type in eventHeader:  # these are non-test events before the test in the same day
                                        if type in event and event[type] >= 1:
                                            row.append(str(event[type]))
                                            event[type] = 0
                                        else:
                                            row.append("0")

                                for test in jsonFile['Tests']:
                                    if test['Result'] == 1:
                                        successCounter+=1
                                    elif test['Result'] == 2:
                                        failedCounter+=1
                                    elif test['Result'] == 3:
                                        errorCounter+=1
                                    elif test['Result'] ==4:
                                        ignoreCounter+=1
                                row.append(str(successCounter))
                                row.append(str(failedCounter))
                                row.append(str(errorCounter))
                                row.append(str(ignoreCounter))
                                successCounter=0
                                failedCounter=0
                                errorCounter=0
                                ignoreCounter=0
                            else:
                                if day!="":
                                    if str(jsonFile['TriggeredAt'])[:10]==day:
                                        for type in eventHeader:
                                            if type in jsonFile['$type']:
                                                try:
                                                    event[type]=event[type]+1
                                                except:
                                                    event[type] = 1
                                                break
                                    else: #start of a new day. Restart the event dict to store events of new day
                                        if foundOne == True:
                                            for type in eventHeader: #these are non-test events after the latest test event
                                                if type in event and event[type]>=1:
                                                    row.append(str(event[type]))
                                                    event[type] = 0
                                                else:
                                                    row.append("0")
                                            data.append(row)
                                        else:
                                            for type in eventHeader:
                                                if type in event:
                                                    event[type]=0
                                        foundOne=False
                                        day=str(jsonFile['TriggeredAt'])[:10]
                                        row=[]
                                else:
                                    day=str(jsonFile['TriggeredAt'])[:10]
                                    for type in eventHeader:
                                        if type in jsonFile['$type']:
                                            try:
                                                event[type] = event[type] + 1
                                            except:
                                                event[type] = 1
                                            break
    """for row in data:
        event=""
        for cell in row:
            event+=cell+","
        print event"""
    header="User,TestEvent,Time,"
    for type in eventHeader:
        header+=type+"Before,"
    header+="Success,Failed,Error,Ignored,"
    for type in eventHeader:
        header+=type+"After,"
    numpy.savetxt("test.csv",numpy.array(data),fmt="%s",delimiter=',',newline='\n',header=header)










