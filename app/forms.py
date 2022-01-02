from flask_wtf import FlaskForm
from wtforms import TextField, StringField, PasswordField, BooleanField, SubmitField, IntegerField, FloatField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from wtforms.fields.html5 import TelField, DateField
from app.models import Users, DictYN, DictScore
import os
import phonenumbers
from flask_wtf.recaptcha import RecaptchaField

RECAPTCHA_PUBLIC_KEY = os.environ.get('CAPTCHA_PUB')
RECAPTCHA_PRIVATE_KEY = os.environ.get('CAPTCHA_PRIV')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    recaptcha = RecaptchaField()
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = TelField('Phone', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    recaptcha = RecaptchaField()
    submit = SubmitField('Register')


    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = Users.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = Users.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

class NewForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    restaurant_name = StringField('Restaurant Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    zip_code = StringField('ZIP Code', validators=[DataRequired()])
    overview = TextAreaField('Overview')
    tortilla_desc = TextAreaField('Tortilla', validators=[DataRequired()])
    tortilla_score = FloatField('Tortilla Score', validators=[DataRequired()])
    potato_desc = TextAreaField('Potato', validators=[DataRequired()])
    potato_score = FloatField('Potato Score', validators=[DataRequired()])
    texture_desc = TextAreaField('Texture', validators=[DataRequired()])
    texture_score = FloatField('Texture Score', validators=[DataRequired()])
    flavor_desc = TextAreaField('Flavor', validators=[DataRequired()])
    flavor_score = FloatField('Flavor Score', validators=[DataRequired()])
    general_desc = TextAreaField('General', validators=[DataRequired()])
    general_score = IntegerField('General Score', validators=[DataRequired()])
    smother = SelectField('Smothered?')
    smother_score = SelectField('+/-')
    published = SelectField('Active Post?')
    submit = SubmitField('Submit')

    def __init__(self):
        super(NewForm, self).__init__()
        self.published.choices = [(e.type, e.type) for e in DictYN.query.all()]
        self.smother_score.choices = [(e.type, e.type) for e in DictScore.query.all()]
        self.smother.choices = [(e.type, e.type) for e in DictYN.query.all()]


class ContactForm(FlaskForm):
    name = StringField('First Name', validators=[DataRequired()])
    email = email = StringField('Email', validators=[DataRequired(), Email()])
    subject = StringField('Subject', validators=[DataRequired()])
    message = TextAreaField('Message', validators=[DataRequired()])

class EditForm(FlaskForm):
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    restaurant_name = StringField('Restaurant Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    zip_code = StringField('ZIP Code', validators=[DataRequired()])
    overview = TextAreaField('Overview')
    tortilla_desc = TextAreaField('Tortilla', validators=[DataRequired()])
    tortilla_score = FloatField('Tortilla Score', validators=[DataRequired()])
    potato_desc = TextAreaField('Potato', validators=[DataRequired()])
    potato_score = FloatField('Potato Score', validators=[DataRequired()])
    texture_desc = TextAreaField('Texture', validators=[DataRequired()])
    texture_score = FloatField('Texture Score', validators=[DataRequired()])
    flavor_desc = TextAreaField('Flavor', validators=[DataRequired()])
    flavor_score = FloatField('Flavor Score', validators=[DataRequired()])
    general_desc = TextAreaField('General', validators=[DataRequired()])
    general_score = IntegerField('General Score', validators=[DataRequired()])
    smother = SelectField('Smothered?')
    smother_score = SelectField('+/-')
    published = SelectField('Active Post?')
    submit = SubmitField('Submit')

    def __init__(self):
        super(EditForm, self).__init__()
        self.published.choices = [(e.type, e.type) for e in DictYN.query.all()]
        self.smother.choices = [(e.type, e.type) for e in DictYN.query.all()]
        self.smother_score.choices = [(e.type, e.type) for e in DictScore.query.all()]