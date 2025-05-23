from async_fastapi_jwt_auth import AuthJWT
from pydantic import Field, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        validate_default=False,
        env_file=('.env', '.env.sample'),
        env_file_encoding='utf-8',
        extra='ignore',
    )
    # Настройки приложения
    project_name: str = Field(default='Travel Companion', env='PROJECT_NAME')
    api_version: str = Field(default='v1', env='API_VERSION')

    # Настройки JWT
    authjwt_secret_key: str = Field(default='secret', env='AUTHJWT_SECRET_KEY')
    authjwt_algorithm: str = Field(default='123', env='AUTHJWT_ALGORITHM')

    # Настройки PostgreSQL
    psql_host: str = Field(default='localhost', env='PSQL_HOST')
    psql_port: int = Field(default=5432, env='PSQL_PORT')
    psql_user: str = Field(default='app', env='PSQL_USER')
    psql_password: str = Field(default='123qwe', env='PSQL_PASSWORD')
    psql_db: str = Field(default='storage_db', env='PSQL_DB')
    db_engine_echo: bool = Field(default=False, env='DB_ENGINE_ECHO')

    # Настройки Redis
    redis_host: str = Field(default='localhost', env='REDIS_HOST')
    redis_port: int = Field(default=6379, env='REDIS_PORT')
    redis_ttl: int = Field(default=60 * 5, env='REDIS_TTL')

    # Настройки LocationIQ
    locationiq_api_key: str = Field(default='', env='LOCATIONIQ_API_KEY')
    locationiq_base_url: str = Field(default='https://eu1.locationiq.com/v1', env='LOCATIONIQ_BASE_URL')

    @computed_field
    @property
    def SQLALCHEMY_SYNC_DATABASE_URI(self) -> MultiHostUrl:
        return MultiHostUrl.build(
            scheme='postgresql+psycopg2',
            username=self.psql_user,
            password=self.psql_password,
            host=self.psql_host,
            port=self.psql_port,
            path=self.psql_db,
        )

    @computed_field
    @property
    def SQLALCHEMY_ASYNC_DATABASE_URI(self) -> MultiHostUrl:
        return MultiHostUrl.build(
            scheme='postgresql+asyncpg',
            username=self.psql_user,
            password=self.psql_password,
            host=self.psql_host,
            port=self.psql_port,
            path=self.psql_db,
        )

    @computed_field
    @property
    def LOCATIONIQ_NEARBY_URL(self) -> str:
        return f'{self.locationiq_base_url}/nearby'

    @computed_field
    @property
    def LOCATIONIQ_SEARCH_URL(self) -> str:
        return f'{self.locationiq_base_url}/search'


settings = Settings()


@AuthJWT.load_config
def get_config() -> Settings:
    return settings
