import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class Games(SqlAlchemyBase):
    __tablename__ = 'games'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    start_date = sqlalchemy.Column(sqlalchemy.DATETIME, default=datetime.datetime.now())
    end_date = sqlalchemy.Column(sqlalchemy.DATETIME, default=datetime.datetime.now())
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    count_cities = sqlalchemy.Column(sqlalchemy.Integer)
