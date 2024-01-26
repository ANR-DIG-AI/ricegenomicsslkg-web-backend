# Generation of files used by the auto-complete service

The `autoComplete` service must complete the user's input against the labels of the named entities used in the annotations of articles. 
It must also be capable of completing an input with labels of classes or concepts whose instances, sub-classes or sub-concepts are used in annotations.
Example: WTO trait `response to environmental condition` is usually not used as a named entity, but its sub-classes and instances are.
Therefore, the user must be able to type this label and get the articles whose named entities are its sub-classes of instances of its sub-classes.

The service does not directly query the SPARQL endpoint as this would be far too slow for smooth interaction.
Instead, it relies on JSON files (stored in [../data](../data)) that list all the entities with their preferred and alternate labels.

These files are generated beforehand by the scripts in this folder. 
For each entity, they include a count of the number of times they are used as annotations.
