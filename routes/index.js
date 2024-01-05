let express = require('express');
let fs = require('fs');
let logger = require("../modules/logger");
let d3 = require('d3-sparql');
require('dotenv').config();

let log = logger.application;
let router = express.Router();
let entitiesJson = require('../data/dumpEntities.json')

log.info('Starting up backend services');


/**
 * Read a SPARQL query template and replace the {id} placeholder
 * @param {string} template - the template file name
 * @param {number} id - value to replace "{id}" with
 * @returns {string} SPARQL query string
 */
function readTemplate(template, id) {
    let queryTpl = fs.readFileSync('queries/' + template, 'utf8');
    return queryTpl.replaceAll("{id}", id);
}


/**
 * Sort 2 strings in case-insensitive alphabetic order
 * @param {string} a
 * @param {string} b
 * @returns {number}
 */
function sortStrings(a, b) {
    let aa = a.entityLabel.toLowerCase();
    let bb = b.entityLabel.toLowerCase();
    if (aa < bb)
        return -1;
    if (aa > bb)
        return 1;
    return 0;
}


/**
 * Split a string formatted like "URI$label$$URI$label$$..." into a document like
 * [ { "entityUri": "URI", "entityLabel": "label" }, { "entityUri": "URI", "entityLabel": "label" } ... ]
 *
 * @param {string} str - input string to process
 * @returns {array} - array of documents
 */
function splitDollar(str) {
    let result = [];
    str.split('$$').forEach(_e => {
        let [uri, label] = _e.split('$');
        result.push({entityUri: uri, entityLabel: label});
    });
    return result;
}


/**
 * Get article metaData (title , date , articleType ... )  without the authors
 * @param {string} uri - URI of the document
 * @return {document} - The output is shaped as in the example below:
 * {
 *   "result": [
 *     {
 *       "title": "Ectopic expression of alpha B-crystallin in Chinese hamster ovary cells suggests a nuclear role for this protein.",
 *       "date": "1999",
 *       "pub": "European journal of cell biology",
 *       "lang": "eng",
 *       "abs": "alpha B-crystallin (alpha B) is known to be a cytosolic..."
 *     }
 *   ]
 * }
 */
router.get('/getArticleMetadata/', (req, res) => {
    let articleUri = req.query.uri;
    log.info('getArticleMetadata - uri: ' + articleUri);
    let query = readTemplate("getArticleMetadata.sparql", articleUri);
    if (log.isDebugEnabled()) {
        log.debug('getArticleMetadata - Will submit SPARQL query: \n' + query);
    }

    (async () => {
        let result;
        try {
            result = await d3.sparql(process.env.SEMANTIC_INDEX_SPARQL_ENDPOINT, query).then((data) => {
                if (log.isTraceEnabled()) {
                    log.trace('getArticleMetadata - SPARQL response: ');
                    data.forEach(res => log.trace(res));
                }
                return data;
            }).then(res => res);

        } catch (err) {
            log.error('getArticleMetadata error: ' + err);
            result = err;
        }
        res.status(200).json({result});
    })()
});


/**
 * GET article authors
 * @param {string} uri - URI of the document
 * @return {document} - The output is shaped as in the example below:
 * {
 *   "result": [
 *     {
 *       "authors": "Hale IL"
 *     },
 *     {
 *       "authors": "Bhat SP"
 *     }
 *     ...
 *   ]
 * }
 */
router.get('/getArticleAuthors/', (req, res) => {
    let articleUri = req.query.uri;
    log.info('getArticleAuthors - uri: ' + articleUri);
    let query = readTemplate("getArticleAuthors.sparql", articleUri);
    if (log.isDebugEnabled()) {
        log.debug('getArticleAuthors - Will submit SPARQL query: \n' + query);
    }

    (async () => {
        let result;
        try {
            result = await d3.sparql(process.env.SEMANTIC_INDEX_SPARQL_ENDPOINT, query).then((data) => {
                if (log.isTraceEnabled()) {
                    log.trace('getArticleAuthors - SPARQL response: ');
                    data.forEach(res => log.trace(res));
                }
                return data;
            }).then(res => res);

        } catch (err) {
            log.error('getArticleAuthors error: ' + err);
            result = err;
        }
        res.status(200).json({result});
    })()
});


/**
 * Get named entities
 * @param {string} uri - URI of the document
 */
router.get('/getAbstractNamedEntities/', (req, res) => {
    let articleUri = req.query.uri;
    log.info('getAbstractNamedEntities - uri: ' + articleUri);
    let query = readTemplate("getNamedEntities.sparql", articleUri);
    if (log.isDebugEnabled()) {
        log.debug('getNamedEntities - Will submit SPARQL query: \n' + query);
    }

    (async () => {
        let result;
        try {
            result = await d3.sparql(process.env.SEMANTIC_INDEX_SPARQL_ENDPOINT, query).then((data) => {
                if (log.isTraceEnabled()) {
                    log.trace('getNamedEntities - SPARQL response: ');
                    data.forEach(res => log.trace(res));
                }
                return data;
            }).then(res => res);

        } catch (err) {
            log.error('getAbstractNamedEntities error: ' + err);
            result = err;
        }
        res.status(200).json({result});
    })()
});


