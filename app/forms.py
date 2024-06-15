from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, HiddenField, FloatField, SelectField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from app.models import User, Participant

class LoginForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember_me = BooleanField('Angemeldet bleiben')
    submit = SubmitField('Anmelden')

class RegistrationForm(FlaskForm):
    username = StringField('Benutzername', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    password2 = PasswordField(
        'Passwort wiederholen', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrieren')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Bitte einen anderen Benutzernamen verwenden.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Bitte eine andere Mailadresse verwenden')

class ParticipantForm(FlaskForm):
    id = HiddenField('ID')
    start_nr = IntegerField('Start Number')
    first_name = StringField('Vorname', validators=[DataRequired()])
    last_name = StringField('Name', validators=[DataRequired()])
    address = StringField('Addresse', validators=[DataRequired()])
    postal_code = StringField('PLZ', validators=[DataRequired()])
    city = StringField('Ort', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    phone = StringField('Telefon')
    time1 = StringField('Zeit 1')
    time2 = StringField('Zeit 2')
    time3 = StringField('Zeit 3')
    time4 = StringField('Zeit 4')
    time5 = StringField('Zeit 5')
    longest_time = StringField('Längste Zeit', render_kw={'readonly': True})
    submit = SubmitField('Speichern')

    def load_data(self, participant):
        self.id.data = participant.id
        self.start_nr.data = participant.start_nr
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
        self.longest_time.data = participant.longest_time

    def update_data(self, participant):
        participant.start_nr = self.start_nr.data
        participant.first_name = self.first_name.data
        participant.last_name = self.last_name.data
        participant.address = self.address.data
        participant.postal_code = self.postal_code.data
        participant.city = self.city.data
        participant.email = self.email.data
        participant.phone = self.phone.data
        participant.time1 = self._convert_to_float(self.time1.data)
        participant.time2 = self._convert_to_float(self.time2.data)
        participant.time3 = self._convert_to_float(self.time3.data)
        participant.time4 = self._convert_to_float(self.time4.data)
        participant.time5 = self._convert_to_float(self.time5.data)

    def validate_start_nr(self, start_nr):
        if Participant.query.filter(Participant.id != self.id.data, Participant.start_nr == start_nr.data).first():
            raise ValidationError('This start number is already in use. Please choose a different one.')

    def _convert_to_float(self, value):
        try:
            return float(value) if value.strip() else None
        except ValueError:
            return None
