from django.test import TestCase
from django.urls import reverse

from dll.content.models import Tool, TeachingModule, Trend, ToolLink
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

        for content in content_list:
            c = content['model'].objects.create(name=content['name'], teaser=content['teaser'], author=self.author)
            if issubclass(content['model'], Tool):
                url = ToolLink.objects.create(url='www.foo.bar', name='Foo', tool=c)
                c.url = url
                c.save()
            c.publish()


class ContentListTests(BaseTestCase):

    def test_content_list(self):
        list_view = reverse('content-list')
        response = self.client.get(list_view)
        data = response.json()
        self.assertTrue(len(data['results']) == 6)
        self.assertEqual(set(data['results'][0].keys()), {'name', 'image', 'type', 'type_verbose', 'teaser',
                                                          'competences', 'url', 'created', 'id'})
        self.assertTrue(isinstance(data['results'][0]['competences'], list))


class ContentRetrieveTests(BaseTestCase):

    def test_content_retrieve(self):
        public_tool = Tool.objects.published().first()
        detail_view = reverse('content-detail', kwargs={'pk': public_tool.pk})
        response = self.client.get(detail_view)
        data = response.json()
        pass
