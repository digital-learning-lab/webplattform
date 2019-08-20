import glob
import logging
import os
import re

import dateparser
import numpy as np
import pandas as pd
from django.core.files import File
from django.core.management import BaseCommand
from django.utils import timezone
from filer.models import Image
from psycopg2._range import NumericRange

from dll.content.models import TeachingModule, ContentLink, Competence, SubCompetence, Trend, Tool, ToolApplication, \
    OperatingSystem, Subject, SchoolType, TrendLink, LICENCE_CHOICES, ToolLink
from dll.general.utils import custom_slugify
from dll.user.utils import get_default_tuhh_user
from dll.user.models import DllUser

logger = logging.getLogger('dll.importer')

TOOLS_KEYS_MAPPING = {
    1: 'digitalkompetenz',
    2: 'usk',
    3: 'registrieren',
    4: 'name',
    5: 'website',
    6: 'teaser',
    7: 'beschreibung',
    8: 'anwendung',
    9: 'betriebssystem',
    10: 'status',
    11: 'pro',
    12: 'kontra',
    13: 'datenschutz',
    14: 'nutzung',
    15: 'anmerkung',
    16: 'aehnliche_tools',
    17: 'video_anleitung',
    18: 'schr_anleitung',
}

TRENDS_KEYS_MAPPING = {
    1: 'kategorie',
    2: 'zielgruppe',
    3: 'sprache',
    4: 'digitalkompetenz',
    5: 'schlagworte',
    6: 'name',
    7: 'herausgeber',
    8: 'datum',
    9: 'teaser',
    10: 'zielsetzung',
    11: 'zInhalt',
    12: 'hintergrund',
    13: 'lizenz',
    14: 'zHinweis',
    15: 'aehnliche_trends',
    16: 'uBaustein',
    17: 'tool',
    18: 'website',
    19: 'weiterelinks',
}

