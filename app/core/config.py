from typing import Literal


from pydantic import BaseModel, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseModel):
    provider: Literal["openai", "google", "gemini"]
    api_key: str
    model_name: str


class EmbeddingConfig(BaseModel):
    model_name: str
    dimensions: int


class DatabaseConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str
    name: str

    @computed_field
    @property
    def database_url_async(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class RedisConfig(BaseModel):
    host: str
    port: int
    db: int


class AuthConfig(BaseModel):
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_nested_delimiter="__",
    )

    # App
    debug: bool = False

    # DATABASE
    database: DatabaseConfig

    # REDIS
    redis: RedisConfig

    # EMBEDDING
    embedding: EmbeddingConfig

    # LLM
    llm: LLMConfig

    # AUTH
    auth: AuthConfig


config = Config()
