from datetime import datetime
import ast
import pandas as pd

fileList = ['convertedMatchesReviewed_BatchC_2020-03-19.csv']


def addType(vocabType):
    if vocabType == 'fast':
        subjectDict['newKey'] = 'dc.subject.fast'
        subject_list.append(subjectDict)
    elif vocabType == 'mesh':
        subjectDict['newKey'] = 'dc.subject.mesh'
        subject_list.append(subjectDict)
    else:
        error_list.append(subjectDict)


error_list = []
subject_list = []
for filename in fileList:
    df_subjects = pd.read_csv(filename, header=0)
    ori_total = df_subjects.search_subject.size
    print(ori_total)
    for index, row in df_subjects.iterrows():
        print(str(ori_total-index)+' left')
        row = dict(row)
        subjectDict = row.copy()
        subjectDict['oldKey'] = 'dc.subject'
        subjectDict['oldValue'] = row['old_subject']
        search_subject = row['search_subject']
        vocabType = row['type']
        results = row['results']
        if isinstance(results, float) or results == 'none':
            print(results)
            subjectDict['newKey'] = 'dc.subject'
            subjectDict['newValue'] = search_subject
            subject_list.append(subjectDict)
        elif '[' or '|' in results:
            if '[' in results:
                results = ast.literal_eval(results)
                results = [x.strip() for x in results]
                results = '|'.join(results)
                subjectDict['newValue'] = results
                addType(vocabType)
            elif '|' in results:
                results = results.split('|')
                results = [x.strip() for x in results]
                results = '|'.join(results)
                subjectDict['newValue'] = results
                addType(vocabType)
        else:
            results = results.strip()
            subjectDict['newValue'] = results
            addType(vocabType)


print('{} errors found'.format(len(error_list)))

dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
df = pd.DataFrame.from_dict(subject_list)
df2 = pd.DataFrame.from_dict(error_list)

subjectFile = 'subjectsCombined_'+dt+'.csv'
errorFile = 'errors_Batch_'+dt+'.csv'
df.to_csv(subjectFile, index=False)
df2.to_csv(errorFile, index=False)
