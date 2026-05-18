from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Agentic Settings"
    redis_url: str = "redis://localhost:6379/0"
    openrouter_base_url: str
    openrouter_api_key: str
    tavily_api_key: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()  # type: ignore
