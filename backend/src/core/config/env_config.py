from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    DB_ENGINE: str = 'django.db.backends.postgresql'
    DB_USERNAME: str = 'postgres'
    DB_PASSWORD: str = ''
    DB_HOST: str = 'db'
    DB_PORT: int = 5432
    DB_NAME: str = 'phantom_mask_db'


class SystemSettings(BaseSettings):
    SECRET_KEY: str | None = None
    HOST_URL: str = 'http://localhost:8000'
    DEBUG: bool = True
    LANGUAGE_CODE: str = 'en-us'
    TIME_ZONE: str = 'Asia/Taipei'
    USE_I18N: bool = True
    USE_TZ: bool = True

    BATCH_SIZE: int = 100


class Settings(SystemSettings, DatabaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


settings = Settings()
