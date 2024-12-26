from os import environ, getenv
from pydantic import BaseModel, SecretStr
from dotenv import load_dotenv

load_dotenv(".env")


class Settings(BaseModel):
    BOT_TOKEN: SecretStr
    APP_TOKEN: SecretStr
    URL: SecretStr


SETTINGS = Settings(**environ)
