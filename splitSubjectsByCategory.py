import csv
import argparse
import re

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

f = csv.writer(open('subjectsToCheckAgainstFASTAndMESH_Batch'+batch+'.csv', 'w'))
f.writerow(['uri']+['dc.subject']+['cleanedSubject'])

f2 = csv.writer(open('listSubjectsToCheckAgainstFASTAndMESH_Batch'+batch+'.csv', 'w'))
f2.writerow(['uri']+['dc.subject']+['cleanedSubject'])


row_count = 0
newrow_count = 0
expectedvalue_count = 0

with open(filename) as itemMetadataFile:
    itemMetadata = csv.DictReader(itemMetadataFile)
    for row in itemMetadata:
        row_count = row_count + 1
        uri = row['uri']
        dc_subject = row['dc.subject']
        newValue = row['newValue'].strip()
        category = row['category'].strip()
        if category == 'list':
            newValue = re.sub(',$', '', newValue) # removes comma from end of string
            if newValue.count(',') > 0:
                newValueList = newValue.split(',')
            elif newValue.count(r'(\n|\r\n)') > 0:
                newValueList = newValue.split(r'(\n|\r\n)')
            else:
                print("can't split!!")
                print(newValue)
            value_count = len(newValueList)
            expectedvalue_count = expectedvalue_count + value_count
            for value in newValueList:
                value = value.strip()
                f2.writerow([uri]+[dc_subject]+[value])
                newrow_count = newrow_count + 1
        elif category == 'remove':
            newValue = newValue.replace('.', '')
            f.writerow([uri]+[dc_subject]+[newValue])
        else:
            f.writerow([uri]+[dc_subject]+[newValue])

print('total_original_rows: '+str(row_count))
print('expected_count:'+str(expectedvalue_count))
print('newrow_count: '+str(newrow_count))
