import argparse
from datetime import datetime
import ast
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('-b', '--batch', help='Batch letter to name outputs.')
args = parser.parse_args()

if args.batch:
    batch = args.batch
else:
    batch = input('Enter batch letter: ')

fileList = ['subjectMatchesReviewed_BatchC2019-11-13 09.19.01 copy.csv']


def singleSelection(vocabType, results, selection):
    results = ast.literal_eval(results)
    selection = selection - 1
    newSubject = results[selection]
    newSubject = newSubject.strip()
    subjectDict['newSubject'] = newSubject
    if vocabType == 'fast':
        subjectDict['newKey'] = 'dc.subject.fast'
    if vocabType == 'mesh':
        subjectDict['newKey'] = 'dc.subject.mesh'
    subject_list.append(subjectDict)


def multipleSelections(vocabType, results, selection):
    results = ast.literal_eval(results)
    subjects = []
    for select in selection:
        select = select.strip()
        select = int(select)
        select = select - 1
        newSubject = results[select]
        newSubject = newSubject.strip()
        subjects.append(newSubject)
    subjects = '|'.join(subjects)
    subjectDict['newSubject'] = subjects
    if vocabType == 'fast':
        subjectDict['newKey'] = 'dc.subject.fast'
    if vocabType == 'mesh':
        subjectDict['newKey'] = 'dc.subject.mesh'
    subject_list.append(subjectDict)


def exactSubject(results):
    results = results.strip()
    subjectDict['newSubject'] = results
    subject_list.append(subjectDict)


error_list = []
subject_list = []
for filename in fileList:
    df_subjects = pd.read_csv(filename, header=0)
    ori_total = df_subjects.cleanedSubject.size
    print(ori_total)
    for index, row in df_subjects.iterrows():
        print(str(ori_total-index)+' left')
        row = dict(row)
        subjectDict = row.copy()
        subjectDict['oldKey'] = 'dc.subject'
        cleanedSubject = row['cleanedSubject']
        vocabType = row['type']
        results = row['results']
        selection = row['selection']
        try:
            selection = int(selection)
        except ValueError:
            if pd.isnull(selection):
                selection = selection
            elif ',' in selection:
                selection = selection.split(',')
            else:
                selection = selection.strip()
        if vocabType == 'fast_exact':
            subjectDict['newKey'] = 'dc.subject.fast'
            exactSubject(results)
        elif vocabType == 'mesh_exact':
            subjectDict['newKey'] = 'dc.subject.mesh'
            exactSubject(results)
        elif isinstance(selection, int):
            singleSelection(vocabType, results, selection)
        elif isinstance(selection, list):
            multipleSelections(vocabType, results, selection)
        elif selection == 'new selection' and ('[' not in results):
            subjectDict['newSubject'] = results
            if vocabType == 'fast':
                subjectDict['newKey'] = 'dc.subject.fast'
            if vocabType == 'mesh':
                subjectDict['newKey'] = 'dc.subject.mesh'
        elif selection == 'none' or vocabType == 'not found':
            subjectDict['newSubject'] = cleanedSubject
            subjectDict['newKey'] = 'dc.subject'
            subject_list.append(subjectDict)
        else:
            error_list.append(subjectDict)


print('{} errors found'.format(len(error_list)))

dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
df = pd.DataFrame.from_dict(subject_list)
df2 = pd.DataFrame.from_dict(error_list)

subjectFile = 'subjectsCombined'+'_Batch'+batch+'_'+dt+'.csv'
errorFile = 'errors_Batch'+batch+'_'+dt+'.csv'
df.to_csv(subjectFile, index=False)
df2.to_csv(errorFile, index=False)
