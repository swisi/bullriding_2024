from flask import render_template, flash, redirect, url_for, request, Blueprint
from flask_login import current_user, login_user, logout_user, login_required

from app import db
from app.models import User, Participant
from app.forms import LoginForm, RegistrationForm, ParticipantForm  # Entfernen Sie TimeEntryForm

bp = Blueprint('main', __name__)

def check_round_passed(participants, round_number):
    if round_number == 1:
        return any(participant.round1_passed for participant in participants)
    elif round_number == 2:
        return any(participant.round2_passed for participant in participants)
    elif round_number == 3:
        return any(participant.round3_passed for participant in participants)
    elif round_number == 4:
        return any(participant.round4_passed for participant in participants)
    elif round_number == 5:
        return any(participant.round5_passed for participant in participants)
    return False

def get_current_round(participants):
    if not check_round_passed(participants, 1):
        return 1
    elif not check_round_passed(participants, 2):
        return 2
    elif not check_round_passed(participants, 3):
        return 3
    elif not check_round_passed(participants, 4):
        return 4
    elif not check_round_passed(participants, 5):
        return 5
    else:
        return 6

@bp.route('/')
@bp.route('/index')
@login_required
def index():
    participants = Participant.query.all() if current_user.is_authenticated else []
    #participants.sort(key=lambda p: p.start_nr if p.start_nr is not None else 0)  # Sortierung nach Startnummer
    participants.sort(key=lambda p: (
        p.time6 if p.time6 is not None else float('-inf'),
        p.time5 if p.time5 is not None else float('-inf'),
        p.time4 if p.time4 is not None else float('-inf'),
        p.time3 if p.time3 is not None else float('-inf'),
        p.time2 if p.time2 is not None else float('-inf'),
        p.time1 if p.time1 is not None else float('-inf')
    ), reverse=True)

    if participants is None:
        flash('Keine Teilnemer gefunden')
        form = ParticipantForm()
        return render_template('participant.html', title='Add Participant', form=form)
    
    # Get current_round from query parameter or calculate it dynamically
    current_round = request.args.get('current_round', default=None, type=int)
    if current_round is None:
        current_round = get_current_round(participants)
    
    return render_template(
        'index.html', 
        title='Home', 
        participants=participants, 
        round1_passed=check_round_passed(participants, 1),
        round2_passed=check_round_passed(participants, 2),
        round3_passed=check_round_passed(participants, 3),
        round4_passed=check_round_passed(participants, 4),
        round5_passed=check_round_passed(participants, 5),
        current_round=current_round
    )

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
    
    if 'update_times' in request.form:
        participant.time1 = request.form.get('time1', type=float)
        participant.time2 = request.form.get('time2', type=float)
        participant.time3 = request.form.get('time3', type=float)
        participant.time4 = request.form.get('time4', type=float)
        participant.time5 = request.form.get('time5', type=float)
        participant.time6 = request.form.get('time6', type=float)
        
        participant.round1_passed = 'round1_passed' in request.form
        participant.round2_passed = 'round2_passed' in request.form
        participant.round3_passed = 'round3_passed' in request.form
        participant.round4_passed = 'round4_passed' in request.form
        participant.round5_passed = 'round5_passed' in request.form
        participant.round6_passed = 'round6_passed' in request.form

        db.session.commit()
        flash('Times and round statuses updated successfully!', 'success')
    
    if 'set_active' in request.form:
        Participant.query.update({Participant.active: False})  # Setze alle auf inaktiv
        participant.active = True
        db.session.commit()
        flash('Active participant set successfully!', 'success')

    return redirect(url_for('main.index'))

@bp.route('/update_times_bulk', methods=['POST'])
@login_required
def update_times_bulk():
    participants = Participant.query.all()
    for participant in participants:
        participant.time1 = request.form.get(f'time1_{participant.id}', type=float)
        participant.round1_passed = f'round1_passed_{participant.id}' in request.form
        participant.time2 = request.form.get(f'time2_{participant.id}', type=float)
        participant.round2_passed = f'round2_passed_{participant.id}' in request.form
        participant.time3 = request.form.get(f'time3_{participant.id}', type=float)
        participant.round3_passed = f'round3_passed_{participant.id}' in request.form
        participant.time4 = request.form.get(f'time4_{participant.id}', type=float)
        participant.round4_passed = f'round4_passed_{participant.id}' in request.form
        participant.time5 = request.form.get(f'time5_{participant.id}', type=float)
        participant.round5_passed = f'round5_passed_{participant.id}' in request.form
        participant.time6 = request.form.get(f'time6_{participant.id}', type=float)
        participant.round6_passed = f'round6_passed_{participant.id}' in request.form

    db.session.commit()
    flash('Times and round statuses updated successfully!', 'success')
    return redirect(url_for('main.index'))


@bp.route('/finish_round/<int:round_number>', methods=['POST'])
@login_required
def finish_round(round_number):
    participants = Participant.query.all()
    
    for participant in participants:
        if round_number == 1:
            participant.round1_passed = f'round1_passed_{participant.id}' in request.form
        elif round_number == 2:
            participant.round2_passed = f'round2_passed_{participant.id}' in request.form
        elif round_number == 3:
            participant.round3_passed = f'round3_passed_{participant.id}' in request.form
        elif round_number == 4:
            participant.round4_passed = f'round4_passed_{participant.id}' in request.form
        elif round_number == 5:
            participant.round5_passed = f'round5_passed_{participant.id}' in request.form
        elif round_number == 6:
            participant.round6_passed = f'round6_passed_{participant.id}' in request.form

    db.session.commit()
    flash(f'Round {round_number} finished successfully!', 'success')
    
    # Increase the round_number after finishing the current round
    next_round = round_number + 1
    
    return redirect(url_for('main.index', current_round=next_round))

@bp.route('/set_active/<int:id>', methods=['POST'])
@login_required
def set_active(id):
    # Set all participants to inactive
    Participant.query.update({Participant.active: False})
    
    # Set the selected participant to active
    active_participant = Participant.query.get(id)
    if active_participant:
        active_participant.active = True
    
    db.session.commit()
    flash('Active participant set successfully!', 'success')
    return redirect(url_for('main.index'))

@bp.route('/ranking')
@login_required
def ranking():
    participants = Participant.query.all() if current_user.is_authenticated else []
    rankings = sorted(participants, key=lambda p: p.longest_time if p.longest_time is not None else 0, reverse=True)
    return render_template('ranking.html', title='Rangliste', rankings=rankings)
