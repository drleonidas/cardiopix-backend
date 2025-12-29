from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/app.db"
    whatsapp_provider: str = "twilio"
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_from_number: str = ""
    dialog_api_key: str = ""
    dialog_phone_number: str = ""

    email_provider: str = "ses"
    ses_region: str = "us-east-1"
    sendgrid_api_key: str = ""
    from_email: EmailStr = "no-reply@example.com"

    max_delivery_attempts: int = 3
    retry_backoff_seconds: int = 30

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()


settings = get_settings()
