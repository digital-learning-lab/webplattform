from django.test import TestCase
from django.urls import reverse

from dll.content.models import Tool, TeachingModule, Trend, ToolLink, Competence, SubCompetence
from dll.user.models import DllUser


class BaseTestCase(TestCase):
    def setUp(self):
        content_list = [
            {'model': Tool, 'name': 'Tool Fusce egestas', 'teaser': 'Fusce ac felis sit amet ligula pharetra condimentum.'},
            {'model': Tool, 'name': 'Tool Duis leo', 'teaser': 'Aliquam eu nunc..'},
            {'model': TeachingModule, 'name': 'TeachingModule Ut a', 'teaser': 'Vivamus quis mi. In ac felis quis tortor malesuada pretium.'},
            {'model': TeachingModule, 'name': 'TeachingModule Proin pretium', 'teaser': 'Nam adipiscing. In auctor lobortis lacus.'},
            {'model': Trend, 'name': 'Trend Integer tincidunt', 'teaser': 'Duis vel nibh at velit scelerisque suscipit. '},
            {'model': Trend, 'name': 'Trend Nullam nulla', 'teaser': 'Phasellus ullamcorper ipsum rutrum nunc. '},
        ]

        author = {
            'username': 'alice',
            'gender': 'male',
            'first_name': 'Alice',
            'last_name': 'Doe',
            'email': 'test+alice@blueshoe.de',
        }

        self.author = DllUser.objects.create(**author)
        self.author.set_password('password')
        self.author.save()

        for content in content_list:
            c = content['model'].objects.create(name=content['name'], teaser=content['teaser'], author=self.author)
            if issubclass(content['model'], Tool):
                url = ToolLink.objects.create(url='www.foo.bar', name='Foo', tool=c)
                c.url = url
                c.save()
            c.publish()

        # Create competence
        Competence.objects.create(cid=1)
        SubCompetence.objects.create(cid=11)


class ContentListTests(BaseTestCase):

    def test_content_retrieve(self):
        public_tool = Tool.objects.published().first()
        detail_view = reverse('public-content-detail', kwargs={'pk': public_tool.pk})
        response = self.client.get(detail_view)
        self.assertEqual(response.status_code, 200)

    def test_content_list(self):
        list_view = reverse('public-content-list')
        response = self.client.get(list_view)
        data = response.json()
        self.assertTrue(len(data['results']) == 6)
        self.assertEqual(set(data['results'][0].keys()), {'name', 'image', 'type', 'type_verbose', 'teaser',
                                                          'competences', 'url', 'created', 'id'})
        self.assertTrue(isinstance(data['results'][0]['competences'], list))


class TrendCreationTests(BaseTestCase):

    def test_content_create(self):
        self.client.login(username='test+alice@blueshoe.de', password='password')

        create_view = reverse('draft-content-list')
        post_data = {
            "name": "New Trend",
            "teaser": "Nunc interdum lacus sit amet orci.",
            "learning_goals": ["a", "b", "c"],
            "related_content": [2, 4],
            "competences": [1],
            "sub_competences": [1],
            "resourcetype": "Trend",
            "contentlink_set": [
                {"url": "https://www.foo.com", "name": "Foo", "type": "audio"},
                {"url": "https://www.bar.com", "name": "Bar", "type": "video"},
            ]
        }
        response = self.client.post(create_view, data=post_data, content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertTrue(data['author']['username'] == 'alice')


class ToolCreationTests(BaseTestCase):
    def test_content_create(self):
        self.client.login(username='test+alice@blueshoe.de', password='password')

        create_view = reverse('draft-content-list')
        post_data = {
            "name": "New Tool",
            "teaser": "Nunc interdum lacus sit amet orci.",
            "learning_goals": ["a", "b", "c"],
            "related_content": [2, 4],
            "competences": [1],
            "sub_competences": [1],
            "resourcetype": "Tool",
            "contentlink_set": [
                {"url": "https://www.foo.com", "name": "Foo", "type": "audio"},
                {"url": "https://www.bar.com", "name": "Bar", "type": "video"},
            ]
        }
        response = self.client.post(create_view, data=post_data, content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertTrue(data['author']['username'] == 'alice')


class TeachingModuleCreationTests(BaseTestCase):
    def test_content_create(self):
        self.client.login(username='test+alice@blueshoe.de', password='password')

        create_view = reverse('draft-content-list')
        post_data = {
            "name": "New TeachingModule",
            "teaser": "Nunc interdum lacus sit amet orci.",
            "learning_goals": ["a", "b", "c"],
            "related_content": [2, 4],
            "competences": [1],
            "sub_competences": [1],
            "resourcetype": "TeachingModule",
            "contentlink_set": [
                {"url": "https://www.foo.com", "name": "Foo", "type": "audio"},
                {"url": "https://www.bar.com", "name": "Bar", "type": "video"},
            ]
        }
        response = self.client.post(create_view, data=post_data, content_type='application/json')
        data = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertTrue(data['author']['username'] == 'alice')

