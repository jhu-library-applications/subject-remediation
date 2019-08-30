# subject-remediation

##checkStringAgainstFAST.py

A python script runs subject strings from a CSV against OCLC's FAST API to find possible matches. The results of this search are put into a new CSV with a column named "results". If an exact match to the subject string is found, "FASTmatch" is added to the "results" column. If no exact match is found, the 3 top results from the API are put into the "results" column as a list.

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

##checkStringAgainstMESH.py

A python script runs subject strings from a CSV against the MESH API to find valid matches.

##combineRowsWithIdenticalValuesInColumn.py

This row takes a CSV with subjects listed by item URI and creates a new CSV organized by subject string.

###original csv

|URI                 | subject      |
|--------------------|--------------|
|database/item/1     | turtles      |
|database/item/1     | Michigan     |
|database/item/2     | turtles      |
|database/item/2     | literature   |

###newcsv

|URI                              | subject      |
|---------------------------------|--------------|
|database/item/1, database/item/2 | turtles      |
|database/item/1                  | Michigan     |
|database/item/2                  | literature   |


##convertLCSHToFAST.py

Queries OCLC’s FAST API against split subject string permutations. Each subject string permutations calls up three FAST results from the API. If the FAST result has a fuzzy matching token_sort_ratio of more than 30, the result is added to a list called results_list in a new CSV.

##reformatCSVFromFASTSearches.py

Using the reformatCSVFromFASTSearches.py script, reformat the following CSVs into four columns in a new spreadsheet called subjectsCombined_BatchA.csv:

  * subjectMatchesReviewed_BatchA.csv
  * subjectMatchesReviewed_BatchA2.csv
  * nameMatchesReviewed_BatchA.csv
  * manualFixesReviewed_BatchA.csv  


The columns are the oldKey, newKey, oldValue, and newValue. Some subjects will have a newKey of dc.subject.fast This script will also produce a spreadsheet called errors_BatchA.csv; it contains subjects that did not meet the criteria for entry into subjectsCombined_BatchA.csv. Review this spreadsheet and fix errors in the original inputs until you can run the reformatCSVFromFASTSearches.py and have no entries in errors_BatchA.csv


##splitValuesByObjectType.py

SplitValuesByObjectType.py on subjectsCombined_BatchA.csv to split the subjects into two categories/spreadsheets:
  * replacing a subject with a single subject (subjectsToUpload_BatchA.csv)
  * replacing a subject with multiple subjects (subjectsToSplitAndUpload_BatchA.csv
