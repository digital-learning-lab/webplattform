# Setup

1. Run `docker-compose up` to setup project.
2. Run `docker-compose run --rm web python manage.py migrate`
3. Clone content repo (https://collaborating.tuhh.de/itbh/tnt/digital-learning-lab/inhalte)
4. Run `docker-compose run --rm web python manage.py import_content -f ./path-to-inhalte`


# Solr 8.2

#### Setup
Instruct solr to use the `schema.xml` file:
- add `<schemaFactory class="ClassicIndexSchemaFactory"/>` in the solrconfig.xml
- remove the `AddSchemaFieldsUpdateProcessorFactory` section from `solrconfig.xml` ([source](https://stackoverflow.com/questions/31719955/solr-error-this-indexschema-is-not-mutable)) 
### Update the schema
- `python manage.py build_solr_schema -f solr/conf/schema.xml`


# JSON Data fields
### Content
```yaml
from_import: 
  type: Bool
  descr: created during import
```

### Review
contains the reviewer comments on the content fields

### DllUser
```yaml
from_import: 
  type: Bool
  descr: created during import
```
