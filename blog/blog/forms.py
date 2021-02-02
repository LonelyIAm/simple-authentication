from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from flask_login import current_user
from wtforms import BooleanField, StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from blog.models import User


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken, choose another one!')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email address is taken, choose another one!')

class UpdateAccountForm(FlaskForm):
    username = username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user and user is current_user:
            raise ValidationError('That username is taken, choose another one!')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and user is current_user:
            raise ValidationError('That email address is taken, choose another one!')


