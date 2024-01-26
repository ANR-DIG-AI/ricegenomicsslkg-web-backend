"""
This script retrieves the labels and URIs of the  concepts that are used
as named entities of at least one article in the dataset.
The additional field 'count' gives the number of articles that have that concept and label as a named entity.

The result is used by the auto-completion of user inputs on the search form.
"""

from SPARQLQuery import submit_sparql_query_chain

limit = 10000
totalResults = 7000

query_tpl = '''
PREFIX fabio:   <http://purl.org/spar/fabio/>
PREFIX frbr:    <http://purl.org/vocab/frbr/core#>
PREFIX oa:      <http://www.w3.org/ns/oa#>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?entityUri ?entityLabel ?entityPrefLabel ?count ?entityType
FROM NAMED <http://ns.inria.fr/d2kab/graph/wheatgenomicsslkg>
FROM NAMED <http://purl.obolibrary.org/obo/ncbitaxon/ncbitaxon.owl>
WHERE {
    { # This sub-query basically selects the URIs for which we want to have auto-completion.
      # It returns each unique NCBI entity that is either a NE or a parent of a NE.
      # Example: if a document d has NE A, and A is an instance or subclass of B,
      # then the query returns 2 couples: (d, A) and (d, B).

	  SELECT DISTINCT ?entityUri (count(DISTINCT ?document) as ?count)
      FROM <http://ns.inria.fr/d2kab/graph/wheatgenomicsslkg>
      FROM NAMED <http://purl.obolibrary.org/obo/ncbitaxon/ncbitaxon.owl>
      WHERE {
        ?a oa:hasTarget [ oa:hasSource ?partOfArticle ].
        ?partOfArticle frbr:partOf+ ?document.
        ?document a fabio:ResearchPaper.

        { ?a oa:hasBody ?entityUri. }
        UNION
        { ?a oa:hasBody ?body. { graph <http://purl.obolibrary.org/obo/ncbitaxon/ncbitaxon.owl> { ?body rdfs:subClassOf+ ?entityUri. }}}
      } GROUP BY ?entityUri
    }

    { # This sub-query retrieves all the NCBI resources and their labels.
      # All labels, preferred and alternate, are given in ?entityLabel.
      # ?entityPrefLabel is optional, it gives the preferred label in case ?entityLabel contains an alternate label.
      GRAPH <http://purl.obolibrary.org/obo/ncbitaxon/ncbitaxon.owl> {
        { ?entityUri rdfs:label ?entityLabel. }
        UNION
        { ?entityUri <http://www.geneontology.org/formats/oboInOwl#hasExactSynonym> ?entityLabel; rdfs:label ?entityPrefLabel }
      }
    }

    BIND("Taxon" as ?entityType)
}
OFFSET %(offset)s  LIMIT %(limit)s
'''

results_json = submit_sparql_query_chain(query_tpl, totalResults, limit)
print("Writing the output to JSON file...")
with open(f"../data/dumpEntitiesNCBITaxon.json", 'w', encoding="utf-8") as f:
    f.write(results_json)
