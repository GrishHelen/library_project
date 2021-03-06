from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired
from flask_restful import abort, Resource
from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import sqlalchemy
from sqlalchemy import orm
from flask_login import UserMixin


class NewTeacher(FlaskForm):
    surname = StringField('Фамилия*', validators=[DataRequired()])
    name = StringField('Имя*', validators=[DataRequired()])
    father = StringField('Отчество')
    position = StringField('Должность*', validators=[DataRequired()])
    code = IntegerField('Номер пропускной карточки*', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class NewStudent(FlaskForm):
    surname = StringField('Фамилия*', validators=[DataRequired()])
    name = StringField('Имя*', validators=[DataRequired()])
    father = StringField('Отчество')
    clas = IntegerField('В каком Вы классе?*', validators=[DataRequired()])
    code = IntegerField('Номер пропускной карточки*', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class GiveBook(FlaskForm):
    book = StringField('Штрих-код книги*', validators=[DataRequired()])
    person_code = IntegerField('Номер пропускной карточки человека*', validators=[DataRequired()])
    submit = SubmitField('Выдать')


class TakeBook(FlaskForm):
    book = StringField('Штрих-код книги*', validators=[DataRequired()])
    person_code = IntegerField('Номер пропускной карточки человека*', validators=[DataRequired()])
    submit = SubmitField('Принять')


class NewBook(FlaskForm):
    author = StringField('Автор*', validators=[DataRequired()])
    name = StringField('Название*', validators=[DataRequired()])
    subject = StringField('Предмет')
    clas = StringField('Класс')
    yeartown = StringField('Год издания')
    publisher = StringField('Издательство')
    number = StringField('Номер издания')
    date = StringField('Дата постановки на учет')
    quantity = StringField('Количество')
    price = StringField('Цена')
    sum = StringField('Общая сумма')
    consignment = StringField('Накладная')
    datecon = StringField('Дата по накладной')
    numberinlist = StringField('П/П')
    set_1 = StringField('КСУ')
    decomission = StringField('Акт выбытия')
    notes = StringField('Примечания')
    code = StringField('Штрих-код*', validators=[DataRequired()])
    submit = SubmitField('Сохранить')
