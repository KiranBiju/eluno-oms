"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./data/eluno_oms.db"
    api_base_url: str = "http://127.0.0.1:8000"

    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    alert_from_email: str = "ops@eluno.com"
    alert_to_email: str = "ops-manager@eluno.com"

    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    breach_alert_threshold: float = 0.70


settings = Settings()
