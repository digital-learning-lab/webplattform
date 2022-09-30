import random

from django.test import TestCase, override_settings
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
                "model": TeachingModule,
                "name": "TeachingModule Proin pretium which has a very very long name",
                "teaser": "Nam adipiscing. In auctor lobortis lacus.",
            },
            {
                "model": TeachingModule,
                "name": "TeachingModule Proin pretium which has a very very long other name",
                "teaser": "Nam adipiscing. In auctor lobortis lacus.",
            },
            {
                "model": TeachingModule,
                "name": "TeachingModule äöüß",
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


class ContentViewTests(BaseTestCase):
    fixtures = ["dll/fixtures/sites.json"]

    def test_content_retrieve(self):
        public_tool = Tool.objects.published().first()
        detail_view = reverse("public-content-detail", kwargs={"pk": public_tool.pk})
        response = self.client.get(detail_view)
        self.assertEqual(response.status_code, 200)

    def test_tool_detail(self):
        public_tool = Tool.objects.published().first()
        detail_view = reverse("tool-detail", kwargs={"slug": public_tool.slug})
        response = self.client.get(detail_view)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"//dlt.local/tools/{public_tool.slug}")

    @override_settings(SITE_ID=2)
    def test_tool_detail_dlt(self):
        public_tool = Tool.objects.published().first()
        detail_view = reverse("tool-detail", kwargs={"slug": public_tool.slug})
        response = self.client.get(detail_view)
        self.assertContains(
            response, f'<h1 class="content-info__title">{public_tool.name}</h1>'
        )
        self.assertContains(
            response, f'<p class="content-info__teaser">{public_tool.teaser}</p>'
        )
        self.assertContains(
            response, f'<meta name="description" content="{public_tool.teaser}">'
        )
        self.assertContains(response, f"<title>Tool | {public_tool.name}</title>")

    def test_trend_detail(self):
        public_trend = Trend.objects.published().first()
        detail_view = reverse("trend-detail", kwargs={"slug": public_trend.slug})
        response = self.client.get(detail_view)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, f'<h1 class="content-info__title">{public_trend.name}</h1>'
        )
        self.assertContains(
            response, f'<p class="content-info__teaser">{public_trend.teaser}</p>'
        )
        self.assertContains(
            response, f'<meta name="description" content="{public_trend.teaser}">'
        )
        self.assertContains(response, f"<title>Trend | {public_trend.name}</title>")

    def test_teaching_module_detail(self):
        public_teaching_module = TeachingModule.objects.published().first()
        detail_view = reverse(
            "teaching-module-detail", kwargs={"slug": public_teaching_module.slug}
        )
        response = self.client.get(detail_view)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f'<h1 class="content-info__title">{public_teaching_module.name}</h1>',
        )
        self.assertContains(
            response,
            f'<p class="content-info__teaser">{public_teaching_module.teaser}</p>',
        )
        self.assertContains(
            response,
            f'<meta name="description" content="{public_teaching_module.teaser}">',
        )
        self.assertContains(
            response,
            f"<title>Unterrichtsbaustein | {public_teaching_module.name}</title>",
        )

    def test_truncated_slug(self):
        """Checks whether truncated slugs work for Content objects.

        In earlier versions of the digital.learning.lab we used to truncate the slugs. Therefore the
        ContentDetailBase contains some logic to check for truncated slugs in case of a 404.
        """
        public_teaching_module = (
            TeachingModule.objects.filter(
                name="TeachingModule Proin pretium which has a very very long name"
            )
            .published()
            .first()
        )
        detail_view = reverse(
            "teaching-module-detail", kwargs={"slug": public_teaching_module.slug[:50]}
        )
        response = self.client.get(detail_view, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f'<h1 class="content-info__title">{public_teaching_module.name}</h1>',
        )
        self.assertContains(
            response,
            f'<p class="content-info__teaser">{public_teaching_module.teaser}</p>',
        )
        self.assertContains(
            response,
            f'<meta name="description" content="{public_teaching_module.teaser}">',
        )
        self.assertContains(
            response,
            f"<title>Unterrichtsbaustein | {public_teaching_module.name}</title>",
        )

    def test_content_detail_404(self):
        """Due to the truncated slug checking logic we need to test whether to 404 handling works correctly."""
        detail_view = reverse(
            "teaching-module-detail", kwargs={"slug": "some-random-slug"}
        )
        response = self.client.get(detail_view, follow=True)
        self.assertEqual(response.status_code, 404)

    def test_content_list(self):
        list_view = reverse("public-content-list")
        response = self.client.get(list_view)
        data = response.json()
        self.assertTrue(len(data["results"]) == 9)
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
                "favored",
            },
        )
        self.assertTrue(isinstance(data["results"][0]["competences"], list))

        # test exclusion of content types
        response = self.client.get(f"{list_view}?teachingModules=false")
        self.assertTrue(len(response.json()["results"]) == 4)
        response = self.client.get(f"{list_view}?trends=false")
        self.assertTrue(len(response.json()["results"]) == 7)
        response = self.client.get(f"{list_view}?tools=false")
        self.assertTrue(len(response.json()["results"]) == 7)

    def test_teaching_modules_filter_view(self):
        url = reverse("teaching-modules-filter")
        response = self.client.get(url)
        # contains vue app container
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "teaching-modules-app")
        self.assertContains(response, "window.subjectFilter")
        self.assertContains(response, "window.schoolFilter")

    def test_trends_filter_view(self):
        url = reverse("trends-filter")
        response = self.client.get(url)
        # contains vue app container
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "trends-app")

    def test_tools_filter_view(self):
        url = reverse("tools-filter")
        response = self.client.get(url)
        # contains vue app container
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "tools-app")
        self.assertContains(response, "window.functionsFilter")

    def test_teaching_content_data_filter_view(self):
        url = reverse("teaching-modules-data-filter")
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data["results"]), 5)

    def test_trends_data_filter_view(self):
        url = reverse("trends-data-filter")
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data["results"]), 2)

    def test_tools_data_filter_view(self):
        url = reverse("tools-data-filter")
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data["results"]), 2)


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
                {"url": "https://www.foo.com", "name": "Foo", "type": "href"},
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
                {"url": "https://www.foo.com", "name": "Foo", "type": "href"},
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
                {"url": "https://www.foo.com", "name": "Foo", "type": "href"},
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
                {"url": "https://www.foo.com", "name": "Foo", "type": "href"},
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
                {"url": "https://www.foo.com", "name": "Foo", "type": "href"},
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
                {"url": "https://www.foo.com", "name": "Foo", "type": "href"},
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

    def test_content_submission_invalid(self):
        self.client.login(username="test+alice@blueshoe.de", password="password")
        tm = TeachingModule.objects.create(
            name="Simple Submission Content Fail", author=self.author
        )
        submit_view = reverse("submit-content", kwargs={"slug": tm.slug})
        response = self.client.post(submit_view, content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("message", response.json())

    def test_content_name_exists_fails(self):
        self.client.login(username="test+alice@blueshoe.de", password="password")

        create_view = reverse("draft-content-list")
        post_data = {
            "name": "TeachingModule äöüß",
            "teaser": "Nunc interdum lacus sit amet orci.",
            "learning_goals": ["a", "b", "c"],
            "related_content": [
                {"pk": pk} for pk in random.choices(self.published_content, k=2)
            ],
            "competences": [{"pk": self.competence.pk}],
            "sub_competences": [{"pk": self.sub_competence.pk}],
            "resourcetype": "TeachingModule",
            "contentlink_set": [
                {"url": "https://www.foo.com", "name": "Foo", "type": "href"},
                {"url": "https://www.bar.com", "name": "Bar", "type": "video"},
            ],
            "subjects": [{"pk": self.subject.pk}],
            "school_types": [{"pk": self.school_type.pk}],
        }
        response = self.client.post(
            create_view, data=post_data, content_type="application/json"
        )
        data = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertTrue("name" in data)  # "content with name already exists"
