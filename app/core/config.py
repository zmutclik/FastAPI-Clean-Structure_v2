from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class DBConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_", env_file=".env", env_file_encoding="utf-8", extra="ignore")
    IPADDRESS: str = "127.0.0.1"
    PORT: str = "3307"
    USER: str = "root"
    PASSWORD: str = "blackant"
    NAME: str = "db"

    @property
    def DB_ENGINE(self) -> str:
        return "mysql+pymysql://{user}:{password}@{hostname}:{port}/{database}".format(
            user=self.USER,
            port=self.PORT,
            password=self.PASSWORD,
            hostname=self.IPADDRESS,
            database=self.NAME,
        )


class RABBITMQConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="RABBITMQ_", env_file=".env", env_file_encoding="utf-8", extra="ignore")
    IPADDRESS: str = "192.168.40.5"
    PORT: str = "5672"
    USER: str = "semut"
    PASSWORD: str = "blackant"
    VHOST: str = "semut-dev"

    @property
    def CELERY_ENGINE(self) -> str:
        return "amqp://{user}:{password}@{hostname}:{ports}//{vhost}".format(
            user=self.USER,
            password=self.PASSWORD,
            hostname=self.IPADDRESS,
            ports=self.PORT,
            vhost=self.VHOST,
        )


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    APP_NAME: str = Field("FastAPI-Structure")
    APP_DESCRIPTION: str = Field("This is a very fancy project, with auto docs for the API and everything.")
    APP_VERSION: str = "0.001"

    CLIENTID_KEY: str = Field("fastapi-clean-structure_id")
    SESSION_KEY: str = Field("fastapi-clean-structure_sesi")
    TOKEN_KEY: str = Field("fastapi-clean-structure_token")

    SECRET_TEXT: str = "HxekWSNWYKyOsezYRQxFEJNgbUroNzDT"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    DATABASE: DBConfig = DBConfig()
    RABBITMQ: RABBITMQConfig = RABBITMQConfig()


config: Config = Config()
