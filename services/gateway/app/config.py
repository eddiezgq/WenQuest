"""Gateway settings, read from environment variables (see .env.example at the repo root)."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="WQ_", env_file=".env", extra="ignore")

    # Moodle's public address, exactly as its wwwroot (e.g. https://classic.example.com).
    moodle_url: str = "http://localhost:8080"
    # Optional: where the gateway connects to Moodle if not via the public address
    # (inside docker: http://moodle). Requests still carry the public host name.
    moodle_connect_url: str = ""
    # Web service the gateway asks Moodle for user tokens.
    moodle_service: str = "moodle_mobile_app"
    # Secret used to encrypt session tokens. Must be set in production.
    secret_key: str = "dev-only-change-me"
    session_days: int = 7
    # Comma-separated list of allowed browser origins (the WenQuest web app).
    cors_origins: str = "http://localhost:5173"
    # Language used when the client does not ask for one: zh or en.
    default_lang: str = "zh"
    http_timeout: float = 20.0
    # Absolute base of this API as clients see it, e.g. https://app.example.com.
    # Empty = relative URLs (fine for the web app served on the same domain;
    # the WeChat mini program needs it set).
    public_url: str = ""

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
