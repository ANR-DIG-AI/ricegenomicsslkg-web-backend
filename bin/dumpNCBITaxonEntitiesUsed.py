"""
This script retrieves the labels and URIs of the  concepts that are used
as named entities of at least one article in the dataset.
The additional field 'count' gives the number of articles that have that concept and label as a named entity.

The result is used by the auto-completion of user inputs on the search form.
"""

import json
from SPARQLWrapper import SPARQLWrapper, JSON, POST
import json
import math
from SPARQLQuery import submit_sparql_query_chain

limit = 10000
totalResults = 3834

prefixes = '''
PREFIX fabio:   <http://purl.org/spar/fabio/>
PREFIX frbr:    <http://purl.org/vocab/frbr/core#>
PREFIX oa:      <http://www.w3.org/ns/oa#>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
'''

query_tpl = prefixes + '''
SELECT DISTINCT ?entityUri ?entityLabel ?entityPrefLabel (count(?document) as ?count) ?source
FROM NAMED <http://ns.inria.fr/d2kab/graph/wheatgenomicsslkg>
FROM NAMED <http://purl.obolibrary.org/obo/ncbitaxon/ncbitaxon.owl>
WHERE {
    
    {
        SELECT DISTINCT ?entityUri ?document WHERE {
            GRAPH <http://ns.inria.fr/d2kab/graph/wheatgenomicsslkg> {
                ?document a fabio:ResearchPaper.
                ?namedEntity oa:hasBody ?entityUri; oa:hasTarget [ oa:hasSource ?partOfArticle ] .
                ?partOfArticle frbr:partOf+ ?document.
            }
        }
    }

    {
        GRAPH <http://purl.obolibrary.org/obo/ncbitaxon/ncbitaxon.owl> {
            { ?entityUri rdfs:label ?entityLabel. }
            union
            { ?entityUri <http://www.geneontology.org/formats/oboInOwl#hasExactSynonym> ?entityLabel; rdfs:label ?entityPrefLabel }
            bind("Taxon" as ?source)
    	}
	}
} group by ?entityUri ?entityLabel ?entityPrefLabel ?source
offset %(offset)s
limit %(limit)s
'''

results_json = submit_sparql_query_chain(query_tpl, totalResults, limit)
print("Writing the output to JSON file...")
with open(f"../data/dumpEntitiesNCBITaxon.json", 'w', encoding="utf-8") as f:
    f.write(results_json)
