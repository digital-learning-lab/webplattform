import random

from django.test import TestCase
from django.urls import reverse

from dll.content.models import (
    Tool,
    TeachingModule,
    Trend,
    ToolLink,
    Competence,
    SubCompetence,
    Content,
    Subject,
    SchoolType,
)
from dll.user.models import DllUser


class BaseTestCase(TestCase):
    def setUp(self):
        content_list = [
            {
                "model": Tool,
                "name": "Tool Fusce egestas",
                "teaser": "Fusce ac felis sit amet ligula pharetra condimentum.",
            },
            {"model": Tool, "name": "Tool Duis leo", "teaser": "Aliquam eu nunc.."},
            {
                "model": TeachingModule,
                "name": "TeachingModule Ut a",
                "teaser": "Vivamus quis mi. In ac felis quis tortor malesuada pretium.",
            },
            {
                "model": TeachingModule,
                "name": "TeachingModule Proin pretium",
                "teaser": "Nam adipiscing. In auctor lobortis lacus.",
            },
            {
                "model": Trend,
                "name": "Trend Integer tincidunt",
                "teaser": "Duis vel nibh at velit scelerisque suscipit. ",
            },
            {
                "model": Trend,
                "name": "Trend Nullam nulla",
                "teaser": "Phasellus ullamcorper ipsum rutrum nunc. ",
            },
        ]

        author = {
            "username": "alice",
            "first_name": "Alice",
            "last_name": "Doe",
            "email": "test+alice@blueshoe.de",
        }

        self.author = DllUser.objects.create(**author)
        self.author.set_password("password")
        self.author.save()
        self.published_content = []
        self.drafted_content = []

        for content in content_list:
            c = content["model"].objects.create(
                name=content["name"], teaser=content["teaser"], author=self.author
            )
            if issubclass(content["model"], Tool):
                url = ToolLink.objects.create(url="www.foo.bar", name="Foo", tool=c)
                c.url = url
                c.save()
            c.publish()
            self.drafted_content.append(c.pk)
            self.published_content.append(c.get_published().pk)

        # Create competence
        self.competence = Competence.objects.create(cid=1)
        self.sub_competence = SubCompetence.objects.create(cid=11, ordering=11)

        self.create_view = reverse("draft-content-list")


class ContentListTests(BaseTestCase):
    def test_content_retrieve(self):
        public_tool = Tool.objects.published().first()
        detail_view = reverse("public-content-detail", kwargs={"pk": public_tool.pk})
        response = self.client.get(detail_view)
        self.assertEqual(response.status_code, 200)

    def test_content_list(self):
        list_view = reverse("public-content-list")
        response = self.client.get(list_view)
        data = response.json()
        self.assertTrue(len(data["results"]) == 6)
        self.assertEqual(
            set(data["results"][0].keys()),
            {
                "name",
                "image",
                "type",
                "type_verbose",
                "teaser",
                "competences",
                "url",
                "created",
                "id",
                "co_authors",
            },
        )
        self.assertTrue(isinstance(data["results"][0]["competences"], list))


class TrendCreationTests(BaseTestCase):
    def test_anonymous_user_cannot_create_content(self):
        post_data = {
            "name": "New Trend",
            "teaser": "Nunc interdum lacus sit amet orci.",
            "learning_goals": ["a", "b", "c"],
            "related_content": [
                {"pk": pk} for pk in random.choices(self.published_content, k=2)
            ],
            "competences": [{"pk": self.competence.pk}],
            "sub_competences": [{"pk": self.sub_competence.pk}],
            "resourcetype": "Trend",
            "contentlink_set": [
                {"url": "https://www.foo.com", "name": "Foo", "type": "audio"},
                {"url": "https://www.bar.com", "name": "Bar", "type": "video"},
            ],
        }
        response = self.client.post(
            self.create_view, data=post_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

    def test_content_create(self):
        self.client.login(username="test+alice@blueshoe.de", password="password")

        post_data = {
            "name": "New Trend",
            "teaser": "Nunc interdum lacus sit amet orci.",
            "learning_goals": ["a", "b", "c"],
            "related_content": [
                {"pk": pk} for pk in random.choices(self.published_content, k=2)
            ],
            "competences": [{"pk": self.competence.pk}],
            "sub_competences": [{"pk": self.sub_competence.pk}],
            "resourcetype": "Trend",
            "contentlink_set": [
                {"url": "https://www.foo.com", "name": "Foo", "type": "audio"},
                {"url": "https://www.bar.com", "name": "Bar", "type": "video"},
            ],
        }
        response = self.client.post(
            self.create_view, data=post_data, content_type="application/json"
        )
        data = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertTrue(data["author"]["username"] == "Alice Doe")


class ContentUpdateTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username="test+alice@blueshoe.de", password="password")

        post_data = {
            "name": "New Trend",
            "teaser": "Nunc interdum lacus sit amet orci.",
            "learning_goals": ["a", "b", "c"],
            "related_content": [
                {"pk": pk} for pk in random.choices(self.published_content, k=2)
            ],
            "competences": [{"pk": self.competence.pk}],
            "sub_competences": [{"pk": self.sub_competence.pk}],
            "resourcetype": "Trend",
            "contentlink_set": [
                {"url": "https://www.foo.com", "name": "Foo", "type": "audio"},
                {"url": "https://www.bar.com", "name": "Bar", "type": "video"},
            ],
        }
        self.client.post(
            self.create_view, data=post_data, content_type="application/json"
        )
        self.content = Content.objects.get(name="New Trend")

    def test_content_update(self):
        self.client.login(username="test+alice@blueshoe.de", password="password")

        update_url = reverse("draft-content-detail", kwargs={"slug": self.content.slug})
        post_data = {
            # "name": "New Trend",
            "teaser": "Vestibulum purus quam, scelerisque ut, mollis sed, nonummy id, metus.",
            "resourcetype": "Trend",
        }
        response = self.client.patch(
            update_url, data=post_data, content_type="application/json"
        )
        data = response.json()
        self.assertEqual(data["teaser"], post_data["teaser"])
        pass

    def test_anonymous_user_cannot_update_content(self):
        self.client.logout()
        update_url = reverse("draft-content-detail", kwargs={"slug": self.content.slug})
        post_data = {
            # "name": "New Trend",
            "teaser": "Vestibulum purus quam, scelerisque ut, mollis sed, nonummy id, metus.",
            "resourcetype": "Trend",
        }
        response = self.client.patch(
            update_url, data=post_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)

    def test_co_author_can_update_content(self):
        # todo
        pass

    def test_random_author_cannot_update_content(self):
        # todo
        pass


class ContentDeleteTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username="test+alice@blueshoe.de", password="password")

        post_data = {
            "name": "New Trend",
            "teaser": "Nunc interdum lacus sit amet orci.",
            "learning_goals": ["a", "b", "c"],
            "related_content": [
                {"pk": pk} for pk in random.choices(self.published_content, k=2)
            ],
            "competences": [{"pk": self.competence.pk}],
            "sub_competences": [{"pk": self.sub_competence.pk}],
            "resourcetype": "Trend",
            "contentlink_set": [
                {"url": "https://www.foo.com", "name": "Foo", "type": "audio"},
                {"url": "https://www.bar.com", "name": "Bar", "type": "video"},
            ],
        }
        self.client.post(
            self.create_view, data=post_data, content_type="application/json"
        )
        self.content = Content.objects.get(name="New Trend")

    def test_author_can_delete_content(self):
        self.client.login(username="test+alice@blueshoe.de", password="password")
        delete_view = reverse(
            "draft-content-detail", kwargs={"slug": self.content.slug}
        )
        response = self.client.delete(delete_view, content_type="application/json")
        self.assertEqual(response.status_code, 204)

    def test_co_author_cannot_delete_content(self):
        # todo
        pass

    def test_anonymous_user_cannot_delete_content(self):
        self.client.logout()
        delete_view = reverse(
            "draft-content-detail", kwargs={"slug": self.content.slug}
        )
        response = self.client.delete(delete_view, content_type="application/json")
        self.assertEqual(response.status_code, 403)

    def test_other_author_cannot_delete_content(self):
        # todo
        pass


class ToolCreationTests(BaseTestCase):
    def test_content_create(self):
        self.client.login(username="test+alice@blueshoe.de", password="password")

        create_view = reverse("draft-content-list")
        post_data = {
            "name": "New Tool",
            "teaser": "Nunc interdum lacus sit amet orci.",
            "learning_goals": ["a", "b", "c"],
            "related_content": [
                {"pk": pk} for pk in random.choices(self.published_content, k=2)
            ],
            "competences": [{"pk": self.competence.pk}],
            "sub_competences": [{"pk": self.sub_competence.pk}],
            "resourcetype": "Tool",
            "contentlink_set": [
                {"url": "https://www.foo.com", "name": "Foo", "type": "audio"},
                {"url": "https://www.bar.com", "name": "Bar", "type": "video"},
            ],
        }
        response = self.client.post(
            create_view, data=post_data, content_type="application/json"
        )
        data = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertTrue(data["author"]["username"] == "Alice Doe")


class TeachingModuleCreationTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.subject = Subject.objects.create(name="Test")
        self.school_type = SchoolType.objects.create(name="Test")

    def test_content_create(self):
        self.client.login(username="test+alice@blueshoe.de", password="password")

        create_view = reverse("draft-content-list")
        post_data = {
            "name": "New TeachingModule",
            "teaser": "Nunc interdum lacus sit amet orci.",
            "learning_goals": ["a", "b", "c"],
            "related_content": [
                {"pk": pk} for pk in random.choices(self.published_content, k=2)
            ],
            "competences": [{"pk": self.competence.pk}],
            "sub_competences": [{"pk": self.sub_competence.pk}],
            "resourcetype": "TeachingModule",
            "contentlink_set": [
                {"url": "https://www.foo.com", "name": "Foo", "type": "audio"},
                {"url": "https://www.bar.com", "name": "Bar", "type": "video"},
            ],
            "subjects": [{"pk": self.subject.pk}],
            "school_types": [{"pk": self.school_type.pk}],
        }
        response = self.client.post(
            create_view, data=post_data, content_type="application/json"
        )
        data = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertTrue(data["author"]["username"] == "Alice Doe")
