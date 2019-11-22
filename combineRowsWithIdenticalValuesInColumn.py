import pandas as pd
import csv
import argparse
import chardet
import re

pd.__version__
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file')
parser.add_argument('-b', '--batch', help='Batch letter to name outputs. optional - if not provided, the script will ask for input')
parser.add_argument('-k', '--key')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')
if args.batch:
    batch = args.batch
else:
    batch = input('Enter batch letter:')
if args.key:
    key = args.key
else:
    key = input('Enter key: ')


def find_encoding(fname):
    r_file = open(fname, 'rb').read()
    result = chardet.detect(r_file)
    charenc = result['encoding']
    return charenc


my_encoding = find_encoding(filename)

print(my_encoding)
df = pd.read_csv(filename, encoding=my_encoding)

print(df.head())
# combine identicial key strings in different rows into one row; in that row create column with list of URI associated with that string
pivoted = pd.pivot_table(df, index=[key], values='uri', aggfunc=lambda x: ','.join(str(v) for v in x))
print(pivoted.sort_values(ascending=True, by=key).head())

df = pd.DataFrame(pivoted)
df = df.reset_index()

df = df.drop(columns='uri')
df['newValue'] = df[key]  # duplicate column with key
df['category'] = ''  # add blank column called Category

print(df.head())


df.to_csv('newData.csv')

# do basic remediation on newValue column -get rid of extra spaces, all quotes, and capitalize first letter in string
f = csv.writer(open('00_deDuplicatedSubjects'+batch+'.csv', 'w'))
f.writerow(['uri']+[key]+['newValue']+['category'])

with open('newData.csv') as itemMetadataFile:
    itemMetadata = csv.DictReader(itemMetadataFile)
    for row in itemMetadata:
        uri = row['uri']
        key = row['dc.type']
        newValue = row['newValue']
        category = row['category']
        match = re.search(r'^[a-z]', newValue)
        try:
            newValue = newValue.strip()
        except:
            pass
        try:
            if newValue.find("  ") != -1:
                newValue = newValue.replace("  ", " ")  # removes extra blanks
                print(newValue)
        except:
            pass
        try:
            if newValue.find('\"') != -1:
                newValue = newValue.replace('\"', '')  # delete quote marks
                print(newValue)
        except:
            pass
        try:
            if match:
                newValue = newValue[:1].upper() + newValue[1:]  # capitalize first letter in first word
                print(newValue)
        except:
            pass
        f.writerow([uri]+[key]+[newValue]+[category])
