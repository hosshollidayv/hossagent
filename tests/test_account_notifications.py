import os
import unittest
from datetime import datetime
from unittest.mock import patch

from account_notifications import (
    DEFAULT_ACCOUNT_NOTIFICATION_EMAIL,
    get_account_notification_email,
    notify_owner_of_external_account,
)
from email_utils import EmailResult


class AccountNotificationTest(unittest.TestCase):
    def test_uses_owner_inbox_by_default(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(
                get_account_notification_email(),
                DEFAULT_ACCOUNT_NOTIFICATION_EMAIL,
            )

    def test_environment_can_override_owner_inbox(self):
        with patch.dict(
            os.environ,
            {"ACCOUNT_NOTIFICATION_EMAIL": "alerts@example.com"},
            clear=True,
        ):
            self.assertEqual(get_account_notification_email(), "alerts@example.com")

    def test_sends_review_fields_without_password_data(self):
        captured = {}

        def fake_send(**kwargs):
            captured.update(kwargs)
            return EmailResult(
                success=True,
                mode="SENDGRID",
                result="success",
                actually_sent=True,
            )

        sent = notify_owner_of_external_account(
            account_id=42,
            company="Acme\nSystems",
            contact_name="Jordan Lee",
            contact_email="jordan@example.com",
            ip_address="203.0.113.8",
            user_agent="Example Browser",
            created_at=datetime(2026, 8, 11, 12, 30),
            send_email_fn=fake_send,
        )

        self.assertTrue(sent)
        self.assertEqual(captured["to_email"], DEFAULT_ACCOUNT_NOTIFICATION_EMAIL)
        self.assertIn("New external account: Acme Systems", captured["subject"])
        self.assertIn("Account ID: 42", captured["body"])
        self.assertIn("Email: jordan@example.com", captured["body"])
        self.assertIn("IP address: 203.0.113.8", captured["body"])
        self.assertNotIn("password", captured["body"].lower())

    def test_delivery_failure_does_not_raise(self):
        def failed_send(**kwargs):
            return EmailResult(
                success=False,
                mode="SENDGRID",
                result="failed",
                error="provider unavailable",
                actually_sent=False,
            )

        sent = notify_owner_of_external_account(
            account_id=7,
            company="Example Co",
            contact_name=None,
            contact_email="owner@example.com",
            ip_address=None,
            user_agent=None,
            send_email_fn=failed_send,
        )

        self.assertFalse(sent)


if __name__ == "__main__":
    unittest.main()
