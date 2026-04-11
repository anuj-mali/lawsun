from typing import Literal


from pydantic import BaseModel, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMConfig(BaseModel):
    provider: Literal["openai", "google", "gemini"]
    api_key: str
    model_name: str


class DatabaseConfig(BaseModel):
    host: str
    port: int
    user: str
    password: str
    name: str

    @computed_field
    @property
    def database_url(self) -> str:
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    @computed_field
    @property
    def database_url_async(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


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

    # EMBEDDING
    embedding_dimensions: int = 768
    llm: LLMConfig


config = Config()
