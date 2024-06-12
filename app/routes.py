from flask import render_template, flash, redirect, url_for, request, Blueprint
from flask_login import current_user, login_user, logout_user, login_required

from app import db
from app.models import User, Participant
from app.forms import LoginForm, RegistrationForm, ParticipantForm  # Entfernen Sie TimeEntryForm

bp = Blueprint('main', __name__)

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    participants = Participant.query.all() if current_user.is_authenticated else []
    participants.sort(key=lambda p: p.longest_time if p.longest_time is not None else 0, reverse=True)
    return render_template('index.html', title='Home', participants=participants)

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

@bp.route('/update_times/<int:id>', methods=['POST'])
@login_required
def update_times(id):
    participant = Participant.query.get_or_404(id)
    participant.time1 = request.form.get('time1', type=float)
    participant.time2 = request.form.get('time2', type=float)
    participant.time3 = request.form.get('time3', type=float)
    participant.time4 = request.form.get('time4', type=float)
    participant.time5 = request.form.get('time5', type=float)
    
    db.session.commit()
    flash('Times updated successfully!')
    return redirect(url_for('main.index'))
