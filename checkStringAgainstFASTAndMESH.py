import requests
from datetime import datetime
import re
import argparse
from fuzzywuzzy import fuzz
import pandas as pd
from nltk.corpus import stopwords


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

sw = stopwords.words("english")


#  Find exact matches from FAST API.
def fastExact(search_query, search_subject):
    fast_url = api_base_url + '?&query=' + search_query
    fast_url += '&queryIndex=suggestall&queryReturn=suggestall,auth,type&suggest=autoSubject&rows=5&wt=json'
    try:
        data = requests.get(fast_url).json()
        response = data.get('response')
        if response.get('numFound') > 0:
            keyInfo = response.get('docs')
            for info in keyInfo:
                auth_name = info.get('auth')
                alt_names = info.get('suggestall')
                alt_name = alt_names[0]
                ratio = fuzz.token_sort_ratio(auth_name, search_subject)
                ratio_alt = fuzz.token_sort_ratio(alt_name, search_subject)
                if ratio >= 99 or ratio_alt >= 99:
                    print('auth100:'+auth_name)
                    newDict['type'] = 'fast_exact'
                    newDict['results'] = auth_name
                    break
                else:
                    pass
    except ValueError:
        pass


#  Find close matches from FAST API
def fastSuggestAll(search_query, search_subject):
    auth_names = []
    fast_url = api_base_url + '?&query=' + search_query
    fast_url += '&queryIndex=suggestall&queryReturn=suggestall,auth,type&suggest=autoSubject&rows=5&wt=json'
    try:
        data = requests.get(fast_url).json()
        response = data.get('response')
        if response.get('numFound') > 0:
            keyInfo = response.get('docs')
            for info in keyInfo:
                auth_name = info.get('auth')
                alt_names = info.get('suggestall')
                alt_name = alt_names[0]
                ratio = fuzz.token_sort_ratio(auth_name, search_subject)
                ratio_alt = fuzz.token_sort_ratio(alt_name, search_subject)
                if ratio >= 30 or ratio_alt >= 30:
                    if auth_name not in auth_names:
                        auth_names.append(auth_name)
                    else:
                        pass
    except ValueError:
        pass
    if len(auth_names) > 0:
        newDict['type'] = 'fast'
        newDict['results'] = auth_names
        print(auth_names)


#  Split up subject search string into meaningful permutations.
def splitSubjects(search_subject):
    if search_subject.find("--") != -1:
        raw_divided_subjects = search_subject.split("--")
    else:
        raw_divided_subjects = re.split(r'\s+', search_subject)
    split_subs = []
    for subject in raw_divided_subjects:
        subject = subject.replace("--", "").replace(".", "").strip()
        if subject.lower() not in sw:
            if len(subject) > 1:
                split_subs.append(subject)
    if len(split_subs) > 2:
        subject_list = []
        for count, term in enumerate(split_subs):
            subject_list.append(term)
            try:
                oneRight = split_subs[count+1]
                newPair = term+' '+oneRight
                subject_list.append(newPair)
                try:
                    twoRight = split_subs[count+2]
                    newTriple = newPair+' '+twoRight
                    subject_list.append(newTriple)
                except IndexError:
                    pass
            except IndexError:
                pass
        newDict['searchList'] = subject_list


#  Find exact matches from MESH API.
def meshExact(search_subjects):
    subject_count = len(search_subjects)
    meshsearch_url = mesh_url+search_subjects[0]+'&match=contains&limit=10'
    mesh_data = requests.get(meshsearch_url).json()
    for mesh_item in mesh_data:
        label = mesh_item.get('label')
        resource = mesh_item.get('resource')
        resource = resource.replace('http://id.nlm.nih.gov/mesh/', '')
        ratio = fuzz.token_sort_ratio(label, search_subjects[0])
        if ratio > 95:
            if subject_count == 1:
                newDict['type'] = 'mesh_exact'
                newDict['results'] = label
                break
            elif subject_count > 1:
                pair_url = 'https://id.nlm.nih.gov/mesh/lookup/pair?label='+search_subjects[1]+'&descriptor='+resource+'&match=contains&limit=10'
                mesh_data = requests.get(pair_url).json()
                for mesh_item in mesh_data:
                    full_label = mesh_item.get('label')
                    print(full_label)
                    search_string = search_subjects.join('/')
                    ratio = fuzz.token_sort_ratio(full_label, search_string)
                    if ratio > 95:
                        newDict['type'] = 'mesh_exact'
                        newDict['results'] = full_label
                        break
                    else:
                        pass
        else:
            pass


all_items = []
df_subjects = pd.read_csv(filename, header=0)
ori_total = df_subjects.cleanedSubject.size
print(ori_total)
for index, row in df_subjects.iterrows():
    print(str(ori_total-index)+' left')
    row = dict(row)
    newDict = row.copy()
    search_subject = row['cleanedSubject'].strip()
    #  Improve quality of API search.
    search_query = search_subject.replace("--", " ")
    search_query = search_query.replace("(", " ")
    search_query = search_query.replace(")", " ")
    if '/' in search_subject:
        search_subjects = search_subject.split('/')
    else:
        search_subjects = [search_subject]
    #  Loop through function to find matches.
    print(search_query)
    fastExact(search_query, search_subject)
    if newDict.get('results') is None:
        meshExact(search_subjects)
        if newDict.get('results') is None:
            fastSuggestAll(search_query, search_subject)
            if newDict.get('results') is None and divide == 'yes':
                splitSubjects(search_subject)
                if newDict.get('searchList') is None:
                    newDict['type'] = 'not_found'
    all_items.append(newDict)

dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
df = pd.DataFrame.from_dict(all_items)
print(df.type.value_counts())
df_1 = df.copy()
df_1 = df_1[df_1['type'].notnull()]

df_2 = df.copy()
df_2 = df_2[df_2['searchList'].notnull()]

print('original total: '+str(ori_total))
print('matches to review spreadsheet: '+str(len(df_1)))
print('split subject spreadsheet: '+str(len(df_2)))
total = len(df_1)+len(df_2)
print('both spreadsheets: '+str(total))

f1name = 'subjectMatchesToReview_Batch'+batch+'_'+dt+'.csv'
f2name = 'potentialLCSHToConvert_Batch'+batch+'_'+dt+'.csv'
df_1.to_csv(path_or_buf=f1name, index=False)
df_2.to_csv(path_or_buf=f2name, index=False)
