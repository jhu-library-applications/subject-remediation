import csv
import argparse
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='enter filename with csv extension.')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')


homonymsList = []
with open('./reference_lists/homonyms_list.csv') as file:
    for row in csv.reader(file, delimiter=','):
        for item in row:
            homonymsList.append(item)

filenamePart = filename[:-4]
print(filenamePart)

dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')


f = csv.writer(open(filenamePart+'WithHC_'+dt+'.csv', 'w'))
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
print('homonyms found: '+str(total))
