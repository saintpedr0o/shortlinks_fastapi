from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, Field


class Settings(BaseSettings):
    app_name: str = "ShortlinksAPI"
    debug: bool = Field(..., env="DEBUG")

    # JWT
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field(..., env="ALGORITHM")
    access_token_expire_minutes: int = Field(..., env="ACCESS_TOKEN_EXPIRE_MINUTES")
    refresh_secret_key: str = Field(..., env="REFRESH_SECRET_KEY")
    refresh_token_expire_days: int = Field(..., env="REFRESH_TOKEN_EXPIRE_DAYS")

    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    base_url: str = Field("0.0.0.0", env="BASE_URL")

    short_code_length: int = Field(..., env="SHORT_CODE_LENGTH")

    enable_tracking: bool = Field(True, env="ENABLE_TRACKING")
    log_ip_address: bool = Field(True, env="LOG_IP_ADDRESS")
    log_user_agent: bool = Field(True, env="LOG_USER_AGENT")
    log_referrer: bool = Field(True, env="LOG_REFERRER")

    database_url: PostgresDsn = Field(..., env="DATABASE_URL")

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def db_url_str(self) -> str:
        return str(self.database_url)


@lru_cache
def get_settings() -> Settings:
    return Settings()
