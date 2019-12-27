# encoding: utf-8

import datetime

import mock
from nose.tools import assert_equal as eq
from nose.tools import assert_raises, assert_in

from ckan.tests import helpers, factories
from ckan.plugins.toolkit import ValidationError

from ckanext.subscribe.tests.factories import (
    Subscription,
    SubscriptionLowLevel,
    )
from ckanext.subscribe import model as subscribe_model


class TestSubscribeSignup(object):
    def setup(self):
        helpers.reset_db()

    @mock.patch('ckanext.subscribe.email_verification.send_confirmation_email')
    def test_basic(self, send_confirmation_email):
        dataset = factories.Dataset()

        subscription = helpers.call_action(
            "subscribe_signup",
            {},
            email='bob@example.com',
            dataset_id=dataset["id"],
        )

        send_confirmation_email.assert_called_once
        eq(send_confirmation_email.call_args[0][0].object_type, 'dataset')
        eq(send_confirmation_email.call_args[0][0].object_id, dataset['id'])
        eq(send_confirmation_email.call_args[0][0].email, 'bob@example.com')
        eq(subscription['object_type'], 'dataset')
        eq(subscription['object_id'], dataset['id'])
        eq(subscription['email'], 'bob@example.com')
        eq(subscription['verified'], False)
        assert 'verification_code' not in subscription

    @mock.patch('ckanext.subscribe.email_verification.send_confirmation_email')
    def test_dataset_name(self, send_confirmation_email):
        dataset = factories.Dataset()

        helpers.call_action(
            "subscribe_signup",
            {},
            email='bob@example.com',
            dataset_id=dataset["name"],
        )

        send_confirmation_email.assert_called_once
        eq(send_confirmation_email.call_args[0][0].object_type, 'dataset')
        eq(send_confirmation_email.call_args[0][0].object_id, dataset['id'])
        eq(send_confirmation_email.call_args[0][0].email, 'bob@example.com')

    @mock.patch('ckanext.subscribe.email_verification.send_confirmation_email')
    def test_group_id(self, send_confirmation_email):
        group = factories.Group()

        helpers.call_action(
            "subscribe_signup",
            {},
            email='bob@example.com',
            group_id=group["id"],
        )

        send_confirmation_email.assert_called_once
        eq(send_confirmation_email.call_args[0][0].object_type, 'group')
        eq(send_confirmation_email.call_args[0][0].object_id, group['id'])
        eq(send_confirmation_email.call_args[0][0].email, 'bob@example.com')

    @mock.patch('ckanext.subscribe.email_verification.send_confirmation_email')
    def test_group_name(self, send_confirmation_email):
        group = factories.Group()

        helpers.call_action(
            "subscribe_signup",
            {},
            email='bob@example.com',
            group_id=group["name"],
        )

        send_confirmation_email.assert_called_once
        eq(send_confirmation_email.call_args[0][0].object_type, 'group')
        eq(send_confirmation_email.call_args[0][0].object_id, group['id'])
        eq(send_confirmation_email.call_args[0][0].email, 'bob@example.com')

    @mock.patch('ckanext.subscribe.email_verification.send_confirmation_email')
    def test_org_id(self, send_confirmation_email):
        org = factories.Organization()

        helpers.call_action(
            "subscribe_signup",
            {},
            email='bob@example.com',
            group_id=org["id"],
        )

        send_confirmation_email.assert_called_once
        eq(send_confirmation_email.call_args[0][0].object_type, 'organization')
        eq(send_confirmation_email.call_args[0][0].object_id, org['id'])
        eq(send_confirmation_email.call_args[0][0].email, 'bob@example.com')

    @mock.patch('ckanext.subscribe.email_verification.send_confirmation_email')
    def test_org_name(self, send_confirmation_email):
        org = factories.Organization()

        helpers.call_action(
            "subscribe_signup",
            {},
            email='bob@example.com',
            group_id=org["name"],
        )

        send_confirmation_email.assert_called_once
        eq(send_confirmation_email.call_args[0][0].object_type, 'organization')
        eq(send_confirmation_email.call_args[0][0].object_id, org['id'])
        eq(send_confirmation_email.call_args[0][0].email, 'bob@example.com')

    @mock.patch('ckanext.subscribe.email_verification.send_confirmation_email')
    def test_skip_verification(self, send_confirmation_email):
        dataset = factories.Dataset()

        subscription = helpers.call_action(
            "subscribe_signup",
            {},
            email='bob@example.com',
            dataset_id=dataset["id"],
            skip_verification=True,
        )

        assert not send_confirmation_email.called
        eq(subscription['object_type'], 'dataset')
        eq(subscription['object_id'], dataset['id'])
        eq(subscription['email'], 'bob@example.com')
        eq(subscription['verified'], True)

    @mock.patch('ckanext.subscribe.email_verification.send_confirmation_email')
    def test_resend_verification(self, send_confirmation_email):
        dataset = factories.Dataset()
        existing_subscription = Subscription(
            dataset_id=dataset['id'],
            email='bob@example.com',
            skip_verification=False,
            verification_code='original_code',
        )

        subscription = helpers.call_action(
            "subscribe_signup",
            {},
            email='bob@example.com',
            dataset_id=dataset["id"],
        )

        send_confirmation_email.assert_called_once
        eq(send_confirmation_email.call_args[0][0].id,
            existing_subscription['id'])
        eq(send_confirmation_email.call_args[0][0].object_type, 'dataset')
        eq(send_confirmation_email.call_args[0][0].object_id, dataset['id'])
        eq(send_confirmation_email.call_args[0][0].email, 'bob@example.com')
        assert send_confirmation_email.call_args[0][0].verification_code != \
            'original_code'
        eq(subscription['object_type'], 'dataset')
        eq(subscription['object_id'], dataset['id'])
        eq(subscription['email'], 'bob@example.com')
        eq(subscription['verified'], False)

    @mock.patch('ckanext.subscribe.email_verification.send_confirmation_email')
    def test_dataset_doesnt_exist(self, send_confirmation_email):
        with assert_raises(ValidationError) as cm:
            helpers.call_action(
                "subscribe_signup",
                {},
                email='bob@example.com',
                dataset_id='doesnt-exist',
            )
        assert_in("dataset_id': [u'Not found",
                  str(cm.exception.error_dict))

        assert not send_confirmation_email.called

    @mock.patch('ckanext.subscribe.email_verification.send_confirmation_email')
    def test_group_doesnt_exist(self, send_confirmation_email):
        with assert_raises(ValidationError) as cm:
            helpers.call_action(
                "subscribe_signup",
                {},
                email='bob@example.com',
                group_id='doesnt-exist',
            )
        assert_in("group_id': [u'That group name or ID does not exist",
                  str(cm.exception.error_dict))

        assert not send_confirmation_email.called

    @mock.patch('ckanext.subscribe.email_verification.send_confirmation_email')
    def test_dataset_and_group_at_same_time(self, send_confirmation_email):
        dataset = factories.Dataset()
        group = factories.Group()

        with assert_raises(ValidationError) as cm:
            helpers.call_action(
                "subscribe_signup",
                {},
                email='bob@example.com',
                dataset_id=dataset["id"],
                group_id=group["id"],
            )
        assert_in('Must not specify both "dataset_id" and "group_id"',
                  str(cm.exception.error_dict))

        assert not send_confirmation_email.called


