import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class Jobs(SqlAlchemyBase):
    __tablename__ = 'job'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    team_leader = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("user.id"))
    job = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    work_size = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    collaborators = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    start_date = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    end_date = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean, nullable=True)
    user = orm.relation('User')

    def __repr__(self):
        return f'{self.job}/{self.user}/{self.work_size}/{self.collaborators}/{self.is_finished}/' \
               f'{self.id}/{self.team_leader}'


class JobsForm(FlaskForm):
    job = StringField('Название объявлнеия')
    work_size = IntegerField("Цена")
    collaborators = StringField("Описание")
    start_date = StringField("Начало работы объявления")
    end_date = StringField("Конец работы объявления")
    is_finished = BooleanField('Доставка')
    submit = SubmitField('Применить')
