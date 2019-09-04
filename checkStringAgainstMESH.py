import requests
import csv
from datetime import datetime
import argparse
from fuzzywuzzy import fuzz


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


# some config
mesh_url = 'https://id.nlm.nih.gov/mesh/lookup/descriptor?label='


f = csv.writer(open('meshMatchesToReview_Batch'+batch+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'w'))
f.writerow(['uri']+['dc.subject']+['cleanedSubject']+['results'])


row_count = 0
with open(filename) as itemMetadataFile:
    itemMetadata = csv.DictReader(itemMetadataFile)
    for row in itemMetadata:
        row_count = row_count + 1
        print(row_count)
        uri = row['uri']
        old_subject = row['dc.subject']
        search_subject = row['cleanedSubject']
        category = row['category']
        print(search_subject)
        if category == 'MESH':
            search_query = search_subject.replace("--", " ")  # improve quality of searching API by deleting dashes & () from search query
            search_query = search_query.replace("(", " ")
            search_query = search_query.replace(")", " ")
            if '/' in search_subject:
                search_subjects = search_subject.split('/')
            else:
                search_subjects = [search_subject]
            url = mesh_url+search_subjects[0]+'&match=contains&limit=10'
            data = requests.get(url).json()
            for item in data:
                label = item.get('label')
                resource = item.get('resource')
                resource = resource.replace('http://id.nlm.nih.gov/mesh/', '')
                ratio = fuzz.token_sort_ratio(label, search_subjects[0])
                print('Options', label, ratio)
                if ratio > 95:
                    if len(search_subjects) == 1:
                        f.writerow([uri]+[old_subject]+[search_subject]+[label])
                    elif len(search_subjects) > 1:
                        pair_url = 'https://id.nlm.nih.gov/mesh/lookup/pair?label='+search_subjects[1]+'&descriptor=http%3A%2F%2Fid.nlm.nih.gov%2Fmesh%2F'+resource+'&match=contains&limit=10'
                        data = requests.get(pair_url).json()
                        for item in data:
                            full_label = item.get('label')
                            ratio = fuzz.token_sort_ratio(full_label, search_subjects)
                            print('Options', full_label, ratio)
                            if ratio > 95:
                                f.writerow([uri]+[old_subject]+[search_subject]+[full_label])
                                break
                        else:
                            f.writerow([uri]+[old_subject]+[search_subject]+['not found!'])
                    break
            else:
                f.writerow([uri]+[old_subject]+[search_subject]+['not found'])
        else:
            print('not mesh '+search_subject)
            f.writerow([uri]+[old_subject]+[search_subject])
