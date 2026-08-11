"""Owner notifications for externally created HossAgent accounts."""

import os
from datetime import datetime, timezone
from typing import Callable, Optional

from email_utils import EmailResult, send_email


DEFAULT_ACCOUNT_NOTIFICATION_EMAIL = "sam@hossagent.net"


def _clean_field(value: Optional[object], fallback: str = "Not provided") -> str:
    """Keep user-supplied values readable and bounded in notification emails."""
    if value is None:
        return fallback
    cleaned = " ".join(str(value).split()).strip()
    return cleaned[:500] or fallback


def get_account_notification_email() -> str:
    """Return the owner inbox for new external-account alerts."""
    configured = os.getenv("ACCOUNT_NOTIFICATION_EMAIL", "").strip()
    return configured or DEFAULT_ACCOUNT_NOTIFICATION_EMAIL


def notify_owner_of_external_account(
    *,
    account_id: int,
    company: str,
    contact_name: Optional[str],
    contact_email: str,
    ip_address: Optional[str],
    user_agent: Optional[str],
    created_at: Optional[datetime] = None,
    send_email_fn: Optional[Callable[..., EmailResult]] = None,
) -> bool:
    """Email the owner after a self-service account is committed.

    Notification failures are contained so they never roll back a valid account.
    The return value is True only when the email provider confirms a real send.
    """
    recipient = get_account_notification_email()
    timestamp = created_at or datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        created_text = f"{timestamp.isoformat()}Z"
    else:
        created_text = timestamp.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    safe_company = _clean_field(company)
    sender = send_email_fn or send_email
    body = "\n".join(
        (
            "A new external HossAgent account was created.",
            "",
            f"Account ID: {account_id}",
            f"Company: {safe_company}",
            f"Contact: {_clean_field(contact_name)}",
            f"Email: {_clean_field(contact_email)}",
            f"Created: {created_text}",
            f"IP address: {_clean_field(ip_address, 'Unavailable')}",
            f"User agent: {_clean_field(user_agent, 'Unavailable')}",
            "",
            "Review: https://hossagent.net/operator",
        )
    )

    try:
        result = sender(
            to_email=recipient,
            subject=f"[HossAgent] New external account: {safe_company}",
            body=body,
            lead_name="Account alert",
            company=safe_company,
        )
    except Exception as exc:
        print(f"[ACCOUNT_ALERT][FAIL] account_id={account_id} error={exc}")
        return False

    if result.actually_sent:
        print(f"[ACCOUNT_ALERT][SENT] account_id={account_id} recipient={recipient}")
        return True

    detail = result.error or result.result
    print(
        f"[ACCOUNT_ALERT][NOT_SENT] account_id={account_id} "
        f"mode={result.mode} detail={detail}"
    )
    return False
