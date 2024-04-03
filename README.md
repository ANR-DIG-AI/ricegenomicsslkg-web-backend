# RiceGenomicsSLKG Web Application Backend Services

The [Rice Genomics Scientific Literature KG](https://github.com/ANR-DIG-AI/RiceGenomicsSLKG) (RiceGenomicsSLKG) is a FAIR knowledge graph that exploits
the Semantic Web technologies to integrate information about Named Entities (NE) extracted automatically from a corpus of
PubMed scientific articles on Rice genetics and genomics.

This repository is the backend part of a web application that demonstrates the interest and leveraging rich knowledge references.
It provides a set of Web APIs (services) used by the frontend application available in the [visualization repository](https://github.com/ANR-DIG-AI/ricegenomicsslkg-web-visualization).

## Services

The services exposed by the server are defined in [routes/index.js](routes/index.js).

With the exception of service `autoComplete`, the services submit SPARQL SELECT [queries](queries) to the D2kAB SPARQL endpoint (property SEMANTIC_INDEX_SPARQL_ENDPOINT in [.env](.env))
using the d3-sparql library.
The response of the services is the output of the d3-sparql library itself, that only returns the "results.bindings" part
of the SPARQL response in JSON format, following this format:

```json
{
  "result": [
    {
      "var1": "value1",
      "var2": "value2",
      ...
    },
    ...
]}
```

Therefore, the SELECT clause of the SPARQL queries are the de facto documentation of the services
since they give the names of the variables (var1 and var2 in the example above).

## Standalone deployment

Pre-requisite: [node.js](https://nodejs.org/) 17, yarn.

Install the dependencies with `yarn install`.

Run the application: `yarn start`

By default, the node.js server listens on port 3000. This can be changed in file [.env](.env).

Make sure the server is properly started and test the services by pointing your browser to:

```
http://localhost:3000/getArticleMetadata/?uri=https://pubmed.ncbi.nlm.nih.gov/10099937
http://localhost:3000/getArticleAuthors/?uri=https://pubmed.ncbi.nlm.nih.gov/10099937
http://localhost:3000/getAbstractNamedEntities/?uri=https://pubmed.ncbi.nlm.nih.gov/10099937
http://localhost:3000/autoComplete/?input=aestivum
http://localhost:3000/searchDocuments/?uri=http://purl.obolibrary.org/obo/NCBITaxon_49317
http://localhost:3000/searchDocumentsSubConcept/?uri=http://opendata.inrae.fr/wto/0000506
http://localhost:3000/searchDocumentsSubConcept/?uri=http://purl.obolibrary.org/obo/NCBITaxon_49317
```

In the `get*` services, uri is an example article that may no longer exist in the database at some point.

### Docker deployment

The repository comes with a Dockerfile and a docker-compose file.
After cloning, build the application with this command:

```
docker-compose build
```

Then start the services with:

```
docker-compose up -d
```

### Logging

Log traces are printed out in file `log/application.log`.

This can be changed by customizing file [config/log4js.json](config/log4js.json).
Refer to the [Log4JS documentation](https://stritti.github.io/log4js/).
