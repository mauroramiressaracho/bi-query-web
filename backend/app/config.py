from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_engine: str = "demo"
    db_host: str = ""
    db_port: int | None = None
    db_database: str = ""
    db_service: str = ""
    db_user: str = ""
    db_password: str = ""
    db_schema: str = ""
    odbc_driver: str = "ODBC Driver 17 for SQL Server"
    cors_origins: str = "http://localhost:5173"
    max_query_rows: int = 500

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]


settings = Settings()
