from django.contrib.auth.models import Group
from django.test import TestCase
from guardian.shortcuts import assign_perm

from dll.content.models import TeachingModule, Review
from dll.user.models import DllUser


class BaseTestCase(TestCase):
    def setUp(self):

        author = {
            'username': 'alice',
            'gender': 'male',
            'first_name': 'Alice',
            'last_name': 'Doe',
            'email': 'test+alice@blueshoe.de',
        }

        co_author = {
            'username': 'bob',
            'gender': 'female',
            'first_name': 'Bob',
            'last_name': 'Doe',
            'email': 'test+bob@blueshoe.de',
        }

        other_author = {
            'username': 'john',
            'gender': 'female',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'test+john@blueshoe.de',
        }

        bsb_reviewer = {
            'username': 'carmen',
            'gender': 'female',
            'first_name': 'Carmen',
            'last_name': 'Doe',
            'email': 'test+carmen@blueshoe.de',
        }

        tuhh_reviewer = {
            'username': 'daniel',
            'gender': 'female',
            'first_name': 'Daniel',
            'last_name': 'Doe',
            'email': 'test+daniel@blueshoe.de',
        }

        bsb_reviewer_group = Group.objects.create(name='BSB-Reviewer')
        tuhh_reviewer_group = Group.objects.create(name='TUHH-Reviewer')
        assign_perm('content.review_teachingmodule', bsb_reviewer_group)
        assign_perm('content.review_tool', bsb_reviewer_group)
        assign_perm('content.review_trend', tuhh_reviewer_group)

        for perm in [f'content.{action}_review' for action in ('change', 'add', 'delete', 'view')]:
            assign_perm(perm, bsb_reviewer_group)
            assign_perm(perm, tuhh_reviewer_group)

        self.author = DllUser.objects.create(**author)
        self.co_author = DllUser.objects.create(**co_author)
        self.other_author = DllUser.objects.create(**other_author)
        self.bsb_reviewer = DllUser.objects.create(**bsb_reviewer)
        bsb_reviewer_group.user_set.add(self.bsb_reviewer)
        self.tuhh_reviewer = DllUser.objects.create(**tuhh_reviewer)
        tuhh_reviewer_group.user_set.add(self.tuhh_reviewer)
        self.content = TeachingModule.objects.create(name='Foo', author=self.author)
        self.content.co_authors.add(self.co_author)


class ContentCreationTests(BaseTestCase):
    def setUp(self):
        super().setUp()

    def test_user_can_edit_own_content(self):
        self.assertTrue(self.author.has_perm('content.change_teachingmodule', self.content))

    def test_other_user_cannot_edit_own_content(self):
        self.assertFalse(self.other_author.has_perm('content.change_teachingmodule', self.content))

    def test_coauthor_has_edit_permission(self):
        self.assertTrue(self.co_author.has_perm('content.change_teachingmodule', self.content))
        self.assertFalse(self.other_author.has_perm('content.change_teachingmodule', self.content))


class ReviewSubmissionTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.content.submit_for_review()

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
        self.content.submit_for_review()
        self.content.review.decline()

    def test_review_status(self):
        self.assertEqual(self.content.review.status, Review.DECLINED)

    def test_reviewer_cannot_edit_review(self):
        self.assertFalse(self.bsb_reviewer.has_perm('content.change_review', self.content.review))

    def test_author_can_edit_content(self):
        self.assertTrue(self.author.has_perm('content.change_teachingmodule', self.content))

    def test_co_author_can_edit_content(self):
        self.assertTrue(self.co_author.has_perm('content.change_teachingmodule', self.content))


class ReviewAcceptTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.content.submit_for_review()
        self.content.review.accept()

    def test_review_status(self):
        self.assertEqual(self.content.review.status, Review.ACCEPTED)

    # def test_content_has_a_public_instance(self):
    #     self.assertFalse(self.content.get_published() is None)

    def test_reviewer_cannot_edit_review(self):
        self.assertFalse(self.bsb_reviewer.has_perm('content.change_review', self.content.review))

    def test_author_can_edit_content(self):
        self.assertTrue(self.author.has_perm('content.change_teachingmodule', self.content))

    def test_co_author_can_edit_content(self):
        self.assertTrue(self.co_author.has_perm('content.change_teachingmodule', self.content))
