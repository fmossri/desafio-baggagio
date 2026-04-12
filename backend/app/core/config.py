from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    app_name: str = "baggagio-challenge"
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

settings = Settings() #type: ignore[call-arg]