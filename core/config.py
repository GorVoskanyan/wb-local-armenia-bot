from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = Field(..., validation_alias="BOT_TOKEN")

    postgres_user: str = Field("postgres", validation_alias="POSTGRES_USER")
    postgres_password: str = Field("postgres", validation_alias="POSTGRES_PASSWORD")
    postgres_db: str = Field("wb_armenia_db", validation_alias="POSTGRES_DB")
    postgres_host: str = Field("localhost", validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(5432, validation_alias="POSTGRES_PORT")
    database_url: str = Field(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/wb_armenia_db",
        validation_alias="DATABASE_URL"
    )

    redis_host: str = Field("localhost", validation_alias="REDIS_HOST")
    redis_port: int = Field(6379, validation_alias="REDIS_PORT")
    redis_url: str = Field("redis://localhost:6379/0", validation_alias="REDIS_URL")

    encryption_key: str = Field(..., validation_alias="ENCRYPTION_KEY")

    wb_deeplink_base_url: str = Field(
        "https://am.wildberries.ru/catalog/{sku}/detail.aspx",
        validation_alias="WB_DEEPLINK_BASE_URL"
    )
    default_language: str = Field("hy", validation_alias="DEFAULT_LANGUAGE")
    mock_wb_api: bool = Field(True, validation_alias="MOCK_WB_API")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
