from django.core import mail
from django.test import TestCase

from dll.communication.models import CommunicationEventType, CommunicationEvent
from dll.content.models import TeachingModule, Trend
from dll.user.models import DllUser
from dll.user.utils import get_bsb_reviewer_group, get_tuhh_reviewer_group


class BaseTestCase(TestCase):
    def setUp(self):
        author = {
            'username': 'alice',
            'gender': 'female',
            'first_name': 'Alice',
            'last_name': 'Doe',
            'email': 'alice@blueshoe.de',
        }
        bsb_reviewer_1 = {
            'username': 'bob',
            'gender': 'male',
            'first_name': 'Bob',
            'last_name': 'Doe',
            'email': 'bob@blueshoe.de',
        }
        bsb_reviewer_2 = {
            'username': 'carmen',
            'gender': 'female',
            'first_name': 'Carmen',
            'last_name': 'Doe',
            'email': 'carmen@blueshoe.de',
        }
        tuhh_reviewer_1 = {
            'username': 'daniel',
            'gender': 'male',
            'first_name': 'Daniel',
            'last_name': 'Doe',
            'email': 'daniel@blueshoe.de',
        }
        tuhh_reviewer_2 = {
            'username': 'emilia',
            'gender': 'female',
            'first_name': 'Emilia',
            'last_name': 'Doe',
            'email': 'emilia@blueshoe.de',
        }

        self.author = DllUser.objects.create(**author)
        self.bsb_reviewer_1 = DllUser.objects.create(**bsb_reviewer_1)
        self.bsb_reviewer_2 = DllUser.objects.create(**bsb_reviewer_2)
        self.tuhh_reviewer_1 = DllUser.objects.create(**tuhh_reviewer_1)
        self.tuhh_reviewer_2 = DllUser.objects.create(**tuhh_reviewer_2)

        self.teaching_module = TeachingModule.objects.create(
            name='Foo',
            author=self.author,
        )

        self.trend = Trend.objects.create(
            name='Bar',
            author=self.author,
        )

        bsb_reviewer_group = get_bsb_reviewer_group()
        tuhh_reviewer_group = get_tuhh_reviewer_group()
        bsb_reviewer_group.user_set.add(self.bsb_reviewer_1, self.bsb_reviewer_2)
        tuhh_reviewer_group.user_set.add(self.tuhh_reviewer_1, self.tuhh_reviewer_2)

        CommunicationEventType.objects.create(code='CONTENT_SUBMITTED_FOR_REVIEW', name="Content submitted")


class ContentSubmissionTests(BaseTestCase):

    def test_teaching_module_submission_sends_mail_to_bsb_reviewers(self):
        self.teaching_module.submit_for_review(by_user=self.author)
        self.assertTrue(self.bsb_reviewer_1.email in mail.outbox[0].to)
        self.assertTrue(self.bsb_reviewer_2.email in mail.outbox[0].to)
        self.assertFalse(self.tuhh_reviewer_1.email in mail.outbox[0].to)
        self.assertFalse(self.tuhh_reviewer_2.email in mail.outbox[0].to)

    def test_trend_submission_sends_mail_to_tuhh_reviewers(self):
        self.trend.submit_for_review(by_user=self.author)
        self.assertFalse(self.bsb_reviewer_1.email in mail.outbox[0].to)
        self.assertFalse(self.bsb_reviewer_2.email in mail.outbox[0].to)
        self.assertTrue(self.tuhh_reviewer_1.email in mail.outbox[0].to)
        self.assertTrue(self.tuhh_reviewer_2.email in mail.outbox[0].to)


class ContentDeclineTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.teaching_module.submit_for_review(by_user=self.author)
        self.teaching_module.review.decline(by_user=self.bsb_reviewer_1)
        CommunicationEventType.objects.create(code='REVIEW_DECLINED', name="Review declined")

    def test_email_sent(self):
        self.assertEqual(len(mail.outbox), 1)


class ContentAcceptTests(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.teaching_module.submit_for_review(by_user=self.author)
        self.teaching_module.review.accept(by_user=self.bsb_reviewer_1)
        CommunicationEventType.objects.create(code='REVIEW_ACCEPTED', name="Review accepted")

    def test_email_sent(self):
        self.assertEqual(len(mail.outbox), 1)
