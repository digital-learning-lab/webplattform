# digital.learning.lab

## Local Development Setup
### Container Setup 🛳
1. Run `docker-compose up` to setup project.
2. Run `docker-compose run --rm web python manage.py migrate`


### Database Restore 📦

If you'd like to restore a database dump leave out step 2 of the setup. Instead copy your
database dump into the database container and restore it:

```bash
docker cp ./local_path/to/db/dump [db-container-name]:/backup/db_dump
docker exec [db-container-name] pg_restore -U postgres -d postgres /backup/db_dump
```

The database container name can be retrieved by runnning `docker ps`.

### Media File Restore 🖼
If you would like to restore the media files on your local development setup simply create 
a directory called `media` within the `dll` directory (`project_dir/dll/media/`) and copy 
`filer_public` as well as `filer_public_thumbnails` into it.

### Superuser creation 🦸‍

You can create a super user by running the following command:
```bash
docker-compose run --rm web python manage.py createsuperuser
```

Please note the first and last name are mandatory fields. Leaving both fields empty may
cause problems.

### Python Shell Access 🐍

In some cases it is useful to be able to access the Python shell of the web container:

```bash
docker-compose run --rm web python manage.py shell_plus
```

The `shell_plus` is a part of the `django-extensions` package. It automatically imports 
all project relevant models and some helper functions.

### Solr 8.2

#### Setup
Instruct solr to use the `schema.xml` file:
- add `<schemaFactory class="ClassicIndexSchemaFactory"/>` in the solrconfig.xml
- remove the `AddSchemaFieldsUpdateProcessorFactory` section from `solrconfig.xml` ([source](https://stackoverflow.com/questions/31719955/solr-error-this-indexschema-is-not-mutable)) 
### Update the schema
- `python manage.py build_solr_schema -f solr/conf/schema.xml`


### JSON Data fields
#### Content
```yaml
from_import: 
  type: Bool
  descr: created during import
```

#### Review
contains the reviewer comments on the content fields

#### DllUser
```yaml
from_import: 
  type: Bool
  descr: created during import
```
