import csv
import argparse
from datetime import datetime
import ast


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='enter filename with csv. optional - if not provided, the script will ask for input')
parser.add_argument('-b', '--batch', help='Batch letter to name outputs. optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')

if args.batch:
    batch = args.batch
else:
    batch = input('Enter batch letter: ')


f3 = csv.writer(open('subjectsToUpload_Batch'+batch+'_'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'w'))
f3.writerow(['oldKey']+['oldSubject']+['newKey']+['newSubject'])

f4 = csv.writer(open('subjectsToSplitAndUpload_Batch'+batch+'_'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'w'))
f4.writerow(['oldKey']+['oldSubject']+['newKey']+['newSubject'])


with open(filename) as itemMetadataFile:
    itemMetadata = csv.DictReader(itemMetadataFile)
    for row in itemMetadata:
        oldKey = row['oldKey']
        oldSubject = row['oldSubject']
        newKey = row['newKey']
        newSubject = row['newSubject']
        try:
            newSubject = ast.literal_eval(newSubject)
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
