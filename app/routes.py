from flask import render_template, flash, redirect, url_for, request, Blueprint
from flask_login import current_user, login_user, logout_user, login_required

from app import db
from app.models import User, Participant
from app.forms import LoginForm, RegistrationForm, ParticipantForm

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
def index():
    if not current_user.is_authenticated:
        participants = Participant.query.all()
        rankings = sorted(participants, key=lambda p: (
            p.toptime_Finalrunde if p.toptime_Finalrunde is not None else float('-inf'),
            p.toptime_Zwischenrunde if p.toptime_Zwischenrunde is not None else float('-inf'),
            p.toptime_Vorrunde if p.toptime_Vorrunde is not None else float('-inf')
        ), reverse=True)

        return render_template('ranking.html', title='Rangliste', rankings=rankings)

    participants = Participant.query.all()
    participants.sort(key=lambda p: (
            p.toptime_Finalrunde if p.toptime_Finalrunde is not None else float('-inf'),
            p.toptime_Zwischenrunde if p.toptime_Zwischenrunde is not None else float('-inf'),
            p.toptime_Vorrunde if p.toptime_Vorrunde is not None else float('-inf')
    ), reverse=True)

    if not participants:
        flash('Keine Teilnehmer gefunden')
        form = ParticipantForm()
        return render_template('participant.html', title='Teilnehmer hinzufügen', form=form)
    
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

@bp.route('/participants')
@login_required
def participant():
    participants = Participant.query.all()
    return render_template('participant.html', title='Alle Teilnehmer', participants=participants)

@bp.route('/participant_add', methods=['GET', 'POST'])
@login_required
def participant_add():
    form = ParticipantForm()
    if form.validate_on_submit():
        participant = Participant()
        form.update_data(participant)
        db.session.add(participant)
        db.session.commit()
        flash('Participant added successfully!', 'success')
        return redirect(url_for('main.index'))
    return render_template('participant_add.html', title='Add Participant', form=form)

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
        Participant.query.update({Participant.active: False})
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

