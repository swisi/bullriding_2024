from flask import render_template, flash, redirect, url_for, request, Blueprint
from flask_login import current_user, login_user, logout_user, login_required

from app import db
from app.models import User, Participant
from app.forms import LoginForm, RegistrationForm, ParticipantForm, TimeEntryForm

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    participants = Participant.query.all() if current_user.is_authenticated else []
    form = TimeEntryForm()
    return render_template('index.html', title='Home', participants=participants, form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.index'))
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/participant', methods=['GET', 'POST'])
@login_required
def participant():
    form = ParticipantForm()
    if form.validate_on_submit():
        participant = Participant()
        form.update_data(participant)
        db.session.add(participant)
        db.session.commit()
        flash('Participant added successfully!')
        return redirect(url_for('main.index'))
    else:
        print("Form validation failed")
    return render_template('participant.html', title='Add Participant', form=form)

@bp.route('/participant_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def participant_edit(id):
    participant = Participant.query.get_or_404(id)
    form = ParticipantForm(obj=participant)
    if form.validate_on_submit():
        form.update_data(participant)
        db.session.commit()
        flash('Participant updated successfully!')
        return redirect(url_for('main.index'))
    else:
        print("Form validation failed")
    form.load_data(participant)
    form.shortest_time.data = participant.shortest_time
    return render_template('participant_edit.html', title='Edit Participant', form=form)

@bp.route('/add_time', methods=['POST'])
@login_required
def add_time():
    form = TimeEntryForm()
    if form.validate_on_submit():
        rider = form.rider.data
        new_time = form.time.data
        participant = Participant.query.filter_by(start_nr=rider).first()

        if participant:
            # Update existing participant
            times = [participant.time1, participant.time2, participant.time3, participant.time4, participant.time5]
            for i in range(len(times)):
                if times[i] is None:
                    times[i] = new_time
                    break
            participant.time1, participant.time2, participant.time3, participant.time4, participant.time5 = times
            db.session.commit()
            flash('Time entry added successfully!')
        else:
            flash('Participant not found')
    return redirect(url_for('main.index'))
