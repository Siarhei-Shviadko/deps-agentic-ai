from typing import Any

from deps_asb import ASBSettings
from deps_kafka import KafkaSettings
from deps_message_flow import MessagingDriverEnum
from deps_rabbitmq import RabbitMQTLSSettings
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from deps_agentic_ai.extras import ServiceInfoSettings


class Settings(BaseSettings):
    model_config = SettingsConfigDict(use_enum_values=True)

    env: str = "development"
    version: str = "1.0"

    logger_level: str = Field("INFO", validation_alias="LOG_LEVEL")

    info: ServiceInfoSettings = ServiceInfoSettings()

    messaging_driver: MessagingDriverEnum = Field(MessagingDriverEnum.RABBITMQ, validation_alias="MESSAGING_DRIVER")
    messaging_driver_settings: Any = Field(None, validation_alias="MESSAGING_DRIVER_SETTINGS")
    message_broker_connection_string: str

    documentation_enabled: bool = True
    instrumentation_enabled: bool = False

    @field_validator("messaging_driver_settings")
    @classmethod
    def validate_messaging_driver_settings(cls, v, info):  # noqa: N805
        messaging_driver = info.data.get("messaging_driver")
        if not messaging_driver:
            raise ValueError("Invalid messaging driver")

        driver = MessagingDriverEnum(messaging_driver)
        if driver == MessagingDriverEnum.ASB:
            return ASBSettings()
        elif driver == MessagingDriverEnum.KAFKA:
            return KafkaSettings()
        elif driver == MessagingDriverEnum.RABBITMQ:
            return RabbitMQTLSSettings().model_dump()

        raise ValueError(f"Driver {driver} is not implemented")
