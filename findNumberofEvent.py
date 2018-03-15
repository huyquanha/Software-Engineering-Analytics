
import json
from io import BytesIO
import zipfile

# dataset = 'dataset/Events-170301.zip'
#
# event = dict()
#
# with zipfile.ZipFile(dataset, "r") as zfile:
#     zfile.printdir()
#     for name in zfile.namelist():
#         if name.endswith('.zip'):
#             zfiledata = BytesIO(zfile.read(name))
#             with zipfile.ZipFile(zfiledata) as zfile2:
#                 zfile2.printdir()
#                 for filename2 in zfile2.namelist():
#                     if filename2.endswith('.json'):
#                         with zfile2.open(filename2) as f:
#
#                             """You can add your script to extract information from Json files here."""
#                             """this is an example"""
#                             jsonFile = json.load(f)
#                             # print jsonFile['$type']  # print type of evente
#                             try:
#                                 event[jsonFile['$type']] =  event[jsonFile['$type']] + 1
#                             except:
#                                 event[jsonFile['$type']] = 1
#
#                             # print event
#
#
# with open('NumberofEvent.txt','w') as file:
#     file.write(json.dumps(event))
#
# print 'done'

dataset = 'Events-170301.zip'

event = dict()

with zipfile.ZipFile(dataset, "r") as zfile:
    zfile.printdir()
    for name in zfile.namelist():
        if name.endswith('.zip'):
            zfiledata = BytesIO(zfile.read(name))
            with zipfile.ZipFile(zfiledata) as zfile2:
                zfile2.printdir()
                for filename2 in zfile2.namelist():
                    if filename2.endswith('.json'):
                        with zfile2.open(filename2) as f:
                            """You can add your script to extract information from Json files here."""
                            """this is an example"""
                            jsonFile = json.load(f)
                            # print jsonFile['$type']  # print type of evente
                            try:
                                event[jsonFile['$type']] = event[jsonFile['$type']] + 1
                            except:
                                event[jsonFile['$type']] = 1

                            # print event

with open('NumberofEvent-context.txt','w') as file:
    file.write(json.dumps(event))

print ('done')