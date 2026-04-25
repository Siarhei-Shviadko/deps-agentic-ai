from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["ServiceInfoSettings"]


class ServiceInfoSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SERVICE_INFO_")

    tag: str = ""
    date: str = ""
    hash: str = ""
