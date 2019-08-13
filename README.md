# Setup

1. Run `docker-compose up` to setup project.
2. Run `docker-compose run --rm web python manage.py migrate`
3. Clone content repo (https://collaborating.tuhh.de/itbh/tnt/digital-learning-lab/inhalte)
4. Run `docker-compose run --rm web python manage.py import_content -f ./path-to-inhalte`
