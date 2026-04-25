from pydantic_settings import BaseSettings, SettingsConfigDict

from .constants import DBDialect, DBDriver

__all__ = ["DatabaseSettings"]


class SSLSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DATABASE_SSL_")

    key: str = ""
    cert: str = ""
    rootcert: str = ""
    mode: str = "verify-full"


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DATABASE_")

    user: str
    password: str
    host: str
    port: str
    db: str
    ssl: SSLSettings = SSLSettings()
    dialect: DBDialect = DBDialect.POSTGRES
    driver: DBDriver = DBDriver.ASYNCPG
    require_secure_transport: bool = False
    pool_size: int = 10
