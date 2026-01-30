class Config:
    SECRET_KEY = "dev-secret-key"

    DB_USER = "postgres"
    DB_PASSWORD = "techv1%403"
    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "log_file"

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
