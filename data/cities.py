import sqlalchemy
from .db_session_cities import SqlAlchemyBase


class City(SqlAlchemyBase):
    __tablename__ = 'cities'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String)
