from pydantic_settings import BaseSettings, SettingsConfigDict


class TortoiseORMSettings(BaseSettings):
    db_connection: str = "sqlite://db.sqlite3"
    apps_models_models: str = "app.models"
    apps_models_default_connection: str = "default"


class SearchSettings(BaseSettings):
    timeout: int = 10000


class JWTSettings(BaseSettings):
    secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1000
    refresh_token_expire_days: int = 30


class Settings(BaseSettings):
    tortoise_orm: TortoiseORMSettings = TortoiseORMSettings()
    search: SearchSettings = SearchSettings()
    jwt: JWTSettings = JWTSettings()


# Now you can load the settings


settings = Settings()
