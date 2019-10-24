import requests
import csv
from datetime import datetime
import re
import argparse


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


f = csv.writer(open('subjectMatchesToReview_Batch'+batch+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'w'))
f.writerow(['uri']+['dc.subject']+['cleanedSubject']+['results'])
f2 = csv.writer(open('potentialLCSHToConvert_Batch'+batch+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'w'))
f2.writerow(['uri']+['dc.subject']+['cleanedSubject']+['searchList'])

row_count = 0
with open(filename) as itemMetadataFile:
    itemMetadata = csv.DictReader(itemMetadataFile)
    for row in itemMetadata:
        row_count = row_count + 1
        print(row_count)
        uri = row['uri']
        old_subject = row['dc.subject']
        search_subject = row['cleanedSubject']
        print(search_subject)
        names = []
        search_query = search_subject.replace("--", " ")  # improve quality of searching API by deleting dashes & () from search query
        search_query = search_query.replace("(", " ")
        search_query = search_query.replace(")", " ")
        url = api_base_url + '?&query=' + search_query
        url += '&queryIndex=suggestall&queryReturn=suggestall,idroot,auth,tag,raw&suggest=autoSubject&rows=3&wt=json'
        try:
            data = requests.get(url).json()
            for item in data:
                if item == 'response':
                    if response.get('numFound') > 0:
                        response = data.get(item)
                        for metadata in response:
                            if metadata == 'docs':
                                keyInfo = response.get(metadata)
                                for info in keyInfo:
                                    name = info.get('auth')
                                    if name not in names:
                                        names.append(name)
                                for name in names:
                                    ratio = fuzz.token_sort_ratio(name, search_subject)
                                    if name == search_subject:
                                        names = 'FASTmatch'
                                    elif ratio > 95:
                                        results = 
                            f.writerow([uri]+[old_subject]+[search_subject]+[names])

                    if response.get('numFound') == 0:  # if no results found from FAST search, divide up subjects and put into new csv

                        #  start MESH search
                        if '/' in search_subject:
                            search_subjects = search_subject.split('/')
                        else:
                            search_subjects = [search_subject]
                        url = mesh_url+search_subjects[0]+'&match=contains&limit=10'
                        mesh_data = requests.get(url).json()
                        for mesh_item in mesh_data:
                            label = mesh_item.get('label')
                            resource = mesh_item.get('resource')
                            resource = resource.replace('http://id.nlm.nih.gov/mesh/', '')
                            ratio = fuzz.token_sort_ratio(label, search_subjects[0])
                            print('Options', label, ratio)
                            if ratio > 95:
                                if len(search_subjects) == 1:
                                    f.writerow([uri]+[old_subject]+[search_subject]+[label])
                                elif len(search_subjects) > 1:
                                    pair_url = 'https://id.nlm.nih.gov/mesh/lookup/pair?label='+search_subjects[1]+'&descriptor=http%3A%2F%2Fid.nlm.nih.gov%2Fmesh%2F'+resource+'&match=contains&limit=10'
                                    mesh_data = requests.get(pair_url).json()
                                    for mesh_item in mesh_data:
                                        full_label = mesh_item.get('label')
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


                            else:




                        if divide == 'yes':
                            print('No matches found')
                            subject_search_list = []
                            if search_subject.find("--") != -1:
                                raw_divided_subjects = search_subject.split("--")
                            else:
                                raw_divided_subjects = re.findall('([A-Z][^A-Z]*)', search_subject)
                            divided_subjects = []
                            for subject in raw_divided_subjects:
                                subject = subject.replace("--", "")
                                subject = subject.replace(".", "")
                                subject = subject.strip()
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
                            f2.writerow([uri]+[old_subject]+[search_subject]+[subject_search_list])
                            # print('added to second spreadsheet')
                            break
                        else:
                            f.writerow([uri]+[old_subject]+[search_subject]+[names])
                            # print('added to first spreadsheet')
                    else:
                        for metadata in response:
                            if metadata == 'docs':
                                keyInfo = response.get(metadata)
                                for info in keyInfo:
                                    name = info.get('auth')
                                    if name not in names:
                                        names.append(name)
                                for name in names:
                                    if name == search_subject:
                                        names = 'FASTmatch'
                                    else:
                                        pass
                        f.writerow([uri]+[old_subject]+[search_subject]+[names])
                        # print('added to first spreadsheet')
        except:
            print('exception')
            f.writerow([uri]+[old_subject]+[search_subject]+[names])
            # print('added to first spreadsheet')
