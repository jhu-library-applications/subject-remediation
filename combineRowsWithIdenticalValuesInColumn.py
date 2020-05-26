import pandas as pd
import csv
import argparse
import chardet
import re
from datetime import datetime

pd.__version__
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
parser.add_argument('-b', '--batch', help='Batch letter to name outputs')
parser.add_argument('-k', '--element')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')
if args.batch:
    batch = args.batch
else:
    batch = input('Enter batch letter:')
if args.element:
    element = args.element
else:
    element = input('Enter element: ')


def find_encoding(fname):
    r_file = open(fname, 'rb').read()
    result = chardet.detect(r_file)
    charenc = result['encoding']
    return charenc


my_encoding = find_encoding(filename)
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')

print(my_encoding)
df = pd.read_csv(filename, encoding=my_encoding)

print(df.head())
# Combine identical element values from different rows into one row.
# In that row create column with list of URI associated with that value.
pivoted = pd.pivot_table(df, index=[element], values='uri', aggfunc=lambda x: ','.join(str(v) for v in x))
print(pivoted.sort_values(ascending=True, by=element).head())

df = pd.DataFrame(pivoted)
df = df.reset_index()

#  df = df.drop(columns='uri') #  If you want to drop a column.
df['newValue'] = df[element]  # duplicate column with element
df['category'] = ''  # add blank column called Category
df = df[df[element] != 'en_US']
print(df.head())


df.to_csv('newData_'+dt+'.csv')

# Do basic remediation on newValue column.
# Get rid of extra spaces, all quotes, capitalize first letter in string.
f = csv.writer(open('00_deDuplicatedSubjects_Batch'+batch+'_'+dt+'.csv', 'w'))
f.writerow(['uri']+[element]+['newValue']+['category'])

with open('newData.csv') as itemMetadataFile:
    itemMetadata = csv.DictReader(itemMetadataFile, restval='index')
    for row in itemMetadata:
        uri = row['uri']
        type = row['dc.type']
        original_element = row[element]
        newValue = row['newValue']
        category = row['category']
        match = re.search(r'^[a-z]', newValue)
        try:
            newValue = newValue.strip()
        except ValueError:
            pass
        try:
            newValue = newValue.replace("  ", " ")  # removes extra blanks
            print(newValue)
        except ValueError:
            pass
        try:
            if newValue.find('\"') != -1:
                newValue = newValue.replace('\"', '')  # delete quote marks
                print(newValue)
        except ValueError:
            pass
        try:
            if match:
                newValue = newValue[:1].upper() + newValue[1:]  # capitalize first letter in first word
                print(newValue)
        except ValueError:
            pass
        f.writerow([uri]+[original_element]+[newValue]+[category])
