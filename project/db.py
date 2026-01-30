from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = None
db_session = scoped_session(sessionmaker())

def init_db(app):
    global engine
    engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], echo=False)
    db_session.configure(bind=engine)

def get_db():
    return db_session
