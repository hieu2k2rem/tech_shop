from wtforms import Form, StringField, TextAreaField, PasswordField, SubmitField, validators, ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_wtf import FlaskForm
from .models import Register

class CustomerRegisterForm(FlaskForm):
    name = StringField('Name: ')
    username = StringField('Username: ', [validators.DataRequired()])
    email = StringField('Email: ', [validators.Email(), validators.DataRequired()])
    password = PasswordField('Password: ', [validators.DataRequired(),
                                            validators.EqualTo('confirm', message='Both pass word must  match! ')])
    confirm = PasswordField('Repeat password: ', [validators.DataRequired()])
    country = StringField('Country: ', [validators.DataRequired()])
    state = StringField('State: ', [validators.DataRequired()])
    city = StringField('City: ', [validators.DataRequired()])
    contact = StringField('Contact: ', [validators.DataRequired()])
    address = StringField('Address: ', [validators.DataRequired()])
    zipcode = StringField('Zipcode: ', [validators.DataRequired()])

    profile = FileField('Profile', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'],
                                                           'Image only please')])

    submit = SubmitField('Register')

    # Viết hàm thông báo nếu khai báo trùng username và email trong form
    def validate_username(self, username):
        if Register.query.filter_by(username=username.data).first():
            raise ValidationError('This useranme is already in use!')

    def validate_email(self, email):
        if Register.query.filter_by(email=email.data).first():
            raise ValidationError('This email is already in use!')


class CustomerLoginForm(FlaskForm):
    email = StringField('Email: ', [validators.Email(), validators.DataRequired()])
    password = StringField('Password: ', [validators.DataRequired()])


