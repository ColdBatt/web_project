import datetime
import sqlalchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import orm
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String,
                              index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime,
                                     default=datetime.datetime.now)
    configuration = sqlalchemy.Column(sqlalchemy.Text)

    assemblies = orm.relation('Assembly', back_populates='user')

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class Assembly(SqlAlchemyBase):
    __tablename__ = 'assemblies'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    cpu = sqlalchemy.Column(sqlalchemy.String)
    cooling = sqlalchemy.Column(sqlalchemy.String)
    ram = sqlalchemy.Column(sqlalchemy.String)
    videocard = sqlalchemy.Column(sqlalchemy.String)
    HDD = sqlalchemy.Column(sqlalchemy.String)
    SSDdisk1 = sqlalchemy.Column(sqlalchemy.String)
    SSDdisk2 = sqlalchemy.Column(sqlalchemy.String)
    DVDdrive = sqlalchemy.Column(sqlalchemy.String)
    Housing = sqlalchemy.Column(sqlalchemy.String)
    PowerSupply = sqlalchemy.Column(sqlalchemy.String)
    WiFiadapter = sqlalchemy.Column(sqlalchemy.String)
    Soundcard = sqlalchemy.Column(sqlalchemy.String)


    user = orm.relation('User')