class TestSubscribeVerify(object):
    def setup(self):
        helpers.reset_db()

    def test_basic(self):
        dataset = factories.Dataset()
        SubscriptionLowLevel(
            object_id=dataset['id'],
            object_type='dataset',
            email='bob@example.com',
            verification_code='the_code',
            verification_code_expires=datetime.datetime.now() \
                + datetime.timedelta(hours=1)
        )

        subscription = helpers.call_action(
            "subscribe_verify",
            {},
            code='the_code',
        )

        eq(subscription['verified'], True)
        eq(subscription['object_type'], 'dataset')
        eq(subscription['object_id'], dataset['id'])
        eq(subscription['email'], 'bob@example.com')
        assert 'verification_code' not in subscription

    def test_wrong_code(self):
        dataset = factories.Dataset()
        subscription = SubscriptionLowLevel(
            object_id=dataset['id'],
            object_type='dataset',
            email='bob@example.com',
            verification_code='the_code',
            verification_code_expires=datetime.datetime.now() \
                + datetime.timedelta(hours=1)
        )

        with assert_raises(ValidationError) as cm:
            subscription = helpers.call_action(
                "subscribe_verify",
                {},
                code='wrong_code',
            )
        assert_in('That validation code is not recognized',
                  str(cm.exception.error_dict))

        subscription = subscribe_model.Subscription.get(subscription['id'])
        eq(subscription.verified, False)

    def test_code_expired(self):
        dataset = factories.Dataset()
        subscription = SubscriptionLowLevel(
            object_id=dataset['id'],
            object_type='dataset',
            email='bob@example.com',
            verification_code='the_code',
            verification_code_expires=datetime.datetime.now() \
                - datetime.timedelta(hours=1)  # in the past
        )

        with assert_raises(ValidationError) as cm:
            subscription = helpers.call_action(
                "subscribe_verify",
                {},
                code='the_code',
            )
        assert_in('That validation code has expired',
                  str(cm.exception.error_dict))

        subscription = subscribe_model.Subscription.get(subscription['id'])
        eq(subscription.verified, False)


class TestSubscribeAndVerify(object):
    def setup(self):
        helpers.reset_db()

    @mock.patch('ckanext.subscribe.email_verification.send_confirmation_email')
    def test_basic(self, send_confirmation_email):
        dataset = factories.Dataset()

        # subscribe
        subscription = helpers.call_action(
            "subscribe_signup",
            {},
            email='bob@example.com',
            dataset_id=dataset["id"],
        )
        code = send_confirmation_email.call_args[0][0].verification_code
        # verify
        subscription = helpers.call_action(
            "subscribe_verify",
            {},
            code=code,
        )

        send_confirmation_email.assert_called_once
        eq(send_confirmation_email.call_args[0][0].object_type, 'dataset')
        eq(send_confirmation_email.call_args[0][0].object_id, dataset['id'])
        eq(send_confirmation_email.call_args[0][0].email, 'bob@example.com')
        eq(subscription['object_type'], 'dataset')
        eq(subscription['object_id'], dataset['id'])
        eq(subscription['email'], 'bob@example.com')
        eq(subscription['verified'], True)