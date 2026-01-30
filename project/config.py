class Config:
    SECRET_KEY = "dev-secret-key"

    DB_USER = "postgres.bbyqpjdlmrvqdegpbygy"
    DB_PASSWORD = "tjs@cW%$b&598V6"
    DB_HOST = "aws-1-ap-south-1.pooler.supabase.com"
    DB_PORT = "6543"
    DB_NAME = "postgres"

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
