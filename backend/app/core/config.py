from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"
DB_FILE = BASE_DIR / "free_sd.db"


class Settings(BaseSettings):
    app_name: str = "Free SD API"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 1440

    database_url: str = f"sqlite:///{DB_FILE}"

    admin_email: str = "laila@potcsd.org"
    admin_password: str = "ChangeThis123!"

    otp_expire_minutes: int = 10
    password_reset_expire_minutes: int = 30

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()