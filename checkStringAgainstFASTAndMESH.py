import requests
import csv
from datetime import datetime
import re
import argparse
from fuzzywuzzy import fuzz
import pandas as pd


parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='Enter filename with csv.')
parser.add_argument('-b', '--batch', help='Enter batch letter to name outputs')
parser.add_argument('-d', '--divide', help='Divide non-matches? Enter yes/no')
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

# Some config for FAST and MESH APIs.
api_base_url = "http://fast.oclc.org/searchfast/fastsuggest"
mesh_url = 'https://id.nlm.nih.gov/mesh/lookup/descriptor?label='
fast_uri_base = "http://id.worldcat.org/fast/{0}"

dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')

f1name = 'subjectMatchesToReview_Batch'+batch+'_'+dt+'.csv'
f2name = 'potentialLCSHToConvert_Batch'+batch+'_'+dt+'.csv'

f = open(f1name, 'w')
w1 = csv.writer(f)
w1.writerow(['uri']+['dc.subject']+['cleanedSubject']+['type']+['results']+['homonym'])
f2 = open(f2name, 'w')
w2 = csv.writer(f2)
w2.writerow(['uri']+['dc.subject']+['cleanedSubject']+['searchList']+['homonym'])


#  Find exact matches from FAST API.
def fastExact_function(uri, old_subject, search_query, search_subject):
    global fastexact_found
    fast_url = api_base_url + '?&query=' + search_query
    fast_url += '&queryIndex=suggestall&queryReturn=suggestall,idroot,auth,tag,raw&suggest=autoSubject&rows=5&wt=json'
    try:
        data = requests.get(fast_url).json()
        for item in data:
            if item == 'response':
                response = data.get(item)
                if response.get('numFound') > 0:
                    for metadata in response:
                        if metadata == 'docs':
                            keyInfo = response.get(metadata)
                            for info in keyInfo:
                                auth_name = info.get('auth')
                                ratio = fuzz.token_sort_ratio(auth_name, search_subject)
                                if auth_name == search_subject or ratio == 100:
                                    print('auth100:'+auth_name)
                                    w1.writerow([uri]+[old_subject]+[search_subject]+['fast_exact']+[auth_name]+[homonym])
                                    fastexact_found = 'yes'
                                    break
                                else:
                                    pass
    except ValueError:
        fastexact_found = 'no'


#  Find close matches from FAST API
def fastClose_function(uri, old_subject, search_query, search_subject):
    auth_names = []
    global fast_found
    fast_url = api_base_url + '?&query=' + search_query
    fast_url += '&queryIndex=suggestall&queryReturn=suggestall,idroot,auth,tag,raw&suggest=autoSubject&rows=5&wt=json'
    try:
        data = requests.get(fast_url).json()
        for item in data:
            if item == 'response':
                response = data.get(item)
                if response.get('numFound') > 0:
                    for metadata in response:
                        if metadata == 'docs':
                            keyInfo = response.get(metadata)
                            for info in keyInfo:
                                auth_name = info.get('auth')
                                suggest_all = info.get('suggestall')
                                ratio = fuzz.token_sort_ratio(auth_name, search_subject)
                                suggest_ratio_0 = fuzz.token_set_ratio(suggest_all[0], search_subject)
                                if ratio >= 70 or suggest_ratio_0 >= 80:
                                    if auth_name not in auth_names:
                                        auth_names.append(auth_name)
                                else:
                                    pass
    except ValueError:
        fast_found = 'no'
    if len(auth_names) > 0:
        print(auth_names)
        w1.writerow([uri]+[old_subject]+[search_subject]+['fast']+[auth_names]+[homonym])
    else:
        fast_found = 'no'


#  Split up subject search string into meaningful permutations.
def fastNoResults_function(uri, old_subject, search_subject, divide, search_subjects):
    if divide == 'yes':
        subject_search_list = []
        divided_subjects = []
        if search_subject.find("--") != -1:
            raw_divided_subjects = search_subject.split("--")
        else:
            raw_divided_subjects = re.split(r'\s+', search_subject)
        for subject in raw_divided_subjects:
            subject = subject.replace("--", "").replace(".", "").strip()
            divided_subjects.append(subject)
        print(divided_subjects)
        if len(divided_subjects) >= 3:
            for term in divided_subjects:
                subject_search_list.append(term)
                print(term)
            print(subject_search_list)
            divided_subjects_a = ' '.join(divided_subjects[:2])
            subject_search_list.append(divided_subjects_a)
            print(subject_search_list)
            divided_subjects_b = ' '.join(divided_subjects[1:])
            subject_search_list.append(divided_subjects_b)
            print(subject_search_list)
            if len(divided_subjects) >= 4:
                divided_subjects_c = ' '.join(divided_subjects[0:3])
                subject_search_list.append(divided_subjects_c)
                divided_subjects_d = ' '.join(divided_subjects[1:3])
                subject_search_list.append(divided_subjects_d)
                divided_subjects_e = ' '.join(divided_subjects[2:])
                subject_search_list.append(divided_subjects_e)
            w2.writerow([uri]+[old_subject]+[search_subject]+[subject_search_list]+[homonym])
        else:
            w1.writerow([uri]+[old_subject]+[search_subject]+['not found']+['']+[homonym])
    else:
        w1.writerow([uri]+[old_subject]+[search_subject]+['not found']+['']+[homonym])


#  Find exact matches from MESH API.
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
    if len(label_list) > 0:
        w1.writerow([uri]+[old_subject]+[search_subject]+['mesh_exact']+[label_list[0]]+[homonym])
    else:
        global mesh_found
        mesh_found = 'no'


row_count = 0
with open(filename) as itemMetadataFile:
    itemMetadata = csv.DictReader(itemMetadataFile)
    for row in itemMetadata:
        fast_found = ''
        mesh_found = ''
        fastexact_found = ''
        row_count = row_count + 1
        uri = row['uri']
        old_subject = row['dc.subject']
        search_subject = row['cleanedSubject'].strip()
        homonym = row['homonym']
        print(search_subject)
        #  Improve quality of API search.
        search_query = search_subject.replace("--", " ")
        search_query = search_query.replace("(", " ")
        search_query = search_query.replace(")", " ")
        if '/' in search_subject:
            search_subjects = search_subject.split('/')
        else:
            search_subjects = [search_subject]
        meshsearch_url = mesh_url+search_subjects[0]+'&match=contains&limit=10'
        #  Loop through function to find matches.
        fastExact_function(uri, old_subject, search_query, search_subject)
        if fastexact_found != 'yes':
            mesh_function(uri, old_subject, search_subject, meshsearch_url, search_subjects)
            if mesh_found == 'no':
                fastClose_function(uri, old_subject, search_query, search_subject)
                if fast_found == 'no':
                    fastNoResults_function(uri, old_subject, search_subject, divide, search_subjects)
                else:
                    pass

f.close()
f2.close()

spreadsheet1 = pd.read_csv(f1name)
spreadsheet2 = pd.read_csv(f2name)
print('original rows: '+str(row_count))
print('first spreadsheet: '+str(len(spreadsheet1)))
print('second spreadsheet: '+str(len(spreadsheet2)))
total = len(spreadsheet1)+len(spreadsheet2)
print('both spreadsheets: '+str(total))
