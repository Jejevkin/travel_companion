from pydantic import Field
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    service_url: str = Field(default='http://127.0.0.1:5001')


test_settings = TestSettings()
