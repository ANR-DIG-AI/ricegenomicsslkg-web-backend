"""
This script retrieves the labels and URIs of the  concepts that are used
as  of at least one article in the dataset.
The additional field 'count' gives the number of articles that have that concept and label as a .

The result is used the auto-completion of user inputs on the search form.
"""

import json
from SPARQLWrapper import SPARQLWrapper, JSON, POST
import json
import math

endpoint = "http://d2kab.i3s.unice.fr/sparql"
limit = 1234
totalResults = 1234

prefixes = '''
PREFIX oa:     <http://www.w3.org/ns/oa#>
PREFIX skos:   <http://www.w3.org/2004/02/skos/core#>
prefix frbr:    <http://purl.org/vocab/frbr/core#>
prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
PREFIX schema: <http://schema.org/>
'''

query_tpl = prefixes + '''
SELECT DISTINCT ?entityUri ?entityLabel ?entityPrefLabel (COUNT(?document) AS ?count) ?source
FROM NAMED <http://ns.inria.fr/d2kab/graph/wheatgenomicsslkg>
WHERE {
  {
    SELECT DISTINCT ?entityUri ?document 
    WHERE {
    
      GRAPH <http://ns.inria.fr/d2kab/graph/wheatgenomicsslkg> {
        ?document a schema:ScholarlyArticle.
        ?namedEntity oa:hasBody ?entityUri; oa:hasTarget [ oa:hasSource ?partOfArticle ] .
        ?partOfArticle frbr:partOf+ ?document.
      }
    }
  }

  GRAPH <http://ns.inria.fr/d2kab/graph/wheatgenomicsslkg> {
    ?entityUri skos:prefLabel ?entityLabel.
    BIND(
      IF(STRSTARTS(STR(?entityUri), "http://ns.inria.fr/d2kab/variety"), "Variety",
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


def sparql_endpoint_call(query):
    """
    Simple execution of a SELECT SPARQL query with JSON response
    """
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results


if __name__ == '__main__':
    try:
        output = []
        for index in range(math.floor(totalResults/limit) + 1):
            offset = index * limit
            print(
                f"Querying SPARQL endpoint [limit: {limit}, offset: {offset}]...")
            results = sparql_endpoint_call(
                query_tpl % {"limit": limit, "offset": offset})

            # Simplify the SPARQL JSON format to keep only the values
            print("Reformatting output...")
            for row in results['results']['bindings']:
                item = {}
                item['entityUri'] = row['entityUri']['value']
                item['entityLabel'] = row['entityLabel']['value']
                if 'entityPrefLabel' in row:
                    item['entityPrefLabel'] = row['entityPrefLabel']['value']
                item['count'] = row['count']['value']
                item['source'] = row['source']['value']
                output.append(item)
            # print(results_json)

        print("Formatting the JSON output...")
        results_json = json.dumps(output, indent=4)
        print("Writing the output to JSON file...")
        with open(f"data/dumpEntitiesGeneVariety.json", 'w', encoding="utf-8") as f:
            f.write(results_json)

    except Exception as e:
        print('Error while processing SPARQL query: ' + str(e))
        exit
