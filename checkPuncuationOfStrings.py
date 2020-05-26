import csv
import argparse
import re
from datetime import datetime
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='enter filename with csv.')
parser.add_argument('-b', '--batch', help='Batch letter to name outputs.')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')

if args.batch:
    batch = args.batch
else:
    batch = input('Enter batch letter: ')


def findError(search, value):
    newList = re.findall(search, newValue)
    errorCount = len(newList)
    return errorCount


def findCategory(errorCount, threshold, type):
    if errorCount >= threshold:
        newDict['category'] = type
    else:
        pass


def manuallyCheck(errorCount, threshold):
    if errorCount >= threshold:
        newDict['check'] = 'yes'
    else:
        pass


all_items = []
with open(filename) as itemMetadataFile:
    itemMetadata = csv.DictReader(itemMetadataFile)
    for row in itemMetadata:
        uri = row['uri']
        oldValue = row['dc.subject']
        newValue = row['newValue']
        category = row['category']
        newDict = {'uri': uri, 'dc.subject': oldValue, 'newValue': newValue}
        newDict['check'] = 'no'
        newDict['category'] = category
        matchCommas = findError(r',', newValue)
        matchNewLines = findError(r'(\n|\r\n)', newValue)
        matchPeriods = findError(r'\.', newValue)
        matchColons = findError(r':', newValue)
        findCategory(matchCommas, 2, 'list')
        findCategory(matchNewLines, 2, 'list')
        findCategory(matchColons, 1, 'bad')
        manuallyCheck(matchPeriods, 1)
        if matchCommas == 1:
            newDict['check'] = 'yes'
        else:
            pass
        all_items.append(newDict)

df = pd.DataFrame.from_dict(all_items)
check_counts = df.check.value_counts(dropna=False)
cat_counts = df.category.value_counts(dropna=False)
print(check_counts)
print(cat_counts)
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
newFile = '02_deDuplicatedSubjects_Batch'+batch+'_'+dt+'.csv'
df.to_csv(path_or_buf=newFile, index=False)
