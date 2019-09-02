# Setup

1. Run `docker-compose up` to setup project.
2. Run `docker-compose run --rm web python manage.py migrate`
3. Clone content repo (https://collaborating.tuhh.de/itbh/tnt/digital-learning-lab/inhalte)
4. Run `docker-compose run --rm web python manage.py import_content -f ./path-to-inhalte`


# Solr

#### Setup
Instruct solr to use the `schema.xml` file:
- add `<schemaFactory class="ClassicIndexSchemaFactory"/>` in the solrconfig.xml
- remove the `AddSchemaFieldsUpdateProcessorFactory` section from `solrconfig.xml` ([source](https://stackoverflow.com/questions/31719955/solr-error-this-indexschema-is-not-mutable)) 
### Update the schema
- `python manage.py build_solr_schema > solr/conf/schema.xml`
- clear the weird output at the beginning of the xml file
- convert fields such as `date` to `pdate`
