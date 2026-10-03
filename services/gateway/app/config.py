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

    # --- AI models (see app/ai.py) ---
    # auto = Claude if a key is set, else DeepSeek; or claude / deepseek / fake (tests and demos)
    ai_provider: str = "auto"
    anthropic_api_key: str = ""
    claude_model: str = "claude-sonnet-5"
    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    ai_timeout: float = 180.0
    ai_fake_delay: float = 0.0  # local testing only: make the fake model take this many seconds per call
    # Where uploaded course materials are kept during an import (kept 24 hours).
    import_dir: str = "/tmp/wq-imports"
    # The animation renderer (services/animator), e.g. http://animator:8000. Empty = lessons get no video.
    animator_url: str = ""
    animator_timeout: float = 600.0
    # The lab checker (services/labcheck), e.g. http://labcheck:8000. Empty = lessons get no virtual lab.
    labcheck_url: str = ""
    # 问渠零件与机器人库 (digital factory). Empty = the built-in sample library generated into data_dir.
    library_url: str = ""
    # The voice service (services/voice): speech synthesis and recognition for lecture videos. Empty = no lecture videos.
    voice_url: str = ""
    # The course lead's model (专家版, round 5): the strongest available; empty = the same as the rest of the team.
    lead_model: str = "claude-opus-5-5"
    # 问渠数字工厂 course interface (read-only key copied by deploy/update.sh). Empty = lessons without factory data.
    factory_url: str = ""
    factory_read_key: str = ""
    # Engineering task sheets (round 11, 2.7 (5)): server-to-server key of the hubs' /api/tasks/course/* and the class
    # factories "pilot:试点班,g2:二班" (both copied by deploy/update.sh). Empty key = the course's 任务单 menu says “not connected”.
    factory_task_key: str = ""
    factory_classes: str = ""
    labcheck_timeout: float = 150.0
    # Built textbooks (textbook/ in the repository, built by CI): <dir>/<book>/web/index.json …
    textbook_dir: str = "/textbook"
    data_dir: str = "/tmp/wq-data"  # converted slides and small settings; a persistent volume in production

    # --- accounts: sign-up, email codes, teacher approval (app/accounts.py) ---
    # Outgoing mail. Empty host = mail is not sent; codes and messages are written to the log instead.
    smtp_host: str = ""
    smtp_port: int = 2525
    smtp_secure: str = "tls"   # tls = STARTTLS, ssl = TLS from the start, none
    smtp_user: str = ""
    smtp_password: str = ""
    mail_from: str = ""        # e.g. noreply@wenquestrobotics.com
    mail_from_name: str = "问渠机器人学院 WenQuest"
    admin_email: str = ""      # where new teacher applications are reported
    admin_email_fallback: str = ""  # MOODLE_ADMIN_EMAIL, used when admin_email is empty
    app_url: str = "http://localhost:8088"   # the learning platform, for links in emails
    site_domain: str = ""      # e.g. wenquestrobotics.com: the sign-in cookie is shared across it
    accounts_service: str = "local_wenquest_accounts"

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
