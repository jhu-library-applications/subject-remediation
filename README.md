# subject-remediation

## checkPuncuationOfStrings.py

This script finds subjects with commas, periods, colons, or that are formatted as a list.

## checkStringAgainstFASTAndMESH.py

This script runs subject strings from a CSV against [OCLC's FAST API](https://platform.worldcat.org/api-explorer/apis/fastapi) and [NIH's MESH API](https://hhs.github.io/meshrdf/sparql-and-uri-requests) to find possible matches.

This is done by looping through the following functions, and trying to find a match. If a match is found, the loop stops and the results are recorded in a CSV.

1) **fastExact_function**: Searches FAST API for an exact match. If it finds an authorized heading that exactly matches the cleanedSubject or has a fuzzywuzzy token_sort_ratio of 100, it records the match and the type in the csv 'subjectMatchesToReview_BatchA.csv'. The variable fastexact_found is set to 'yes.'

2) **mesh_function**: Searches MESH API for an exact match. If it finds an authorized heading that exactly matches the cleanedSubject or has a fuzzywuzzy token_sort_ratio of more than 95, it records the match and the type in the csv 'subjectMatchesToReview_BatchA.csv'. The variable mesh_found is set to 'yes'

3) **fastClose_function**: Searches the FAST API for a close match. If it finds any authorized headings with a fuzzywuzzy token_sort_ratio of over 70 or a token_set_ratio of 80

3) **fastNoResults_function**: Splits up subject heading into different string combos and adds to csv 'potentialLCSHToConvert_BatchA.csv'

The csv 'subjectMatchesToReview_BatchA.csv' has the following columns: uri, dc.subject, cleanedSubject, type, results, and homonym.

URI contains the item(s) uri(s)
dc.subject contains the original subject string from the item(s)
cleanedSubject is the cleaned subject (removed puncuation and editing from previous scripts)
Type is either 'fast_exact', 'mesh_exact', 'fast', or 'not found'.
Results contain the authorized heading from the API search
Homonym contains 'yes' if the subject is homonym. This was generated from [homonymCheck.py]()


If the FAST API does not find any possible matches for a subject string, there is option for the script to split the subject string by "--" or by capitalization pattern to create meaningful permutations of the string. For instance, the string "Agricultural resources--Maryland--Carroll County--Maps" will be split into 4 different strings, which has 9 different permutations (see below) that might be meaningful to the FAST API. These different meaningful permutations are combined into a list and added in a column "subject_search_list" in new CSV called "potentialLCSHToConvert_Batch.csv". In convertLCSHToFAST.py. these permutations are searched again against the FAST API for possible matches.


|subject                                                | meaningful permutations                          |
|-------------------------------------------------------|--------------------------------------------------|
|Agricultural resources--Maryland--Carroll County--Maps | Agricultural resources                           |  
|Agricultural resources--Maryland--Carroll County--Maps | Maryland                                         |
|Agricultural resources--Maryland--Carroll County--Maps | Carroll County                                   |
|Agricultural resources--Maryland--Carroll County--Maps | Maps                                             |
|Agricultural resources--Maryland--Carroll County--Maps | Agricultural resources--Maryland--Carroll County |
|Agricultural resources--Maryland--Carroll County--Maps | Maryland--Carroll County--Maps                   |
|Agricultural resources--Maryland--Carroll County--Maps | Agricultural resources--Maryland                 |
|Agricultural resources--Maryland--Carroll County--Maps | Maryland--Carroll County                         |
|Agricultural resources--Maryland--Carroll County--Maps | Carroll County--Maps                             |


## combineRowsWithIdenticalValuesInColumn.py

This row takes a CSV with subjects listed by item URI and creates a new CSV organized by subject string.

### original csv

|URI                 | subject      |
|--------------------|--------------|
|database/item/1     | turtles      |
|database/item/1     | Michigan     |
|database/item/2     | turtles      |
|database/item/2     | literature   |

### newcsv

|URI                              | subject      |
|---------------------------------|--------------|
|database/item/1, database/item/2 | turtles      |
|database/item/1                  | Michigan     |
|database/item/2                  | literature   |


## convertLCSHToFAST.py

Queries OCLC’s FAST API against split subject string permutations. Each subject string permutations calls up three FAST results from the API. If the FAST result has a fuzzy matching token_sort_ratio of more than 30, the result is added to a list called results_list in a new CSV.

## homonymCheck.py

This script checks subjects against a CSV with English language homonyms and marks them if they are a homonym. 

## reformatCSVFromFASTSearches.py

Using the reformatCSVFromFASTSearches.py script, reformat the following CSVs into four columns in a new spreadsheet called subjectsCombined_BatchA.csv:

  * subjectMatchesReviewed_BatchA.csv
  * subjectMatchesReviewed_BatchA2.csv
  * nameMatchesReviewed_BatchA.csv
  * manualFixesReviewed_BatchA.csv  


The columns are the oldKey, newKey, oldValue, and newValue. Some subjects will have a newKey of dc.subject.fast This script will also produce a spreadsheet called errors_BatchA.csv; it contains subjects that did not meet the criteria for entry into subjectsCombined_BatchA.csv. Review this spreadsheet and fix errors in the original inputs until you can run the reformatCSVFromFASTSearches.py and have no entries in errors_BatchA.csv

## splitSubjectsByCategory.py

This script splits up subjects categorized as a list of subjects. It splits up by commas or by newline/tab. For each individual subject from a list of subjects, it creates a row in a new CSV called 'listSubjectsToCheckAgainstFASTAndMESH_BatchA.csv'. For uncategorized subjects or subjects with periods, it adds them to a new CSV called 'subjectsToCheckAgainstFASTAndMESH_BatchA.csv.' Periods are removed before being added to the CSV if they were categorized as 'remove.'

## splitValuesByObjectType.py

SplitValuesByObjectType.py on subjectsCombined_BatchA.csv to split the subjects into two categories/spreadsheets:
  * replacing a subject with a single subject (subjectsToUpload_BatchA.csv)
  * replacing a subject with multiple subjects (subjectsToSplitAndUpload_BatchA.csv)
