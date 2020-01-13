import rdflib
from rdflib.namespace import SKOS
from rdflib import Literal

# Put list of .nt files below.
files = []

# Put name of new text file.
f = open('newfile.txt', 'w')

for file in files:
    g = rdflib.Graph()
    g.parse(file, format='nt')
    print('parsed')
    # Searches for value in prefLabel.
    for o in g.objects(None, SKOS.prefLabel):
        o = Literal(o)
        o = str(o)
        f.write(o+', ')

    g.close()
