import os
from dotenv import load_dotenv


class Config:
    REQUIRED_KEYS = [
        "DATABASE_USER",
        "DATABASE_PASSWORD",
        "DATABASE_HOST",
        "DATABASE_PORT",
        "DATABASE_NAME",
    ]
    
    def __init__(self):
        load_dotenv()

        self.DATABASE_USER = os.environ.get("DATABASE_USER", None)
        self.DATABASE_PASSWORD = os.environ.get("DATABASE_PASSWORD", None)
        self.DATABASE_HOST = os.environ.get("DATABASE_HOST", None)
        self.DATABASE_PORT = os.environ.get("DATABASE_PORT", None)
        self.DATABASE_NAME = os.environ.get("DATABASE_NAME", None)

    @property
    def DATABASE_URL(self):
        return f"postgresql+psycopg2://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

config = Config()