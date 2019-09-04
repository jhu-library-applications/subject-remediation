import csv
import argparse
from datetime import datetime
import ast

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='enter filename with csv. optional - if not provided, the script will ask for input')
parser.add_argument('-f2', '--file2', help='enter filename with csv. optional - if not provided, the script will ask for input')
parser.add_argument('-b', '--batch', help='Batch letter to name outputs. optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')
if args.file2:
    filename2 = args.file2
else:
    filename2 = input('Enter second filename (including \'.csv\'): ')
if args.batch:
    batch = args.batch
else:
    batch = input('Enter batch letter: ')

subjectFile = 'subjectsCombined'+'_Batch'+batch+'_'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv'
print(subjectFile)

f = csv.writer(open(subjectFile, 'w'))
f.writerow(['oldKey']+['oldSubject']+['newKey']+['newSubject'])

f2 = csv.writer(open('errors'+'_Batch'+batch+'_'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'w'))
f2.writerow(['oldSubject']+['cleanedSubject']+['results']+['selection'])

error = 0

with open(filename) as itemMetadataFile:
    itemMetadata = csv.DictReader(itemMetadataFile)
    for row in itemMetadata:
        oldKey = 'dc.subject'
        oldSubject = row['dc.subject']
        cleanedSubject = row['cleanedSubject']
        results = row['results'].strip()
        selection = row['selection'].strip()
        try:
            selection = int(selection)
        except:
            selection = selection
        newKey = ''
        newSubject = ''
        if results == 'FASTmatch':
            newSubject = cleanedSubject
            newKey = 'dc.subject.fast'
            f.writerow([oldKey]+[oldSubject]+[newKey]+[newSubject])
        elif results != 'FASTmatch' and isinstance(selection, int):
            results = ast.literal_eval(results)
            selection = selection - 1
            newSubject = results[selection]
            newKey = 'dc.subject.fast'
            f.writerow([oldKey]+[oldSubject]+[newKey]+[newSubject])
        elif results != 'FASTmatch' and selection == 'none':
            newSubject = cleanedSubject
            newKey = 'dc.subject'
            f.writerow([oldKey]+[oldSubject]+[newKey]+[newSubject])
        else:
            print('Error found')
            error = error + 1
            f2.writerow([oldSubject]+[cleanedSubject]+[results]+[selection])

with open(filename2) as itemMetadataFile2:
    itemMetadata = csv.DictReader(itemMetadataFile2)
    for row in itemMetadata:
        oldKey = 'dc.subject'
        oldSubject = row['dc.subject']
        cleanedSubject = row['cleanedSubject']
        results = row['results'].strip()
        selection = row['selection'].strip()
        newKey = ''
        newSubject = ''
        if selection == 'x':
            newKey = 'dc.subject.fast'
            newSubject = results
            f.writerow([oldKey]+[oldSubject]+[newKey]+[newSubject])
        elif selection == 'none':
            newKey = 'dc.subject'
            newSubject = cleanedSubject
            f.writerow([oldKey]+[oldSubject]+[newKey]+[newSubject])
        else:
            print('Error found')
            error = error + 1
            f2.writerow([oldSubject]+[cleanedSubject]+[results]+[selection])

print('{} errors found'.format(error))