@bp.route('/finish_round/<string:round>', methods=['POST'])
@login_required
def finish_round(round):
    

    if round == 'VR1':
        participants = Participant.query.all()
        # Sortiere Teilnehmer nach Zeit in der ersten Vorrunde in absteigender Reihenfolge
        sorted_participants = sorted(participants, key=lambda p: p.time1 if p.time1 is not None else float('-inf'), reverse=True)

        # Ausgabe der sortierten Teilnehmer zur Überprüfung
        #print("Sortierte Teilnehmer in VR1:")
        #for participant in sorted_participants:
        #    print(f"Teilnehmer ID: {participant.id}, Zeit: {participant.time1}")


        # Setze alle Teilnehmer auf nicht qualifiziert
        for participant in participants:
            participant.round1_qualified = False
            participant.round1_passed = False

        # Qualifiziere alle Teilnehmer mit Zeit >= 99 Sekunden
        qualified_participants = []
        for participant in participants:
            if participant.time1 is not None and participant.time1 >= 99:
                participant.round1_qualified = True
                participant.round2_qualified = True
                participant.round3_qualified = True
                participant.round1_passed = False
                qualified_participants.append(participant)

        # Fülle die Qualifikationen auf, bis mindestens 5 Teilnehmer qualifiziert sind
        for participant in sorted_participants:
            if len(qualified_participants) < 5:
                if not participant.round1_qualified:  # Nur nicht bereits qualifizierte Teilnehmer hinzufügen
                    participant.round1_qualified = True
                    participant.round2_qualified = True
                    participant.round3_qualified = True
                    participant.round1_passed = False
                    qualified_participants.append(participant)
            else:
                break

        # Setze alle Teilnehmer auf "Runde 1 bestanden"
        for participant in participants:
            if participant.round1_qualified == True:
                pass
            else:
                participant.round1_passed = True

    elif round == 'VR2':
        participants = Participant.query.all()
        # Sortiere Teilnehmer nach Zeit in der ersten Vorrunde in absteigender Reihenfolge
        sorted_participants = sorted(participants, key=lambda p: p.time2 if p.time2 is not None else float('-inf'), reverse=True)

        # Ausgabe der sortierten Teilnehmer zur Überprüfung
        #print("Sortierte Teilnehmer in VR1:")
        #for participant in sorted_participants:
        #    print(f"Teilnehmer ID: {participant.id}, Zeit: {participant.time1}")


        # Setze alle Teilnehmer auf nicht qualifiziert
        for participant in participants:
            participant.round2_passed = False

        # Qualifiziere alle Teilnehmer mit Zeit >= 99 Sekunden
        qualified_participants = []
        for participant in participants:
            if participant.time2 is not None and participant.time2 >= 99:
                participant.round2_qualified = True
                participant.round3_qualified = True
                participant.round2_passed = False
                qualified_participants.append(participant)

        # Fülle die Qualifikationen auf, bis mindestens 5 Teilnehmer qualifiziert sind
        for participant in sorted_participants:
            if len(qualified_participants) < 5:
                if not participant.round2_qualified :  # Nur nicht bereits qualifizierte Teilnehmer hinzufügen
                    participant.round2_qualified = True
                    participant.round3_qualified = True
                    participant.round2_passed = False
                    qualified_participants.append(participant)
            else:
                break

        # Setze alle Teilnehmer auf "Runde 1 bestanden"
        for participant in participants:
            if participant.round2_qualified == True:
                pass
            else:
                participant.round2_passed = True

    elif round == 'VR3':
        participants = Participant.query.all()
        # Sortiere Teilnehmer nach Zeit in der ersten Vorrunde in absteigender Reihenfolge
        sorted_participants = sorted(participants, key=lambda p: p.time3 if p.time3 is not None else float('-inf'), reverse=True)

        # Ausgabe der sortierten Teilnehmer zur Überprüfung
        #print("Sortierte Teilnehmer in VR1:")
        #for participant in sorted_participants:
        #    print(f"Teilnehmer ID: {participant.id}, Zeit: {participant.time1}")


        # Setze alle Teilnehmer auf nicht qualifiziert
        for participant in participants:
            participant.round3_passed = False

        # Qualifiziere alle Teilnehmer mit Zeit >= 99 Sekunden
        qualified_participants = []
        for participant in participants:
            if participant.time3 is not None and participant.time3 >= 99:
                participant.round3_qualified = True
                participant.round3_passed = False
                qualified_participants.append(participant)

        # Fülle die Qualifikationen auf, bis mindestens 5 Teilnehmer qualifiziert sind
        for participant in sorted_participants:
            if len(qualified_participants) < 5:
                if not participant.round3_qualified :  # Nur nicht bereits qualifizierte Teilnehmer hinzufügen
                    participant.round3_qualified = True
                    participant.round3_passed = False
                    qualified_participants.append(participant)
            else:
                break

        # Setze alle Teilnehmer auf "Runde 1 bestanden"
        for participant in participants:
            if participant.round3_qualified == True:
                pass
            else:
                participant.round3_passed = True

    elif round == 'ZR1':
        for participant in participants:
            participant.round4_passed = True
    elif round == 'ZR2':
        for participant in participants:
            participant.round5_passed = True
    elif round == 'FINAL':
        for participant in participants:
            participant.round6_passed = True

    db.session.commit()
    flash(f'Runde {round} abgeschlossen!', 'success')
    
    return redirect(url_for('main.index'))


@bp.route('/set_active/<int:id>', methods=['POST'])
@login_required
def set_active(id):
    Participant.query.update({Participant.active: False})
    active_participant = Participant.query.get(id)
    if active_participant:
        active_participant.active = True
    db.session.commit()
    flash('Active participant set successfully!', 'success')
    return redirect(url_for('main.index'))

@bp.route('/reset_results')
@login_required
def reset_results():
    participants = Participant.query.all()
    for participant in participants:
        participant.active = False
        participant.time1 = None
        participant.time2 = None
        participant.time3 = None
        participant.time4 = None
        participant.time5 = None
        participant.time6 = None
        participant.round1_passed = False
        participant.round2_passed = False
        participant.round3_passed = False
        participant.round4_passed = False
        participant.round5_passed = False
        participant.round6_passed = False
        participant.round1_qualified = False
        participant.round2_qualified = False
        participant.round3_qualified = False
        participant.round4_qualified = False
        participant.round5_qualified = False
        participant.round6_qualified = False
    
    db.session.commit()
    flash('All fields have been reset.', 'success')
    return redirect(url_for('main.index'))

@bp.route('/reset_participants')
@login_required
def reset_participants():
    Participant.query.delete()
    db.session.commit()
    flash('Alle Teilnehmer wurden gelöscht.', 'success')
    return redirect(url_for('main.participant'))

@bp.route('/ranking')
def ranking():
    participants = Participant.query.all()
    rankings = sorted(participants, key=lambda p: (
            p.toptime_Finalrunde if p.toptime_Finalrunde is not None else float('-inf'),
            p.toptime_Zwischenrunde if p.toptime_Zwischenrunde is not None else float('-inf'),
            p.toptime_Vorrunde if p.toptime_Vorrunde is not None else float('-inf')
    ), reverse=True)

    return render_template('ranking.html', title='Rangliste', rankings=rankings)
