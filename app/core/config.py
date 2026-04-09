from pydantic_settings import BaseSettings


class Config(BaseSettings):
    embedding_dimensions: int = 768
    provider: str
    api_key: str
    model_name: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


config = Config()
