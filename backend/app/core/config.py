from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "WSJF Excel Generator"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    # CORS
    ALLOWED_HOSTS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Database
    DATABASE_URL: str = "wsjf.db"

    # Excel
    EXCEL_EXPORT_PATH: str = "./exports/"

    class Config:
        env_file = ".env"


settings = Settings()
