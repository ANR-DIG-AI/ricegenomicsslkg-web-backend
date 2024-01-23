"""
This script retrieves the labels and URIs of the  concepts that are used
as named entities of at least one article in the dataset.
The additional field 'count' gives the number of articles that have that concept and label as a named entity.

The result is used by the auto-completion of user inputs on the search form.
"""

from SPARQLQuery import submit_sparql_query_chain

limit = 10000
totalResults = 239

prefixes = '''
PREFIX fabio:   <http://purl.org/spar/fabio/>
PREFIX frbr:    <http://purl.org/vocab/frbr/core#>
PREFIX oa:      <http://www.w3.org/ns/oa#>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos:    <http://www.w3.org/2004/02/skos/core#>
'''

query_tpl = prefixes + '''
SELECT DISTINCT ?entityUri ?entityLabel ?entityPrefLabel (count(?document) as ?count) ?entityType
FROM NAMED <http://ns.inria.fr/d2kab/graph/wheatgenomicsslkg>
FROM NAMED <http://ns.inria.fr/d2kab/ontology/wto/v3>
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
      GRAPH <http://ns.inria.fr/d2kab/ontology/wto/v3> {
        { ?entityUri skos:prefLabel ?entityLabel. }
      	UNION
      	{ ?entityUri skos:altLabel ?entityLabel; skos:prefLabel ?entityPrefLabel. }
      	UNION
      	{ ?entityUri a owl:Class ; rdfs:label ?entityLabel. }
        UNION
        { ?entityUri skos:altLabel ?entityLabel; rdfs:label ?entityPrefLabel. }

        bind("Phenotype or trait" as ?entityType)
      }
  	}
} group by ?entityUri ?entityLabel ?entityPrefLabel ?entityType
offset %(offset)s
limit %(limit)s
'''

results_json = submit_sparql_query_chain(query_tpl, totalResults, limit)
with open(f"../data/dumpEntitiesWTO.json", 'w', encoding="utf-8") as f:
    f.write(results_json)
