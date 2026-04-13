from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    app_name: str = "desafio-fullstack-gestao-de-produtos"
    debug: bool = False
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    rabbitmq_url: str
    messaging_retry_ttl_ms: int = 5000
    messaging_max_attempts: int = 8
    outbox_batch_size: int = 100
    outbox_poll_interval_seconds: int = 2

    cors_origins: str = Field(
        default="http://localhost:4200,http://127.0.0.1:4200",
        validation_alias="CORS_ORIGINS",
    )
    cors_allow_credentials: bool = Field(
        default=True,
        validation_alias="CORS_ALLOW_CREDENTIALS",
    )

    redis_url: str = Field(
        default="redis://localhost:6379/0",
        validation_alias="REDIS_URL",
    )
    refresh_token_expire_days: int = Field(default=7, validation_alias="REFRESH_TOKEN_EXPIRE_DAYS")
    rate_limit_login_per_minute: int = Field(
        default=10,
        validation_alias="RATE_LIMIT_LOGIN_PER_MINUTE",
)
settings = Settings() #type: ignore[call-arg]