/**
 * Complete the user's input using entities labels.
 *
 * @param {string} input - first characters entered by the use
 * @return {document} - The output is a JSON array whose documents are shaped as in the example below:
 *     {
 *         "entityUri": "http://aims.fao.org/aos/agrovoc/c_4459",
 *         "entityLabel": "Luffa cylindrica",
 *         "entityPrefLabel": "Luffa aegyptica",
 *         "count": "1"
 *     }
 * entityPrefLabel is optional, it gives the preferred label in case entityLabel is not the preferred label.
 * "Count" is the number of documents in the knowledge base that are assigned the named entity with this URI/label.
 */
router.get('/autoComplete/', (req, res) => {
    let input = req.query.input.toLowerCase();
    if (log.isDebugEnabled()) {
        log.debug('autoComplete - input: ' + input);
    }

    // Count the number of entities selected (to return ony a maximum number)
    let _count = 0;

    // Search for entities whose label starts like the input
    let _startsWith = entitiesJson.filter(_entity => {
        if (_count < process.env.SEARCH_MAX_AUTOCOMPLETE) {
            if (_entity.entityLabel.toLowerCase().startsWith(input)) {
                _count++;
                return true;
            }
        } else return false;
    }).sort(sortStrings);

    if (log.isTraceEnabled()) {
        log.trace('autoComplete - Result _startsWith: ');
        _startsWith.forEach(res => log.trace(res));
    }

    let _includes = entitiesJson.filter(_entity => {
        if (_count < process.env.SEARCH_MAX_AUTOCOMPLETE) {
            let _entityLabLow = _entity.entityLabel.toLowerCase()

            // Find entities whose label includes the input but that was not already selected above
            if (_entityLabLow.includes(input) &&
                !_startsWith.some(_s => _s.entityLabel.toLowerCase() === _entityLabLow && _s.entityUri === _entity.entityUri)) {
                _count++;
                return true;
            }
        } else return false;
    }).sort(sortStrings);

    if (log.isTraceEnabled()) {
        log.trace('autoComplete - Result includes: ');
        _includes.forEach(res => log.trace(res));
    }

    res.status(200).json(_startsWith.concat(_includes));
});


/**
 * Search for documents annotated with a set of named entities  given by their URIs
 * @param {string} uri - URIs of the named entities to search, passed on the query string either as "uri=a,b,..." or "uri=a&uri=b&..."
 * @return {document} - output like this:
 * {
 *   "result": [
 *     {
 *       "document": "http://data-issa.cirad.fr/document/585171",
 *       "title": "The endless palm oil debate: Science-based solutions beyond controversies",
 *       "date": "2017",
 *       "authors": [
 *         "Alain Rival", "X Y"
 *       ]
 *     },
 *     ...
 * }
 */
router.get('/searchDocuments/', (req, res) => {
    let uri = req.query.uri;
    log.info('searchDocuments - uri: [' + uri + ']');

    if (uri.length === 0) {
        log.info('searchDocuments - no parameter, returning empty SPARQL response');
        res.status(200).json({result: []});
    } else {

        // Create the SPARQL triple patterns to match each one of the URIs
        let lines = '';
        let i = 0;

        let uris = uri.split(',');
        uris.forEach(_uri => {
            let lineTpl = '?annotation' + i + ' oa:hasBody <{uri}>; oa:hasTarget [ oa:hasSource ?articleUriAbstract' + i + ' ] .?articleUriAbstract' + i + ' frbr:partOf+ ?document.';
            lines += lineTpl.replaceAll("{uri}", _uri) + '\n';
            i = i + 1;
        })

        // Insert the triple patterns into the SPARQL query
        let queryTpl = fs.readFileSync('queries/searchArticle.sparql', 'utf8');
        let query = queryTpl.replace("{triples}", lines);
        if (log.isDebugEnabled()) {
            log.debug('searchDocuments - Will submit SPARQL query: \n' + query);
        }

        (async () => {
            let result = [];
            try {
                result = await d3.sparql(process.env.SEMANTIC_INDEX_SPARQL_ENDPOINT, query).then((data) => {
                    log.info('searchDocuments returned ' + data.length + ' results');
                    // Turn string authors into an array
                    data = data.map(_r => {
                        _r.authors = _r.authors.split('$');
                        return _r;
                    });
                    if (log.isTraceEnabled()) {
                        log.trace('searchDocuments - SPARQL response: ');
                        data.forEach(res => log.trace(res));
                    }
                    return data;
                }).then(res => res);

            } catch (err) {
                log.error('searchDocuments error: ' + err);
                result = err;
            }
            res.status(200).json({result: result});
        })()
    }
});


