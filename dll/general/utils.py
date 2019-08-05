import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.text import slugify


def get_default_tuhh_user():
    user, created = get_user_model().objects.get_or_create(
        username=settings.DEFAULT_USER_EMAIL,
        email=settings.DEFAULT_USER_EMAIL)
    if created:
        user.set_password(settings.DEFAULT_USER_PASSWORD)
        user.save()
    return user


def multiple_replace(dictionary, text):
    """
    Replace in 'text' all occurences of any key in the given
    dictionary by its corresponding value.  Returns the new string.
    source: http://code.activestate.com/recipes/81330-single-pass-multiple-replace/
    """

    # Create a regular expression  from the dictionary keys
    regex = re.compile("(%s)" % "|".join(map(re.escape, dictionary.keys())))

    # For each match, look-up corresponding value in dictionary
    return regex.sub(lambda mo: dictionary[mo.string[mo.start():mo.end()]], text)


def custom_slugify(value):
    mapping = {
        'ä': 'ae',
        'ö': 'oe',
        'ü': 'ue',
        'ß': 'ss'
    }
    value = multiple_replace(mapping, value)
    return slugify(value)


GERMAN_STATES = (
    ('nordrhein-westfalen', 'Nordrhein-Westfalen'),
    ('niedersachsen', 'Niedersachsen'),
    ('bayern', 'Bayern'),
    ('rheinland-pfalz', 'Rheinland-Pfalz'),
    ('hessen', 'Hessen'),
    ('saarland', 'Saarland'),
    ('berlin', 'Berlin'),
    ('brandenburg', 'Brandenburg'),
    ('schleswig-holstein', 'Schleswig-Holstein'),
    ('mecklenburg-vorpommern', 'Mecklenburg-Vorpommern'),
    ('thueringen', 'Thüringen'),
    ('sachsen', 'Sachsen'),
    ('sachsen-anhalt', 'Sachsen-Anhalt'),
    ('bremen', 'Bremen'),
    ('baden-wuerttemberg', 'Baden-Württemberg'),
    ('hamburg', 'Hamburg'),
)
