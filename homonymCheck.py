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

homonymsList = []
with open('homonyms.csv') as file:
    for row in csv.reader(file, delimiter = ','):
        for item in row:
            homonymsList.append(item)

f = csv.writer(open('listSubjectsToCheckAgainstFASTAndMESH_Batch'+batch+'2.csv', 'w'))
f.writerow(['uri']+['dc.subject']+['cleanedSubject']+['homonym'])

total = 0
with open(filename) as itemMetadataFile:
        itemMetadata = csv.DictReader(itemMetadataFile)
        for row in itemMetadata:
            uri = row['uri']
            dc_subject = row['dc.subject']
            cleanedSubject = row['cleanedSubject']
            newValue = cleanedSubject.lower()
            if newValue in homonymsList:
                f.writerow([uri]+[dc_subject]+[cleanedSubject]+['yes'])
                print(cleanedSubject)
                total = total + 1
            else:
                f.writerow([uri]+[dc_subject]+[cleanedSubject])
print(total)
