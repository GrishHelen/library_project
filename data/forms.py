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
    surname = StringField('Введите фамилию*', validators=[DataRequired()])
    name = StringField('Введите имя*', validators=[DataRequired()])
    father = StringField('Введите отчество')
    position = StringField('Выберите должность*', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class NewStudent(FlaskForm):
    surname = StringField('Введите фамилию*', validators=[DataRequired()])
    name = StringField('Введите имя*', validators=[DataRequired()])
    father = StringField('Введите отчество')
    clas = IntegerField('В каком Вы классе?*', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class GiveBook(FlaskForm):
    book = StringField('Введите штрих-код книги*', validators=[DataRequired()])
    person = StringField('Введите ID человека*', validators=[DataRequired()])
    submit = SubmitField('Выдать')


class TakeBook(FlaskForm):
    book = StringField('Введите штрих-код книги*', validators=[DataRequired()])
    person = StringField('Введите ID человека*', validators=[DataRequired()])
    submit = SubmitField('Принять')
