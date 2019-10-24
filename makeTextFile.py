import rdflib
from rdflib.namespace import SKOS
from rdflib import Literal

files = ['FASTFormGenre.nt', 'FASTTopical.nt']

f = open('FASTlist.txt', 'w')

for file in files:
    g = rdflib.Graph()
    g.parse(file, format='nt')
    print('yay!')

    for o in g.objects(None, SKOS.prefLabel):
        o = Literal(o)
        o = str(o)
        f.write(o+', ')

    g.close()
