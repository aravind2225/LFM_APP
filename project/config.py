import os
from dotenv import load_dotenv
 
load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    
    DB_USER = os.getenv("user")
    DB_PASSWORD = os.getenv("password")
    DB_HOST =os.getenv("host")
    DB_PORT = os.getenv("port")
    DB_NAME = os.getenv("dbname")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
