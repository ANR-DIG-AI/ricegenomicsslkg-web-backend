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
prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
prefix rdfs:    <http://www.w3.org/2000/01/rdf-schema#> 
prefix xsd:     <http://www.w3.org/2001/XMLSchema#> 
prefix schema:  <http://schema.org/> 
prefix owl:     <http://www.w3.org/2002/07/owl#> 
prefix skos:    <http://www.w3.org/2004/02/skos/core#> 
prefix oa:      <http://www.w3.org/ns/oa#> 
prefix ncbi:    <http://identifiers.org/taxonomy/> 
prefix dct:     <http://purl.org/dc/terms/> 
prefix frbr:    <http://purl.org/vocab/frbr/core#> 
prefix fabio:   <http://purl.org/spar/fabio/> 
prefix obo:     <http://purl.obolibrary.org/obo/> 
prefix bibo: <http://purl.org/ontology/bibo/> 
prefix d2kab:   <http://ns.inria.fr/d2kab/> 
prefix dc: <http://purl.org/dc/terms/> 

SELECT ?entityUri ?entityLabel ?entityType (count(distinct ?paper) as ?count) 
FROM <http://ns.inria.fr/d2kab/graph/ricegenomicsslkg>
where {

?a1 a oa:Annotation; 
    oa:hasTarget [ oa:hasSource ?source1 ];  
    oa:hasBody ?entityUri.
    ?entityUri a ?entityType; skos:prefLabel ?entityLabel.

?source1 frbr:partOf+ ?paper.
?paper a fabio:ResearchPaper.
}
GROUP BY ?entityUri ?entityLabel ?entityType
HAVING (count(distinct ?paper) > 0)
ORDER BY DESC(?count)
'''


results_json = submit_sparql_query_chain(query_tpl, totalResults, limit)
print("Writing the output to JSON file...")
with open(f"../data/dumpEntitiesNCBIEntityTypes.json", 'w', encoding="utf-8") as f:
    f.write(results_json)
f.close()
print("Saved successfully !")
