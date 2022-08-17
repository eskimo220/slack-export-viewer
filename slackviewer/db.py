import sqlalchemy
import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    team = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    json = sqlalchemy.Column(sqlalchemy.Text)
    last_updated = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now,
                                     onupdate=datetime.datetime.now)


class Channel(Base):
    __tablename__ = 'channels'
    team = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    type = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    json = sqlalchemy.Column(sqlalchemy.Text)
    last_updated = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now,
                                     onupdate=datetime.datetime.now)


class Message(Base):
    __tablename__ = 'messages'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    team = sqlalchemy.Column(sqlalchemy.String)
    channel = sqlalchemy.Column(sqlalchemy.String)
    ts = sqlalchemy.Column(sqlalchemy.String)
    json = sqlalchemy.Column(sqlalchemy.Text)
    last_updated = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now,
                                     onupdate=datetime.datetime.now)


engine = sqlalchemy.create_engine(DATABASE_URL)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

# session = Session()
# print(session.merge(User(team="123", json="456")))
# session.commit()


def getAll():
    session = Session()
    try:
        return {
            "users": session.query(users),
            "channels": session.query(channels),
            "messages": session.query(messages),
        }
        session.commit()
    finally:
        session.close()
