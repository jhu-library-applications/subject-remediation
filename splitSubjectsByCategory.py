import csv
import argparse

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

f = csv.writer(open('subjectsToCheckAgainstFAST_Batch'+batch+'.csv', 'w'))
f.writerow(['uri']+['dc.subject']+['cleanedSubject'])

f2 = csv.writer(open('manualFixes_Batch'+batch+'.csv', 'w'))
f2.writerow(['uri']+['dc.subject']+['cleanedSubject'])

row_count = 0
nonmanual_count = 0
manual_count = 0
with open(filename) as itemMetadataFile:
    itemMetadata = csv.DictReader(itemMetadataFile)
    for row in itemMetadata:
        row_count = row_count + 1
        uri = row['uri']
        dc_subject = row['dc.subject']
        newValue = row['newValue']
        category = row['category'].strip()
        if category == 'list':
            newValueList = newValue.split(',')
            newValueCount = len(newValueList)
            row_count = row_count + newValueCount
            for value in newValueList:
                f.writerow([uri]+[dc_subject]+[value])
                nonmanual_count = nonmanual_count + 1
        elif category == 'remove':
            newValue = newValue.replace('.', '')
            f.writerow([uri]+[dc_subject]+[newValue])
            nonmanual_count = nonmanual_count + 1
        elif category == 'bad':
            f2.writerow([uri]+[dc_subject]+[newValue])
            manual_count = manual_count + 1
        elif category == '?':
            f2.writerow([uri]+[dc_subject]+[newValue])
            manual_count = manual_count + 1
        else:
            f.writerow([uri]+[dc_subject]+[newValue])
            nonmanual_count = nonmanual_count + 1

print('total_row: '+str(row_count))
print('nonmanual_count: '+str(nonmanual_count))
print('manual_count: '+str(manual_count))
