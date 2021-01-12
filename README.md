# digital.learning.lab

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

The digital.learning.lab is a online platform and understands itself as competence centre for teaching in the digital age. School teachers will find suggestions and inspiration here for further developing their lessons, taking into account the competencies for a digitalised living and working environment.

## Want to jump in?

-   Bug hunt: Did you find a bug? Please check existing gitlab issues and create
    a new one if it is not listed yet.
-   Use Cases: How would you like to use this online platform for teaching concepts and school development in your contexts?
    Please describe your idea as a comment to this issue
-   Writing code: if you want to support the further code development, please fork the existing codebase and feel free, to reach out to us to step in
-   Discuss: Do you want to see additional features or have feedback about the
    software? Write us at <digital.learning.lab@tuhh.de>

## Current Main Features

-   Collection of good practices of teaching concepts (Unterrichtsbausteine), software applications (Tools) and webplatforms, publications and examples of organisation development for schools (Trends) in the digital age
-   Login option
    -   User account
    -   Development and publication of new content (Unterrichtsbausteine, Tools, Trends)
    -   collaboration of users for development of joint new content
    -   Review and release of contributions by authorised users

## Roadmap

Short term - What we are working on now 

-   cluster of tools
-   sequential development and submission of new content by users

Medium term - what we’re working on next! 

-   extended login section for school content planning
-   document management for teachers

Longer term items - working on this soon! 

-   social community for user
-   integration of media such as audio and video


## Local Development Setup
### 🛳 Container Setup 
1. Run `docker-compose up` to setup project.
2. Run `docker-compose run --rm web python manage.py migrate`
3. Create an `.env` file from `sample.env`

### 📦 Database Restore

If you'd like to restore a database dump leave out step 2 of the setup. Instead copy your
database dump into the database container and restore it:

```bash
docker cp ./local_path/to/db/dump [db-container-name]:/db_dump.bin
docker exec [db-container-name] pg_restore -U postgres -d postgres /backup/db_dump
```

The database container name can be retrieved by runnning `docker ps`.

Depending on the age of your database dump there may be new database migrations
which are not yet reflected in the database dump. This is usually the case when 
you're experiencing a `ProgrammingError` after restoring a database dump.

In that simply execute Django's migration command in the web container:
```bash
docker-compose run --rm web python manage.py migrate
```

At this point all content is available but not yet indexed for the search.
Setup Solr and run following command to index all contents:

```bash
docker-compose run --rm web python manage.py rebuild_index
```

### 🖼 Media File Restore
If you would like to restore the media files on your local development setup simply create 
a directory called `media` within the `dll` directory (`project_dir/dll/media/`) and copy 
`filer_public` as well as `filer_public_thumbnails` into it.

### 🦸 Superuser creation

You can create a super user by running the following command:
```bash
docker-compose run --rm web python manage.py createsuperuser
```

Please note the first and last name are mandatory fields. Leaving both fields empty may
cause problems.

### 🐍 Python Shell Access 

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

#### Update the schema
- `python manage.py build_solr_schema -f solr/conf/schema.xml`

### Testing

The digital.learning.lab platform comes with a testsuite, which can simply be 
extended and executed:

```bash
docker-compose exec web coverage run --source=/code/dll/ -m pytest /code/dll/
```