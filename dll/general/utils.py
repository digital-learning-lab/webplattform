import re

from django.utils.text import slugify


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


def remove_number_custom_slugify(value):
    return custom_slugify(value     .strip('1234567890. '))


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
