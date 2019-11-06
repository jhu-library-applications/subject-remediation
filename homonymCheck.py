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
total = 0
print(homonymsList)
with open(filename) as itemMetadataFile:
        itemMetadata = csv.DictReader(itemMetadataFile)
        for row in itemMetadata:
            newValue = row['newValue'].lower()
            newValueList = newValue.split(" ")
            if newValue in homonymsList:
                print(newValue)
                total = total + 1
            else:
                pass
print(total)
