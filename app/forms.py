from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class ParticipantForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    postal_code = StringField('Postal Code', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Phone', validators=[DataRequired()])
    time1 = StringField('Time 1', validators=[DataRequired()])
    time2 = StringField('Time 2', validators=[DataRequired()])
    time3 = StringField('Time 3', validators=[DataRequired()])
    time4 = StringField('Time 4', validators=[DataRequired()])
    time5 = StringField('Time 5', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def load_data(self, participant):
        self.first_name.data = participant.first_name
        self.last_name.data = participant.last_name
        self.address.data = participant.address
        self.postal_code.data = participant.postal_code
        self.city.data = participant.city
        self.email.data = participant.email
        self.phone.data = participant.phone
        self.time1.data = participant.time1
        self.time2.data = participant.time2
        self.time3.data = participant.time3
        self.time4.data = participant.time4
        self.time5.data = participant.time5

    def update_data(self, participant):
        participant.first_name = self.first_name.data
        participant.last_name = self.last_name.data
        participant.address = self.address.data
        participant.postal_code = self.postal_code.data
        participant.city = self.city.data
        participant.email = self.email.data
        participant.phone = self.phone.data
        participant.time1 = self.time1.data
        participant.time2 = self.time2.data
        participant.time3 = self.time3.data
        participant.time4 = self.time4.data
        participant.time5 = self.time5.data