TEACHING_MODULES_KEYS_MAPPING = {
    1: 'autor',
    2: 'name',
    3: 'lernziele',
    4: 'teaser',
    5: 'schulform',
    6: 'jahrgangsstufe',
    7: 'unterrichtsfach',
    8: 'fachkompetenz',
    9: 'digitalkompetenz',
    10: 'zeitumfang',
    11: 'tool',
    12: 'ausstattung',
    13: 'unterrichtsgeg',
    14: 'beschreibung',
    15: 'bildungsplanbezug',
    16: 'differenzierung',
    17: 'hinweise',
    18: 'schlagworte',
    19: 'medialinks',
    20: 'literaturlinks',
    21: 'bundesland',
    22: 'datum'
}


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('-f', '--folder', type=str)

    def handle(self, *args, **options):
        base_dir = options['folder']
        self.TOOLS_FOLDER = os.path.join(base_dir, 'Tool')
        self.TRENDS_FOLDER = os.path.join(base_dir, 'Trend')
        self.TEACHING_MODULES_FOLDER = os.path.join(base_dir, 'UBaustein')
        self._import_tools()
        self._import_teaching_modules()
        self._import_trends()

    @staticmethod
    def _read_xlsx_file(xlsx_file, content_type):
        data = {}

        if content_type == 'Tool':
            mapping = TOOLS_KEYS_MAPPING
            n_worksheets = 2
        elif content_type == 'Trend':
            mapping = TRENDS_KEYS_MAPPING
            n_worksheets = 3
        elif content_type == 'TeachingModule':
            mapping = TEACHING_MODULES_KEYS_MAPPING
            n_worksheets = 3
        else:
            return data

        for n in range(n_worksheets):
            logger.debug(f"Read worksheet {n} of {xlsx_file}")
            df = pd.read_excel(
                xlsx_file,
                sheet_name=n,
                header=1,
                usecols="A:C"
            )
            df = df.replace(np.nan, '', regex=True)
            df['#'] = df['#'].map(mapping)
            data.update(df.set_index('#')['Beispiel'].to_dict())

        return data

    def _import_tools(self):
        for folder in os.listdir(self.TOOLS_FOLDER):
            # Try to find the required files for import
            try:
                xlsx_file = glob.glob(os.path.join(self.TOOLS_FOLDER, folder, '*.xlsx'))[0]
            except IndexError:
                logger.warning("Missing xlsx file in folder {} for import".format(
                    os.path.join(self.TOOLS_FOLDER, folder)))
                continue

            # Try to read the content of the xlsx file
            try:
                data = self._read_xlsx_file(xlsx_file, content_type='Tool')
            except Exception as e:
                logger.exception(e)
                continue

            # Try to parse the fields
            try:
                logger.debug("Parse worksheet values {}".format(folder))
                status = self._parse_tool_status(data['status'])
                requires_registration = self._parse_tool_registration(data['registrieren'])
                usk = self._parse_tool_usk(data['usk'])
                privacy = self._parse_tool_privacy(data['datenschutz'])
            except Exception as e:
                logger.exception(e)
                pass

            author = get_default_tuhh_user()

            # Try to update/create the Tool
            try:
                logger.debug("Update or create Trend from folder {}".format(folder))
                tool, created = Tool.objects.drafts().update_or_create(
                    name=data['name'],
                    defaults={
                        # 'image': filer_image,
                        'author': author,
                        'teaser': data['teaser'],
                        'description': self._replace_semicolon_with_newline(data['beschreibung']),
                        'status': status,
                        'requires_registration': requires_registration,
                        'usk': usk,
                        'pro': self._parse_semicolon_separated_values(data['pro']),
                        'contra': self._parse_semicolon_separated_values(data['kontra']),
                        'privacy': privacy,
                        'usage': self._replace_semicolon_with_newline(data['nutzung']),
                        'additional_info': data['anmerkung'],
                        'base_folder': folder,
                    },
                )
                if created:
                    logger.info("Created new Trend from folder {}".format(folder))
                    # try to get the image
                try:
                    image_path = glob.glob(os.path.join(self.TOOLS_FOLDER, folder, '*.jpg'))[0]
                    image_name = folder + '.jpg'
                    tool.update_or_add_image_from_path(image_path, image_name=image_name)
                except IndexError:
                    logger.warning("Missing jpg file in folder {} for import".format(
                        os.path.join(self.TOOLS_FOLDER, folder)))
                except Exception as e:
                    logger.exception("Can not import image from folder {}".format(folder))
            except Exception as e:
                logger.exception(e)
                continue

            # Try to parse the competences
            try:
                logger.debug("Parse competences for Tool {}".format(folder))
                # make it a string first, because pandas parses single digits to integers
                competences = str(data['digitalkompetenz'])
                competence_list = list(filter(None, map(lambda x: x.strip(), competences.split(';'))))
                main_competences = self._parse_main_competences(competence_list)
                sub_competences = self._parse_sub_competences(competence_list)
                tool.competences.add(*main_competences)
                tool.sub_competences.add(*sub_competences)
            except ValueError:
                logger.warning("Could not parse competences for Tool {}".format(folder))
            except Exception as e:
                logger.exception(e)
                continue

            # Try to parse the links
            try:
                logger.debug("Parse links for Tool {}".format(folder))
                try:
                    text, href = self._parse_markdown_link(data['website'])
                    link = ToolLink.objects.create(
                        url=href,
                        name=text,
                        tool=tool
                    )
                except AttributeError:
                    logger.error('Could not parse link {} for Tool {}'.format(data['website'], folder))
                    continue

                for md_link in filter(None, data['schr_anleitung'].split(';')):
                    try:
                        text, href = self._parse_markdown_link(md_link)
                        link = ContentLink.objects.create(
                            url=href,
                            name=text,
                            content=tool,
                            type='literature'
                        )
                    except AttributeError:
                        logger.error('Could not parse link {} for Tool {}'.format(md_link, folder))
                        continue

                for md_link in filter(None, data['video_anleitung'].split(';')):
                    try:
                        text, href = self._parse_markdown_link(md_link)
                        link = ContentLink.objects.create(
                            url=href,
                            name=text,
                            content=tool,
                            type='video'
                        )
                    except AttributeError:
                        logger.error('Could not parse link {} for Tool {}'.format(md_link, folder))
                        continue

            except Exception as e:
                logger.exception(e)
                continue

            # Try to parse the applications
            try:
                apps = self._parse_tool_applications(data['anwendung'])
                tool.applications.add(*apps)
            except Exception as e:
                logger.exception(e)
                continue

            # Try to parse the operating systems
            try:
                tool.operating_systems.add(*self._parse_tools_os(data['betriebssystem']))
            except Exception as e:
                logger.exception(e)

            # Try to connect Tool to other content
            try:
                self._parse_related_content(tool, data)
            except Exception as e:
                logger.exception(e)

            # Try to publish the new Trend
            try:
                tool.publish()
            except Exception as e:
                logger.warning('Could not publish Tool {}'.format(folder))
                logger.exception(e)
                continue

    def _import_trends(self):
        for folder in os.listdir(self.TRENDS_FOLDER):
            # Try to find the required files for import
            try:
                xlsx_file = glob.glob(os.path.join(self.TRENDS_FOLDER, folder, '*.xlsx'))[0]
            except IndexError:
                logger.warning("Missing xlsx file in folder {} for import".format(
                    os.path.join(self.TRENDS_FOLDER, folder)))
                continue

            # Try to read the content of the xlsx file
            try:
                data = self._read_xlsx_file(xlsx_file, content_type='Trend')
            except Exception as e:
                logger.exception(e)
                continue

            # Try to parse the data
            try:
                licence = self._parse_trend_licence(data['lizenz'])
                if licence is None:
                    logger.warning("Could not parse licence {} for Trend {}.".format(data['lizenz'], folder))
                category = self._parse_trend_category(data['kategorie'])
                language = self._parse_trend_language(data['sprache'])
                if data['datum']:
                    publisher_date = data['datum']
                else:
                    publisher_date = None
                author = get_default_tuhh_user()
            except Exception as e:
                logger.exception(e)

            # Try to create the Trend
            try:
                logger.debug("Update or create Trend from folder {}".format(folder))
                trend, created = Trend.objects.drafts().update_or_create(
                    name=data['name'],
                    defaults={
                        'author': author,
                        'target_group': self._parse_semicolon_separated_values(data['zielgruppe']),
                        'category': category,
                        'publisher': self._parse_semicolon_separated_values(data['herausgeber']),
                        'publisher_date': publisher_date,
                        'language': language,
                        'teaser': data['teaser'],
                        'learning_goals': self._parse_semicolon_separated_values(data['zielsetzung']),
                        'central_contents': data['zInhalt'],
                        'licence': licence,
                        'additional_info': data['hintergrund'],
                        'citation_info': data['zHinweis'],
                        'base_folder': folder,
                    },
                )
                if created:
                    logger.info("Created new Trend from folder {}".format(folder))
                # try to get the image
                try:
                    image_path = glob.glob(os.path.join(self.TRENDS_FOLDER, folder, '*.jpg'))[0]
                    image_name = folder + '.jpg'
                    trend.update_or_add_image_from_path(image_path, image_name=image_name)
                except IndexError:
                    logger.warning("Missing jpg file in folder {} for import".format(
                        os.path.join(self.TRENDS_FOLDER, folder)))
                except Exception as e:
                    logger.exception("Can not import image from folder {}".format(folder))
            except Exception as e:
                logger.exception(e)
                continue

            # Try to parse the competences
            try:
                logger.debug("Parse competences for Trend {}".format(folder))
                # make it a string first, because pandas parses single digits to integers
                competences = str(data['digitalkompetenz'])
                competence_list = list(filter(None, map(lambda x: x.strip(), competences.split(';'))))
                main_competences = self._parse_main_competences(competence_list)
                sub_competences = self._parse_sub_competences(competence_list)
                trend.competences.add(*main_competences)
                trend.sub_competences.add(*sub_competences)
                trend.tags.add(*self._parse_tags(data['schlagworte']))
            except ValueError:
                logger.warning("Could not parse competences for Trend {}".format(folder))
            except Exception as e:
                logger.exception(e)
                continue

            # Try to parse the links
            try:
                logger.debug("Parse links for Trend {}".format(folder))
                for md_link in filter(None, data['weiterelinks'].split(';')):
                    try:
                        text, href = self._parse_markdown_link(md_link)
                        link = ContentLink.objects.create(
                            url=href,
                            name=text,
                            content=trend,
                            type='href'
                        )
                    except AttributeError:
                        logger.error('Could not parse link {} for Trend {}'.format(md_link, folder))
                        continue
                for md_link in filter(None, data['website'].split(';')):
                    try:
                        text, href = self._parse_markdown_link(md_link)
                        link = TrendLink.objects.create(
                            url=href,
                            name=text,
                            trend=trend,
                        )
                    except AttributeError:
                        logger.error('Could not parse link {} for Trend {}'.format(md_link, folder))
                        continue
            except Exception as e:
                logger.exception(e)
                continue

            # Try to connect Trend to other content
            try:
                self._parse_related_content(trend, data)
            except Exception as e:
                logger.exception(e)

            # Try to publish the new Trend
            try:
                trend.publish()
            except Exception as e:
                logger.warning('Could not publish Trend {}'.format(folder))
                logger.exception(e)
                continue

    def _import_teaching_modules(self):
        for folder in os.listdir(self.TEACHING_MODULES_FOLDER):
            # Try to find the required files for import
            try:
                xlsx_file = glob.glob(os.path.join(self.TEACHING_MODULES_FOLDER, folder, '*.xlsx'))[0]
            except IndexError:
                logger.warning("Missing xlsx file in folder {} for import".format(
                    os.path.join(self.TEACHING_MODULES_FOLDER, folder)))
                continue

            # Try to read the content of the xlsx file
            try:
                data = self._read_xlsx_file(xlsx_file, content_type='TeachingModule')
            except Exception as e:
                logger.exception(e)
                continue

            try:
                logger.debug("Get or create authors for TeachingModule {}".format(folder))
                authors = self._parse_authors(data['autor'])
            except Exception as e:
                logger.exception(e)
                continue

            try:
                state = self._parse_teaching_module_state(data.get('bundesland', None))
                if state is None:
                    logger.warning('No state specified for TeachingModule {}'.format(folder))

                try:
                    if 'datum' in data.keys():
                        date = dateparser.parse(data.get('datum'))
                    else:
                        date = timezone.now()
                except TypeError:
                    logger.warning('Could not parse date {} for TeachingModule {}'.format(data.get('datum'), folder))
                try:
                    class_range = self._parse_school_class_range(data['jahrgangsstufe'])
                    class_range = NumericRange(*class_range)
                except ValueError:
                    logger.warning('Can not parse school_class for TeachingModule {}. '
                                   'Value: {}'.format(folder, data['jahrgangsstufe']))
                    class_range = None
            except Exception as e:
                logger.exception(e)
                pass

            # Try to create a new TeachingModule with the content
            try:
                logger.debug("Update or create TeachingModule from folder {}".format(folder))
                teaching_module, created = TeachingModule.objects.drafts().update_or_create(
                    name=data['name'].strip(),
                    defaults={
                        'base_folder': folder,
                        'author': authors[0],
                        'learning_goals': self._parse_semicolon_separated_values(data['lernziele']),
                        'teaser': data['teaser'],
                        'expertise': self._parse_semicolon_separated_values(data['fachkompetenz']),
                        'estimated_time': self._parse_semicolon_separated_values(data['zeitumfang']),
                        'equipment': self._parse_semicolon_separated_values(data['ausstattung']),
                        'school_class': class_range,
                        'subject_of_tuition': self._parse_semicolon_separated_values(data['unterrichtsgeg']),
                        'description': data['beschreibung'],
                        'educational_plan_reference': data['bildungsplanbezug'],
                        'state': state,
                        'differentiating_attribute': data['differenzierung'],
                        'additional_info': data['hinweise'],
                        'modified': date,
                        'licence': 5  # "CC BY-NC-SA"
                    }
                )
                if created:
                    logger.info("Created new TeachingModule from folder {}".format(folder))
                # try to get the image
                try:
                    image_path = glob.glob(os.path.join(self.TEACHING_MODULES_FOLDER, folder, '*.jpg'))[0]
                    image_name = folder + '.jpg'
                    teaching_module.update_or_add_image_from_path(image_path, image_name=image_name)
                except IndexError:
                    logger.warning("Missing jpg file in folder {} for import".format(
                        os.path.join(self.TEACHING_MODULES_FOLDER, folder)))
                except Exception as e:
                    logger.exception("Can not import image from folder {}".format(folder))

                teaching_module.co_authors.add(*authors[1:])
                tags = self._parse_tags(data['schlagworte'])
                if any(map(lambda x: len(x) > 100, tags)):
                    logger.warning("Can not parse tags from xlsx file in folder {}. "
                                   "Tag is over 100 characters long".format(
                                    os.path.join(self.TEACHING_MODULES_FOLDER, folder)))
                else:
                    teaching_module.tags.add(*tags)

            except Exception as e:
                logger.exception(e)
                continue

            # Try to parse the competences
            try:
                logger.debug("Parse competences for TeachingModule {}".format(folder))
                # make it a string first, because pandas parses single digits to integers
                competences = str(data['digitalkompetenz'])
                competence_list = list(filter(None, map(lambda x: x.strip(), competences.split(';'))))
                main_competences = self._parse_main_competences(competence_list)
                sub_competences = self._parse_sub_competences(competence_list)
                teaching_module.competences.add(*main_competences)
                teaching_module.sub_competences.add(*sub_competences)
            except ValueError:
                logger.warning("Could not parse competences for TeachingModule {}".format(folder))
            except Exception as e:
                logger.exception(e)
                continue

            # Try to parse the links
            try:
                logger.debug("Parse links for TeachingModule {}".format(folder))
                for md_link in filter(None, data['medialinks'].split(';')):
                    try:
                        text, href = self._parse_markdown_link(md_link)
                        link = ContentLink.objects.create(
                            url=href,
                            name=text,
                            content=teaching_module,
                            type='href'
                        )
                    except AttributeError:
                        logger.error('Could not parse link {} for TeachingModule {}'.format(md_link, folder))
                        continue

                for md_link in filter(None, data['literaturlinks'].split(';')):
                    try:
                        text, href = self._parse_markdown_link(md_link)
                        link = ContentLink.objects.create(
                            url=href,
                            name=text,
                            content=teaching_module,
                            type='literature'
                        )
                    except AttributeError:
                        logger.error('Could not parse link {} for TeachingModule {}'.format(md_link, folder))
                        continue
            except Exception as e:
                logger.exception(e)
                continue

            # Try to add the different school types and Subjects
            try:
                for name in filter(None, map(lambda x: x.strip(), data['schulform'].split(';'))):
                    school_type, created = SchoolType.objects.get_or_create(name=name)
                    teaching_module.school_types.add(school_type)
                for name in filter(None, map(lambda x: x.strip(), data['unterrichtsfach'].split(';'))):
                    subject, created = Subject.objects.get_or_create(name=name)
                    teaching_module.subjects.add(subject)
            except Exception as e:
                logger.exception(e)

            # Try to connect TeachingModule to other content
            try:
                self._parse_related_content(teaching_module, data)
            except Exception as e:
                logger.exception(e)

            # Try to publish the new TeachingModule
            try:
                teaching_module.publish()
            except Exception as e:
                logger.warning('Could not publish TeachingModule {}'.format(folder))
                logger.exception(e)
                continue

    @staticmethod
    def _parse_related_content(obj, data):
        for name in filter(None, map(lambda x: x.strip(), data.get('aehnliche_trends', '').split(';'))):
            try:
                related_trend = Trend.objects.published().get(name=name)
                obj.related_content.add(related_trend)
            except Trend.DoesNotExist:
                related_trend = Trend(
                    name=name,
                    author=get_default_tuhh_user(),
                    publisher_is_draft=True
                )
                related_trend.json_data['from_import'] = True
                related_trend.save()
            except Trend.MultipleObjectsReturned:
                logger.error('Multiple Trends with the name ({name}) for {cls} in folder {folder}'.format(
                    name=name, cls=obj.__class__.__name__, folder=obj.base_folder))
        for name in filter(None, map(lambda x: x.strip(), data.get('uBaustein', '').split(';'))):
            try:
                related_teaching_module = TeachingModule.objects.published().get(name=name)
                obj.related_content.add(related_teaching_module)
            except TeachingModule.DoesNotExist:
                related_teaching_module = TeachingModule(
                    name=name,
                    author=get_default_tuhh_user(),
                    publisher_is_draft=True
                )
                related_teaching_module.json_data['from_import'] = True
                related_teaching_module.save()
            except TeachingModule.MultipleObjectsReturned:
                logger.error('Multiple TeachingModules with the name ({name}) for {cls} in folder {folder}'.format(
                    name=name, cls=obj.__class__.__name__, folder=obj.base_folder))
        for name in filter(None, map(lambda x: x.strip(), data.get('tool', '').split(';'))):
            try:
                related_tool = Tool.objects.published().get(name=name)
                obj.related_content.add(related_tool)
            except Tool.DoesNotExist:
                related_tool = Tool(
                    name=name,
                    author=get_default_tuhh_user(),
                    publisher_is_draft=True
                )
                related_tool.json_data['from_import'] = True
                related_tool.save()
            except Tool.MultipleObjectsReturned:
                logger.error('Multiple Tools with the name ({name}) for {cls} in folder {folder}'.format(
                    name=name, cls=obj.__class__.__name__, folder=obj.base_folder))

    @staticmethod
    def _import_image_from_path_to_folder(image_path, image_name, folder):
        file = File(open(image_path, 'rb'), name=image_name)
        filer_image = Image.objects.create(original_filename=image_name,
                                           file=file,
                                           folder=folder,
                                           owner=get_default_tuhh_user())
        return filer_image

    @staticmethod
    def _parse_school_class_range(value):
        if type(value) == int:
            return value, None
        elif type(value) == str:
            try:
                a, b = map(lambda x: int(x.strip()), value.split(';'))
            except ValueError:
                a = int(value.replace(';', ''))
                b = None

            return a, b
        else:
            raise ValueError

    @staticmethod
    def _parse_tags(value):
        gen = map(lambda x: custom_slugify(x.strip()), value.split(';'))
        gen = filter(None, gen)
        return list(gen)

    @staticmethod
    def _parse_semicolon_separated_values(value):
        return list(map(lambda x: x.strip(), value.split(';')))

    @staticmethod
    def _replace_semicolon_with_newline(value):
        return value.replace(';', '\n')

    @staticmethod
    def _parse_markdown_link(value):
        m = re.match(r"\[([^\[\]]+)\]\(([^)]+)", value)
        text, href = m.group(1, 2)
        return text, href

    @staticmethod
    def _parse_links(value):
        links = []
        l = filter(None, map(lambda x: x.strip(), value.split(';')))
        for s in l:
            m = re.match(r"\[([^\[\]]+)\]\(([^)]+)", s)
            text, href = m.group(1, 2)
            links.append({'text': text, 'href': href})
        return links

    @staticmethod
    def _parse_authors(value):
        """Returns a list of DllUser instances. First item is the author, all following authors are co-authors"""
        author_list = []
        authors = filter(None, value.split(';'))
        if authors:
            for author in authors:
                autogenerated_email = custom_slugify(author) + "@dll.web"
                obj, created = DllUser.objects.get_or_create(
                    email=autogenerated_email,
                )
                if created:
                    obj.username = author
                    obj.json_data['from_import'] = True
                    password = author.split()[-1] + '_dll_2019'
                    obj.set_password(password)
                    obj.save()
                author_list.append(obj)
        else:
            author_list.append(get_default_tuhh_user())
        return author_list

    @staticmethod
    def _parse_main_competences(lst):
        main_competences = []
        parsed_lst = set(map(lambda x: int(x[0]), lst))
        for i in parsed_lst:
            competence, created = Competence.objects.get_or_create(cid=i)
            main_competences.append(competence)
        return main_competences

    @staticmethod
    def _parse_sub_competences(lst):
        sub_competences = []
        parsed_lst = filter(lambda x: len(x) > 1, lst)
        parsed_lst = map(lambda x: int(x.replace('.', '')), parsed_lst)
        for i in parsed_lst:
            sub_competence, created = SubCompetence.objects.get_or_create(cid=i)
            sub_competences.append(sub_competence)
        return sub_competences

    @staticmethod
    def _parse_trend_category(value):
        mapping = dict(map(lambda x: x[::-1], Trend.CATEGORY_CHOICES))
        try:
            return mapping[value]
        except KeyError:
            logger.warning("Could not parse value for Trend licence {}. Default to None".format(value))
            return None

    @staticmethod
    def _parse_trend_language(value):
        mapping = dict(map(lambda x: x[::-1], Trend.LANGUAGE_CHOICHES))
        try:
            return mapping[value]
        except KeyError:
            logger.warning("Could not parse value for Trend licence {}. Default to None".format(value))
            return 'german'

    @staticmethod
    def _parse_trend_licence(value):
        mapping = dict(map(lambda x: x[::-1], LICENCE_CHOICES))
        try:
            return mapping[value]
        except KeyError:
            return 2

    @staticmethod
    def _parse_tool_status(value):
        try:
            if value in dict(Tool.STATUS_CHOICES).keys():
                return value
        except KeyError:
            logger.warning("Could not parse value for Tool status {}. Default to None".format(value))
            return None

    @staticmethod
    def _parse_tool_registration(value):
        try:
            if int(value) == 0:
                return False
            elif int(value) == 1:
                return True
            else:
                raise ValueError
        except ValueError:
            logger.warning("Could not parse value for Tool registration {}. Default to True".format(value))
            return None

    @staticmethod
    def _parse_tool_usk(value):
        if value in dict(Tool.USK_CHOICES).keys():
            return value
        else:
            logger.warning("Could not parse value for Tool licence {}. Default to usk18".format(value))
            return None

    @staticmethod
    def _parse_tool_privacy(value):
        try:
            return int(value)
        except ValueError:
            logger.warning("Could not parse value for Tool privacy {}. Default to 4".format(value))
            return 4

    @staticmethod
    def _parse_tool_applications(value):
        applications_list = []
        lst = value.split(';')
        for i in lst:
            app, created = ToolApplication.objects.get_or_create(name=i)
            applications_list.append(app)
        return applications_list

    @staticmethod
    def _parse_teaching_module_state(value):
        if value is None:
            return None
        else:
            return custom_slugify(value)

    @staticmethod
    def _parse_tools_os(value):
        os_lst = []
        for name in filter(None, map(lambda x: x.strip(), value.split(';'))):
            op_sys, created = OperatingSystem.objects.get_or_create(name=name)
            os_lst.append(op_sys)
        return os_lst
