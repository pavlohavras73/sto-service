from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APPLICATION_VERSION: str = "1.0.0"
    TEST_MODE: bool = False
    DATABASE_URL: str = "sqlite:///./sto_database.db"

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings() -> Settings:
    return Settings()
