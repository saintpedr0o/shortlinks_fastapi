from functools import lru_cache
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        extra="ignore",
        env_file_encoding="utf-8",
    )

    app_name: str = "ShortlinksAPI"
    debug: bool = False  # default value; will be loaded from .env if present

    # prefix for shortlink redirects, e.g. URLs will look like http://host/r/<code>
    # if prefix is "" - shortlink look like http://host/<code>
    redirect_prefix: str = "r"

    # JWT
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_secret_key: str
    refresh_token_expire_days: int

    host: str = "0.0.0.0"
    port: int = 8000
    base_url: str = "0.0.0.0"

    short_code_length: int

    enable_tracking: bool = True
    log_ip_address: bool = True
    log_user_agent: bool = True
    log_referrer: bool = True

    postgres_user: str
    postgres_password: str
    postgres_db: str

    database_url: PostgresDsn

    @property
    def db_url_str(self):
        return str(self.database_url)


@lru_cache
def get_settings() -> Settings:
    return Settings()
