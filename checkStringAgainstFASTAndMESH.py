import requests
import csv
from datetime import datetime
import re
import argparse
from fuzzywuzzy import fuzz
import pandas as pd


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='enter filename with csv. optional - if not provided, the script will ask for input')
parser.add_argument('-b', '--batch', help='Batch letter to name outputs. optional - if not provided, the script will ask for input')
parser.add_argument('-d', '--divide', help='Do you want to divide non-matches? optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')

if args.batch:
    batch = args.batch
else:
    batch = input('Enter batch letter: ')

if args.divide:
    divide = args.divide
else:
    divide = input('Do you want to divide non-matches? Enter yes or no: ')

# some config
api_base_url = "http://fast.oclc.org/searchfast/fastsuggest"
mesh_url = 'https://id.nlm.nih.gov/mesh/lookup/descriptor?label='
# For constructing links to FAST.
fast_uri_base = "http://id.worldcat.org/fast/{0}"

f1name = 'subjectMatchesToReview_Batch'+batch+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv'
f2name = 'potentialLCSHToConvert_Batch'+batch+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv'

f = open(f1name, 'w')
writer1 = csv.writer(f)
writer1.writerow(['uri']+['dc.subject']+['cleanedSubject']+['type']+['results'])
f2 = open(f2name, 'w')
writer2 = csv.writer(f2)
writer2.writerow(['uri']+['dc.subject']+['cleanedSubject']+['searchList'])


def fastResults_function(uri, old_subject, response, search_subject):
    for metadata in response:
        if metadata == 'docs':
            keyInfo = response.get(metadata)
            auth_names = []
            for info in keyInfo:
                auth_name = info.get('auth')
                ratio = fuzz.token_sort_ratio(auth_name, search_subject)
                if auth_name == search_subject or ratio == 100:
                    writer1.writerow([uri]+[old_subject]+[search_subject]+['fast_exact']+[auth_name])
                    global fast_found
                    fast_found = 'yes'
                    break
                elif ratio >= 90:
                    if auth_name not in auth_names:
                        auth_names.append(auth_name)
                else:
                    pass
            if len(auth_names) > 0:
                writer1.writerow([uri]+[old_subject]+[search_subject]+['fast']+[auth_names])
            elif fast_found == 'yes':
                pass
            else:
                fast_found = 'no'


def fastNoResults_function(uri, old_subject, search_subject, divide, search_subjects):
    if divide == 'yes':
        subject_search_list = []
        divided_subjects = []
        if search_subject.find("--") != -1:
            raw_divided_subjects = search_subject.split("--")
        else:
            raw_divided_subjects = re.findall('([A-Z][^A-Z]*)', search_subject)
        for subject in raw_divided_subjects:
            subject = subject.replace("--", "").replace(".", "").strip()
            divided_subjects.append(subject)
        if len(divided_subjects) >= 2:
            for subject in divided_subjects:
                subject_search_list.append(subject)
                if len(divided_subjects) >= 3:
                    divided_subjects_a = ' '.join(divided_subjects[:2])
                    subject_search_list.append(divided_subjects_a)
                    divided_subjects_b = ' '.join(divided_subjects[1:])
                    subject_search_list.append(divided_subjects_b)
                    if len(divided_subjects) >= 4:
                        divided_subjects_c = ' '.join(divided_subjects[0:3])
                        subject_search_list.append(divided_subjects_c)
                        divided_subjects_d = ' '.join(divided_subjects[1:3])
                        subject_search_list.append(divided_subjects_d)
                        divided_subjects_e = ' '.join(divided_subjects[2:])
                        subject_search_list.append(divided_subjects_e)
        print(subject_search_list)
        if len(subject_search_list) > 1:
            writer2.writerow([uri]+[old_subject]+[search_subject]+[subject_search_list])
        else:
            writer1.writerow([uri]+[old_subject]+[search_subject]+['not found'])
    else:
        writer1.writerow([uri]+[old_subject]+[search_subject]+['not found'])


def mesh_function(uri, old_subject, search_subject, meshsearch_url, search_subjects):
    subject_count = len(search_subjects)
    mesh_data = requests.get(meshsearch_url).json()
    label_list = []
    for mesh_item in mesh_data:
        label = mesh_item.get('label')
        resource = mesh_item.get('resource')
        resource = resource.replace('http://id.nlm.nih.gov/mesh/', '')
        ratio = fuzz.token_sort_ratio(label, search_subjects[0])
        if ratio > 95:
            if subject_count == 1:
                label_list.append(label)
                break
            elif subject_count > 1:
                pair_url = 'https://id.nlm.nih.gov/mesh/lookup/pair?label='+search_subjects[1]+'&descriptor=http%3A%2F%2Fid.nlm.nih.gov%2Fmesh%2F'+resource+'&match=contains&limit=10'
                mesh_data = requests.get(pair_url).json()
                for mesh_item in mesh_data:
                    full_label = mesh_item.get('label')
                    ratio = fuzz.token_sort_ratio(full_label, search_subjects)
                    if ratio > 95:
                        label_list.append(full_label)
                        break
                    else:
                        pass
        else:
            pass
    print(label_list)
    if len(label_list) > 0:
        writer1.writerow([uri]+[old_subject]+[search_subject]+['mesh_exact']+[label_list])
    else:
        global mesh_found
        mesh_found = 'no'


row_count = 0
with open(filename) as itemMetadataFile:
    itemMetadata = csv.DictReader(itemMetadataFile)
    for row in itemMetadata:
        fast_found = ''
        mesh_found = ''
        row_count = row_count + 1
        uri = row['uri']
        old_subject = row['dc.subject']
        search_subject = row['cleanedSubject']
        print(search_subject)
        search_query = search_subject.replace("--", " ")  # improve quality of searching API by deleting dashes & () from search query
        search_query = search_query.replace("(", " ")
        search_query = search_query.replace(")", " ")
        if '/' in search_subject:
            search_subjects = search_subject.split('/')
        else:
            search_subjects = [search_subject]
        url = api_base_url + '?&query=' + search_query
        url += '&queryIndex=suggestall&queryReturn=suggestall,idroot,auth,tag,raw&suggest=autoSubject&rows=3&wt=json'
        meshsearch_url = mesh_url+search_subjects[0]+'&match=contains&limit=10'
        try:
            data = requests.get(url).json()
            for item in data:
                if item == 'response':
                    response = data.get(item)
                    if response.get('numFound') > 0:
                        fastResults_function(uri, old_subject, response, search_subject)
                        if fast_found == 'no':
                            mesh_function(uri, old_subject, search_subject, meshsearch_url, search_subjects)
                            if mesh_found == 'no':
                                fastNoResults_function(uri, old_subject, search_subject, divide, search_subjects)
                            else:
                                pass
                    elif response.get('numFound') == 0:
                        mesh_function(uri, old_subject, search_subject, meshsearch_url, search_subjects)
                        if mesh_found == 'no':
                            fastNoResults_function(uri, old_subject, search_subject, divide, search_subjects)
                        else:
                            pass
        except:
            writer1.writerow([uri]+[old_subject]+[search_subject]+['not found'])

f.close()
f2.close()

spreadsheet1 = pd.read_csv(f1name)
spreadsheet2 = pd.read_csv(f2name)
print('original rows: '+str(row_count))
print('first spreadsheet: '+str(len(spreadsheet1)))
print('second spreadsheet: '+str(len(spreadsheet2)))
total = len(spreadsheet1)+len(spreadsheet2)
print('both spreadsheets: '+str(total))
