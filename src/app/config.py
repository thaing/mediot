from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:////app/mediot.db"
    KAFKA_BROKER: str = "localhost:9092"
    JWT_SECRET: str = "change-me-in-production-use-a-strong-secret"
    API_KEY: str = "change-me-device-api-key"

    OAUTH_GOOGLE_CLIENT_ID: str = ""
    OAUTH_GOOGLE_CLIENT_SECRET: str = ""
    OAUTH_APPLE_CLIENT_ID: str = ""
    OAUTH_APPLE_CLIENT_SECRET: str = ""
    OAUTH_FACEBOOK_CLIENT_ID: str = ""
    OAUTH_FACEBOOK_CLIENT_SECRET: str = ""

    CORS_ORIGINS: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
