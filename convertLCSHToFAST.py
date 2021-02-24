import requests
import csv
from datetime import datetime
from fuzzywuzzy import fuzz
import argparse
import ast
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='enter filename with csv.')
parser.add_argument('-b', '--batch', help='Batch letter & number of outputs.')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')

if args.batch:
    batch = args.batch
else:
    batch = input('Enter batch letter: ')

# Base URL for FAST API.
api_base_url = "http://fast.oclc.org/searchfast/fastsuggest"


def fastClose_function(subject):
    url = api_base_url + '?&query=' + subject
    url += '&queryIndex=suggestall&queryReturn=suggestall,idroot,auth,tag,raw&suggest=autoSubject&rows=3&wt=json'
    try:
        data = requests.get(url).json()
        for item in data:
            if item == 'response':
                response = data.get(item)
                if response.get('numFound') == 0:
                    pass
                else:
                    for metadata in response:
                        if metadata == 'docs':
                            keyInfo = response.get(metadata)
                            for info in keyInfo:
                                name = info.get('auth')
                                ratio = fuzz.token_sort_ratio(name, subject)
                                print('Options', name, ratio)
                                if name == subject:
                                    if name not in fast_list:
                                        fast_list.append(name)
                                        break
                                elif ratio == 100:
                                    if name not in fast_list:
                                        fast_list.append(name)
                                        break
                                elif ratio > 30:
                                    if name not in fast_list:
                                        fast_list.append(name)
                                else:
                                    pass
    except ValueError:
        pass


row_count = 0
convert_list = []
with open(filename) as itemMetadataFile:
    itemMetadata = csv.DictReader(itemMetadataFile)
    for row in itemMetadata:
        subjectDict = {}
        row_count = row_count + 1
        print(row_count)
        subjectDict['uri'] = row['uri']
        subjectDict['old_subject'] = row['dc.subject']
        subjectDict['search_subject'] = row['cleanedSubject']
        search_list = row['searchList']
        search_list = ast.literal_eval(search_list)
        fast_list = []
        mesh_list = []
        for subject in search_list:
            subject = subject.replace("Md", "Maryland")
            print(subject)
            fastClose_function(subject)
        subjectDict['fast_list'] = fast_list
        convert_list.append(subjectDict)

df = pd.DataFrame.from_dict(convert_list)
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
df.to_csv(path_or_buf='convertedMatchesToReview_Batch'+batch+'_'+dt+'.csv', index=False)
