import argparse
from datetime import datetime
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--file', help='enter filename with csv.')
args = parser.parse_args()

if args.file:
    filename = args.file
else:
    filename = input('Enter filename (including \'.csv\'): ')

df_subjects = pd.read_csv(filename, header=0)

df_subjects.newValue = df_subjects.newValue.str.strip()

new_unique = df_subjects.newValue.value_counts()
new_unique.to_csv('newValuecounts.csv')
print(len(new_unique))
old_unique = df_subjects.oldValue.value_counts()
old_unique.to_csv('oldValuecounts.csv')
print(len(old_unique))


all_items = []
dropped = 0
for count, row in df_subjects.iterrows():
    row = row
    uri = row['uri']
    oldValue = row['oldValue']
    newValue = row['newValue'].strip()
    newKey = row['newKey'].strip()
    oldKey = row['oldKey']
    if ((oldKey == newKey) and (newValue == oldValue)):
        dropped = dropped + 1
        print(oldKey, newKey)
        print(oldValue, newValue)
        print("")
        pass
    else:
        all_items.append(row)

df = pd.DataFrame.from_dict(all_items)
dt = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
df.to_csv('test_'+dt+'.csv', index=False)
