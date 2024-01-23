import json
import math
from SPARQLWrapper import SPARQLWrapper, JSON, POST

endpoint = "http://d2kab.i3s.unice.fr/sparql"

def submit_sparql_query(endpoint, query):
    """
    Simple execution of a SELECT SPARQL query with JSON response
    """
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    return results

def submit_sparql_query_chain(query_tpl, totalResults, maxResultsPerQuery):
    """
    Submits (potentially) multiple times the same query with increasing offset in order to safely gather all the results
    """
    try:
        output = []
        for index in range(math.floor(totalResults/maxResultsPerQuery) + 1):
            offset = index * maxResultsPerQuery
            print(f"Querying SPARQL endpoint [limit: {maxResultsPerQuery}, offset: {offset}]...")
            results = submit_sparql_query(endpoint, query_tpl % {"limit": maxResultsPerQuery, "offset": offset})

            # Simplify the SPARQL JSON format to keep only the values
            print("Reformatting output...")
            for row in results['results']['bindings']:
                item = {}
                item['entityUri'] = row['entityUri']['value']
                item['entityLabel'] = row['entityLabel']['value']
                if 'entityPrefLabel' in row:
                    item['entityPrefLabel'] = row['entityPrefLabel']['value']
                item['count'] = row['count']['value']
                item['entityType'] = row['entityType']['value']
                output.append(item)

        print("Formatting the JSON output...")
        results_json = json.dumps(output, indent=4)
        return results_json

    except Exception as e:
        print('Error while processing SPARQL query: ' + str(e))
        exit
