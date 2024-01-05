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
totalResults = 1237

prefixes = '''
PREFIX fabio:   <http://purl.org/spar/fabio/>
PREFIX frbr:    <http://purl.org/vocab/frbr/core#>
PREFIX oa:      <http://www.w3.org/ns/oa#>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos:    <http://www.w3.org/2004/02/skos/core#>
'''

query_tpl = prefixes + '''
SELECT DISTINCT ?entityUri ?entityLabel ?entityPrefLabel (COUNT(?document) AS ?count) ?source
FROM <http://ns.inria.fr/d2kab/graph/wheatgenomicsslkg>
WHERE {
  {
    SELECT DISTINCT ?entityUri ?document 
    WHERE {
        ?document a fabio:ResearchPaper.
        ?namedEntity oa:hasBody ?entityUri; oa:hasTarget [ oa:hasSource ?partOfArticle ] .
        ?partOfArticle frbr:partOf+ ?document.
    }
  }

  {
    ?entityUri skos:prefLabel ?entityLabel.
    BIND(
      IF(STRSTARTS(STR(?entityUri), "http://ns.inria.fr/d2kab/variety"),
        "Variety",
        IF(STRSTARTS(STR(?entityUri), "http://ns.inria.fr/d2kab/gene"), "Gene", "")
      )
      AS ?source
    )
    FILTER (!STRSTARTS(STR(?entityUri), "http://purl.obolibrary.org/obo/NCBITaxon"))
    FILTER (!STRSTARTS(STR(?entityUri), "http://ns.inria.fr/d2kab/marker"))
    FILTER (!STRSTARTS(STR(?entityUri), "http://opendata.inrae.fr/wto"))
  }
}  group by ?entityUri ?entityLabel ?entityPrefLabel ?source
offset %(offset)s
limit %(limit)s
'''

if __name__ == "__main__":
    results_json = submit_sparql_query_chain(query_tpl, totalResults, limit)
    print("Writing the output to JSON file...")
    with open(f"../data/dumpEntitiesGeneVariety.json", 'w', encoding="utf-8") as f:
        f.write(results_json)
