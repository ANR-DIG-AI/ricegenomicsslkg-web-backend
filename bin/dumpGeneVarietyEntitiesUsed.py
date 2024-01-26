"""
This script retrieves the labels and URIs of the  concepts that are used
as named entities of at least one article in the dataset.
The additional field 'count' gives the number of articles that have that concept and label as a named entity.

The result is used by the auto-completion of user inputs on the search form.
"""

from SPARQLQuery import submit_sparql_query_chain

limit = 10000
totalResults = 1237

query_tpl = '''
PREFIX fabio:   <http://purl.org/spar/fabio/>
PREFIX frbr:    <http://purl.org/vocab/frbr/core#>
PREFIX oa:      <http://www.w3.org/ns/oa#>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos:    <http://www.w3.org/2004/02/skos/core#>

SELECT DISTINCT ?entityUri ?entityLabel ?entityPrefLabel ?count ?entityType
FROM <http://ns.inria.fr/d2kab/graph/wheatgenomicsslkg>
WHERE {
  {
    SELECT DISTINCT ?entityUri (COUNT(DISTINCT ?document) AS ?count)
    WHERE {
        ?a oa:hasTarget [ oa:hasSource ?partOfArticle ].
        ?partOfArticle frbr:partOf+ ?document.
        ?document a fabio:ResearchPaper.
      	?a oa:hasBody ?entityUri.
    } GROUP BY ?entityUri
  }

  {
    ?entityUri skos:prefLabel ?entityLabel.
    FILTER (
      STRSTARTS(STR(?entityUri), "http://ns.inria.fr/d2kab/variety") ||
      STRSTARTS(STR(?entityUri), "http://ns.inria.fr/d2kab/gene")
    )
    BIND(
      IF(STRSTARTS(STR(?entityUri), "http://ns.inria.fr/d2kab/variety"),
        "Variety",
        IF(STRSTARTS(STR(?entityUri), "http://ns.inria.fr/d2kab/gene"), "Gene", "")
      )
      AS ?entityType
    )
  }
}
OFFSET %(offset)s  LIMIT %(limit)s
'''

if __name__ == "__main__":
    results_json = submit_sparql_query_chain(query_tpl, totalResults, limit)
    print("Writing the output to JSON file...")
    with open(f"../data/dumpEntitiesGeneVariety.json", 'w', encoding="utf-8") as f:
        f.write(results_json)
