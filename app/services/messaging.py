from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from app.config import Settings


class MessageChannelError(RuntimeError):
    pass


class WhatsAppProvider(Protocol):
    def send_message(self, to: str, body: str) -> str:
        ...


class EmailProvider(Protocol):
    def send_email(self, to: str, subject: str, body: str) -> str:
        ...


@dataclass
class TwilioWhatsApp:
    account_sid: str
    auth_token: str
    from_number: str

    def send_message(self, to: str, body: str) -> str:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}/Messages.json"
        data = {"From": f"whatsapp:{self.from_number}", "To": f"whatsapp:{to}", "Body": body}
        auth = (self.account_sid, self.auth_token)
        # Real request disabled for safety; kept as reference.
        # response = httpx.post(url, data=data, auth=auth, timeout=10)
        # if response.status_code >= 300:
        #     raise MessageChannelError(f"Twilio error: {response.text}")
        # return response.json().get("sid", "")
        return "twilio-simulated-sid"


@dataclass
class DialogWhatsApp:
    api_key: str
    phone_number: str

    def send_message(self, to: str, body: str) -> str:
        headers = {"D360-API-KEY": self.api_key, "Content-Type": "application/json"}
        payload = {"to": to, "type": "text", "text": {"body": body}}
        url = "https://waba.360dialog.io/v1/messages"
        # response = httpx.post(url, json=payload, headers=headers, timeout=10)
        # if response.status_code >= 300:
        #     raise MessageChannelError(f"360Dialog error: {response.text}")
        # return response.json().get("messages", [{}])[0].get("id", "")
        return "360dialog-simulated-id"


@dataclass
class SendGridEmail:
    api_key: str
    from_email: str

    def send_email(self, to: str, subject: str, body: str) -> str:
        url = "https://api.sendgrid.com/v3/mail/send"
        payload = {
            "personalizations": [{"to": [{"email": to}]}],
            "from": {"email": self.from_email},
            "subject": subject,
            "content": [{"type": "text/plain", "value": body}],
        }
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        # response = httpx.post(url, json=payload, headers=headers, timeout=10)
        # if response.status_code >= 300:
        #     raise MessageChannelError(f"SendGrid error: {response.text}")
        return "sendgrid-simulated"


@dataclass
class SESEmail:
    region: str
    from_email: str

    def send_email(self, to: str, subject: str, body: str) -> str:
        # Placeholder for boto3 SES send_email usage
        return "ses-simulated"


class MessagingService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.whatsapp_client: WhatsAppProvider | None = None
        self.email_client: EmailProvider | None = None
        self._init_clients()

    def _init_clients(self) -> None:
        if self.settings.whatsapp_provider.lower() == "twilio":
            self.whatsapp_client = TwilioWhatsApp(
                account_sid=self.settings.twilio_account_sid,
                auth_token=self.settings.twilio_auth_token,
                from_number=self.settings.twilio_from_number,
            )
        elif self.settings.whatsapp_provider.lower() == "360dialog":
            self.whatsapp_client = DialogWhatsApp(
                api_key=self.settings.dialog_api_key,
                phone_number=self.settings.dialog_phone_number,
            )

        if self.settings.email_provider.lower() == "sendgrid":
            self.email_client = SendGridEmail(api_key=self.settings.sendgrid_api_key, from_email=self.settings.from_email)
        else:
            self.email_client = SESEmail(region=self.settings.ses_region, from_email=self.settings.from_email)

    def send_whatsapp(self, to: str, body: str) -> str:
        if not self.whatsapp_client:
            raise MessageChannelError("WhatsApp provider is not configured")
        return self.whatsapp_client.send_message(to=to, body=body)

    def send_email(self, to: str, subject: str, body: str) -> str:
        if not self.email_client:
            raise MessageChannelError("Email provider is not configured")
        return self.email_client.send_email(to=to, subject=subject, body=body)
