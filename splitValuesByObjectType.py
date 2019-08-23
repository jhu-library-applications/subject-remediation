import csv
import argparse
from datetime import datetime
import ast
batch = "A"
f3 = csv.writer(open('subjectsToUpload'+'_Batch'+batch+'_'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'w'))
f3.writerow(['oldKey']+['oldSubject']+['newKey']+['newSubject'])

f4 = csv.writer(open('subjectsToSplitAndUpload'+'_Batch'+batch+'_'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'w'))
f4.writerow(['oldKey']+['oldSubject']+['newKey']+['newSubject'])


subjectFile = 'subjects'+'_Batch'+batch+'.csv'

with open(subjectFile) as itemMetadataFile3:
    itemMetadata = csv.DictReader(itemMetadataFile3)
    for row in itemMetadata:
        oldKey = row['oldKey']
        oldSubject = row['oldSubject']
        newKey = row['newKey']
        newSubject = row['newSubject']
        try:
            newSubject= ast.literal_eval(newSubject)
            if isinstance(newSubject, list):
                print(len(newSubject))
                if len(newSubject) == 1:
                    newSubject = newSubject[0]
                    print(newSubject)
                    f3.writerow([oldKey]+[oldSubject]+[newKey]+[newSubject])
                else:
                    f4.writerow([oldKey]+[oldSubject]+[newKey]+[newSubject])
        except:
            if isinstance(newSubject, str):
                f3.writerow([oldKey]+[oldSubject]+[newKey]+[newSubject])
            else:
                print("oh no!")