/**
 * Search for the documents that are annotated with a set of named entities {id} or any of their sub-concepts/sub-classes.
 *
 * @param {string} uri - URIs of the named entities to search, passed on the query string either as "uri=a,b,..." or "uri=a&uri=b&..."
 * @return {document} - output like this:
 *
 * {
 *   "result": [
 *     {
 *       "document": "http://data-issa.cirad.fr/document/601515",
 *       "title": "Transformation of coffee-growing across Latin America",
 *       "date": "2022",
 *       "authors": [
 *         "Armbrecht, Inge", "Avelino, Jacques", "Barrera, Juan Francisco"
 *       ],
 *       "matchedEntities": [{
 *           "entityUri": "http://aims.fao.org/aos/agrovoc/c_33561",
 *           "entityLabel": "sustainable agriculture"
 *         },
 *         ...
 *       ]
 *     },
 *     ...
 * }
 */
router.get('/searchDocumentsSubConcept/', async (req, res) => {
    let uri = req.query.uri;
    log.info('searchDocumentsSubConcept - uri: [' + uri + ']');

    if (uri.length === 0) {
        log.info('searchDocumentsSubConcept - no parameter, returning empty response');
        res.status(200).json({result: []});
    } else {

        // Submit one SPARQL query for each URI
        let uris = uri.split(',');
        let promises = [];
        uris.forEach(_uri => {
            // Get the source KG of the current _uri from the list of entities (dumpEntities.json)
            let _source = getSourceFromJson(_uri);
            if (log.isDebugEnabled()) {
                log.debug(`searchDocumentsSubConcept - Source for uri ${_uri}: ${_source}`);
            }

            let query;
            switch (_source) {
                case "Taxon":
                    query = readTemplate("searchArticleSubConceptNCBI.sparql", _uri);
                    break;
                case "Phenotype or trait":
                    query = readTemplate("searchArticleSubConceptWTO.sparql", _uri);
                    break;
                default:
                    log.error(`searchDocumentsSubConcept - Unknown source for uri ${_uri}: ${_source}`);
                    query = '';
            }

            if (query !== '') {
                if (log.isDebugEnabled()) {
                    log.debug('searchDocumentsSubConcept - Will submit SPARQL query: \n' + query);
                }

                // Submit the SPARQL query and save the promise
                let _promise = (async () => {
                    let _result = [];
                    try {
                        _result = await d3.sparql(process.env.SEMANTIC_INDEX_SPARQL_ENDPOINT, query).then((data) => {
                            log.info('searchDocumentsSubConcept: query for uri ' + _uri + ' returned ' + data.length + ' results');
                            return data;
                        }).then(res => res);
                    } catch (err) {
                        log.error('searchDocumentsSubConcept error: ' + err);
                        _result = err;
                    }
                    return _result;
                })();
                promises.push(_promise);
            }
        });

        // Wait for all the responses (promises) and compute the intersection of all of them based on the document URIs
        let joinedResults = [];
        Promise.allSettled(promises).then((_promises) => {

            // Iterate on the results of each SPARQL query
            _promises.forEach((_promise, index) => {
                if (index === 0) {
                    // First promise: initialize the intersection with the first set of results
                    joinedResults = _promise.value.map(_r => {
                        // Turn string matchedEntities into an array
                        _r.matchedEntities = splitDollar(_r.matchedEntities);

                        // Turn string authors into an array
                        _r.authors = _r.authors.split('$');

                        return _r;
                    });
                } else {
                    // Remove, from the current intersection, the documents that are not mentioned in the results of the current promise
                    joinedResults = joinedResults.filter(_r => _promise.value.some(_n => _n.document === _r.document));

                    // Join the matched entities of each result in the current intersection with
                    // the matched entities of the corresponding result of the current promise
                    joinedResults = joinedResults.map(_r => {
                        let newResult = _promise.value.find(_n => _n.document === _r.document);
                        let _matchedEntitiesAr = splitDollar(newResult.matchedEntities);
                        _matchedEntitiesAr.forEach(_e => {
                            if (!_r.matchedEntities.some(_me => _me.entityUri === _e.entityUri))
                                _r.matchedEntities.push(_e);
                        });
                        return _r;
                    });
                }
                log.info("searchDocumentsSubConcept: current number of results : " + joinedResults.length);
            });
            log.info("searchDocumentsSubConcept: returning : " + joinedResults.length + " results");
            res.status(200).json({"result": joinedResults});
        });
    }
});


/**
 * Get the name of the source KG of one entity (given by its URI) from the list of entities (dumpEntities.json)
 * @param uri
 * @return {*|string|string}
 */
function getSourceFromJson(uri) {
    try {
        let entityData = entitiesJson.find(_entry => uri.includes(_entry.entityUri));
        return entityData ? entityData.source : "Unknown";
    } catch (err) {
        console.error('Error reading dumpEntities.json: ' + err);
        return "Unknown";
    }
}

module.exports = router;
