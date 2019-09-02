# Setup

1. Run `docker-compose up` to setup project.
2. Run `docker-compose run --rm web python manage.py migrate`
3. Clone content repo (https://collaborating.tuhh.de/itbh/tnt/digital-learning-lab/inhalte)
4. Run `docker-compose run --rm web python manage.py import_content -f ./path-to-inhalte`


# Solr
### Update the schema
`python manage.py build_solr_schema > solr/schema.xml`
#### Instruct solr to use the `schema.xml` file
- add `<schemaFactory class="ClassicIndexSchemaFactory"/>` in the solrconfig.xml
## Solr errors:
`dll-default: org.apache.solr.common.SolrException:org.apache.solr.common.SolrException: fieldType 'pdates' not found in the schema` 
https://github.com/nextcloud/fulltextsearch/issues/208
```xml
<fieldType name="pdate" class="solr.DatePointField" docValues="true"/>
<fieldType name="pdates" class="solr.DatePointField" docValues="true" multiValued="true"/>
<dynamicField name="*_pdts" type="pdates" indexed="true" stored="true"/>
```
