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

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        flash('Welcome back!', 'success')
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
        flash('Congratulations, you are now a registered user!', 'success')
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
        flash('Participant added successfully!', 'success')
        return redirect(url_for('main.index'))
    else:
        #flash("Form validation failed", 'warning')
        pass
    return render_template('participant.html', title='Add Participant', form=form)

@bp.route('/participant_edit/<int:id>', methods=['GET', 'POST'])
@login_required
def participant_edit(id):
    participant = Participant.query.get_or_404(id)
    form = ParticipantForm(obj=participant)
    if form.validate_on_submit():
        form.update_data(participant)
        db.session.commit()
        flash('Participant updated successfully!', 'success')
        return redirect(url_for('main.index'))
    else:
        #flash('Form validation failed', 'warning')
        pass
    form.load_data(participant)
    form.longest_time.data = participant.longest_time
    return render_template('participant_edit.html', title='Edit Participant', form=form, participant=participant)

@bp.route('/participant_delete/<int:id>', methods=['POST', 'GET'])
@login_required
def participant_delete(id):
    participant = Participant.query.get_or_404(id)
    db.session.delete(participant)
    db.session.commit()
    flash('Participant deleted successfully!', 'success')
    return redirect(url_for('main.index'))


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
    flash('Times updated successfully!', 'success')
    return redirect(url_for('main.index'))
