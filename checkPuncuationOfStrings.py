import csv
import argparse
import re
from spellchecker import SpellChecker
from datetime import datetime

spell = SpellChecker()
spell.word_frequency.load_text_file('./reference_lists/MESH_list.txt')
spell.word_frequency.load_text_file('./reference_lists/FAST_list.txt')


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

dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')

f = csv.writer(open('02_deDuplicatedSubjects_Batch'+batch+'_'+dt+'.csv', 'w'))
f.writerow(['uri']+['dc.subject']+['newValue']+['check']+['category'])

match1Comma_count = 0
list_count = 0
matchPeriods_count = 0
matchColons_count = 0
# spelling_count = 0
newLines_count = 0
with open(filename) as itemMetadataFile:
    itemMetadata = csv.DictReader(itemMetadataFile)
    for row in itemMetadata:
        uri = row['uri']
        dc_subject = row['dc.subject']
        newValue = row['newValue']
        category = row['category']
        newValueList = newValue.split(" ")
#  find all commas in string and put into list
        matchCommas = re.findall(r',', newValue)
#  find all periods in string and put into list
        matchPeriods = re.findall(r'\.', newValue)
#  find all colons in string and put into list
        matchColons = re.findall(r':', newValue)
#  find all newlines in string and put into list
        matchNewLines = re.findall(r'(\n|\r\n)', newValue)
        # spelling = spell.unknown(newValueList)
        # spelling = len(spelling)
        # if spelling > 0:
        #     moreSpelling = spell.unknown(newValue)
        #     moreSpelling = len(moreSpelling)
        #     if moreSpelling == 0:
        #         spelling = 0
        #     else:
        #         pass
        # else:
        #     pass
        #  find the total number of newlines in string
        matchNewLines = len(matchNewLines)
        #  find the total number of periods in string
        matchPeriods = len(matchPeriods)
        #  find the total number of commas in string
        matchCommas = len(matchCommas)
        #  find the total number of colons in string
        matchColons = len(matchColons)
        if matchCommas >= 2:
            list_count = list_count + 1
            f.writerow([uri]+[dc_subject]+[newValue]+['no']+['list'])
        elif matchCommas == 1:
            match1Comma_count = match1Comma_count + 1
            f.writerow([uri]+[dc_subject]+[newValue]+['yes']+[category])
        elif matchNewLines >= 2:
            newLines_count = newLines_count + 1
            f.writerow([uri]+[dc_subject]+[newValue]+['no']+['list'])
        elif matchPeriods > 0:
            matchPeriods_count = matchPeriods_count + 1
            f.writerow([uri]+[dc_subject]+[newValue]+['yes']+[category])
        elif matchColons > 0:
            matchColons_count = matchColons_count + 1
            f.writerow([uri]+[dc_subject]+[newValue]+['no']+['bad'])
        # elif spelling > 0:
        #     spelling_count = spelling_count + 1
        #     f.writerow([uri]+[dc_subject]+[newValue]+['yes']+[category])
        else:
            f.writerow([uri]+[dc_subject]+[newValue]+['no']+[category])


print('commas: '+str(match1Comma_count))
print('list: '+str(list_count))
print('periods: '+str(matchPeriods_count))
print('colons: '+str(matchColons_count))
# print('misspelled: '+str(spelling_count))
print('new lines: '+str(newLines_count))
