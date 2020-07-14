from django.core.files import File
from django.test import TestCase
from filer.models import File as FilerFile

from dll.content.models import TeachingModule, Review, ContentLink, ContentFile, Content
from dll.user.models import DllUser


# TODO write tests for Tool and Trend too
from dll.user.utils import get_bsb_reviewer_group, get_tuhh_reviewer_group


class BaseTestCase(TestCase):
    def setUp(self):

        author = {
            'username': 'alice',
            'first_name': 'Alice',
            'last_name': 'Doe',
            'email': 'test+alice@blueshoe.de',
        }

        co_author = {
            'username': 'bob',
            'first_name': 'Bob',
            'last_name': 'Doe',
            'email': 'test+bob@blueshoe.de',
        }

        other_author = {
            'username': 'john',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'test+john@blueshoe.de',
        }

        bsb_reviewer = {
            'username': 'carmen',
            'first_name': 'Carmen',
            'last_name': 'Doe',
            'email': 'test+carmen@blueshoe.de',
        }

        tuhh_reviewer = {
            'username': 'daniel',
            'first_name': 'Daniel',
            'last_name': 'Doe',
            'email': 'test+daniel@blueshoe.de',
        }

        bsb_reviewer_group = get_bsb_reviewer_group()
        tuhh_reviewer_group = get_tuhh_reviewer_group()

        self.author = DllUser.objects.create(**author)
        self.co_author = DllUser.objects.create(**co_author)
        self.other_author = DllUser.objects.create(**other_author)
        self.bsb_reviewer = DllUser.objects.create(**bsb_reviewer)
        bsb_reviewer_group.user_set.add(self.bsb_reviewer)
        self.tuhh_reviewer = DllUser.objects.create(**tuhh_reviewer)
        tuhh_reviewer_group.user_set.add(self.tuhh_reviewer)
        self.content = TeachingModule.objects.create(
            name='Foo',
            author=self.author,
        )
        self.content.update_or_add_image_from_path('dll/static/img/cc_license.png', image_name='Test Image.jpg')
        self.content.tags.add('tag1', 'tag2', 'tag3')

        # related content
        self.content.related_content.add(TeachingModule.objects.create(
            name='Bar',
            author=self.other_author,
        ))

        # co authors
        self.content.co_authors.add(self.co_author)

        # links and files
        ContentLink.objects.create(url='https://www.foo.org', name='FooLink', type='href', content=self.content)
        file = File(open('dll/static/img/cc_license.png', 'rb'), name='BarFile')
        filer_file = FilerFile.objects.create(file=file)
        ContentFile.objects.create(file=filer_file, title='BarFile', content=self.content)


class ContentEditTests(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_user_can_edit_own_content(self):
        self.assertTrue(self.author.has_perm('content.change_teachingmodule', self.content))

    def test_other_user_cannot_edit_foreign_content(self):
        self.assertFalse(self.other_author.has_perm('content.change_teachingmodule', self.content))

    def test_coauthor_has_edit_permission(self):
        self.assertTrue(self.co_author.has_perm('content.change_teachingmodule', self.content))
        self.assertFalse(self.other_author.has_perm('content.change_teachingmodule', self.content))


class ReviewSubmissionTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.content.submit_for_review(by_user=self.author)

    def test_content_has_a_review(self):
        self.assertTrue(isinstance(self.content.review, Review))
        self.assertEqual(self.content.review.status, Review.NEW)

    def test_reviewer_can_edit_review(self):
        self.assertTrue(self.bsb_reviewer.has_perm('content.change_review', self.content.review))

    def test_author_cannot_edit_content(self):
        self.assertFalse(self.author.has_perm('content.change_teachingmodule', self.content))

    def test_co_author_cannot_edit_content(self):
        self.assertFalse(self.co_author.has_perm('content.change_teachingmodule', self.content))


class ReviewDeclineTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.content.submit_for_review(by_user=self.author)
        self.content.review.decline(by_user=self.bsb_reviewer)

    def test_review_status(self):
        self.assertEqual(self.content.review.status, Review.DECLINED)

    def test_content_has_no_public_version(self):
        self.assertTrue(self.content.get_published() is None)

    def test_reviewer_cannot_edit_review(self):
        self.assertFalse(self.bsb_reviewer.has_perm('content.change_review', self.content.review))

    def test_author_can_edit_content(self):
        self.assertTrue(self.author.has_perm('content.change_teachingmodule', self.content))

    def test_co_author_can_edit_content(self):
        self.assertTrue(self.co_author.has_perm('content.change_teachingmodule', self.content))


class ReviewAcceptTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.content.submit_for_review(by_user=self.author)
        self.content.review.accept(by_user=self.bsb_reviewer)

        self.draft = self.content.get_draft()
        self.public = self.content.get_published()

    def test_review_status(self):
        self.assertTrue(self.content.reviews.filter(status=Review.ACCEPTED).exists())

    def test_draft_still_exists(self):
        self.assertTrue(TeachingModule.objects.filter(pk=self.content.pk).exists())

    def test_content_has_a_public_instance(self):
        self.assertFalse(self.content.get_published() is None)

    def test_content_relations_have_different_pks(self):
        self.assertTrue(self.public.contentlink_set.exists())
        self.assertTrue(self.public.contentfile_set.exists())
        self.assertFalse(set(self.draft.contentlink_set.all()) == set(self.public.contentlink_set.all()))
        self.assertFalse(set(self.draft.contentfile_set.all()) == set(self.public.contentfile_set.all()))

    def test_public_and_draft_have_same_authors(self):
        self.assertEqual(self.draft.author, self.public.author)
        self.assertEqual(set(self.draft.co_authors.all()), set(self.public.co_authors.all()))

    def test_public_and_draft_have_same_tags(self):
        self.assertEqual(set(self.draft.tags.all()), set(self.public.tags.all()))

    def test_public_and_draft_have_same_related_content(self):
        published_related_content = Content.objects.published().filter(
            publisher_draft__in=self.draft.related_content.all())
        self.assertEqual(set(published_related_content), set(self.public.related_content.all()))

    def test_draft_and_public_have_different_pks(self):
        self.assertFalse(self.content.pk == self.content.get_published().pk)

    def test_author_can_edit_content(self):
        self.assertTrue(self.author.has_perm('content.change_teachingmodule', self.content))

    def test_co_author_can_edit_content(self):
        self.assertTrue(self.co_author.has_perm('content.change_teachingmodule', self.content))


class ContentEditAfterPublishingTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        # accept first version
        self.content.submit_for_review(by_user=self.author)
        self.content.review.accept(by_user=self.bsb_reviewer)

        self.draft = self.content.get_draft()
        self.public1 = self.content.get_published()

        # modify draft
        self.draft.name = 'Foo2'
        self.draft.save()

        # submit modified draft for review
        self.draft.submit_for_review(by_user=self.author)
        self.draft.review.accept(by_user=self.bsb_reviewer)
        self.public2 = self.content.get_published()

    def test_draft_edit_does_not_affect_public(self):
        self.assertFalse(self.draft.name == self.public1.name)

    def test_new_review_was_created(self):
        self.assertTrue(self.draft.reviews.count() == 2)

    def test_old_public_version_does_not_exist(self):
        cls = self.content.__class__
        with self.assertRaises(cls.DoesNotExist):
            cls.objects.get(pk=self.public1.pk)
