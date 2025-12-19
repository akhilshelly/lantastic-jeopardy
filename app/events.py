import logging

from flask import request
from flask_socketio import emit, join_room

from app import socketio
from app.game_logic import game_manager
from app.models import QuestionState
from config import Config

active_timers = {}

logger = logging.getLogger(__name__)

@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")
    emit('connection_response', {'status': 'connected', 'sid': request.sid})
    # Send current game state to newly connected client
    emit('game_update', game_manager.get_game_summary())


@socketio.on('request_game_state')
def handle_request_game_state():
    """Client requests current game state."""
    emit('game_update', game_manager.get_game_summary())


@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")
    # Mark player as disconnected
    for player in game_manager.state.players.values():
        if player.session_id == request.sid:
            player.connected = False
            emit('game_update', game_manager.get_game_summary(), broadcast=True)
            break


@socketio.on('register_trebek')
def handle_register_trebek():
    """Register Trebek user."""
    game_manager.set_trebek(request.sid)
    game_manager.load_questions()
    join_room('trebek')
    emit('registration_success', {'role': 'trebek'})
    emit('game_update', game_manager.get_game_summary())


@socketio.on('register_display')
def handle_register_display():
    """Register display screen."""
    join_room('display')
    emit('registration_success', {'role': 'display'})
    emit('game_update', game_manager.get_game_summary())

    # Send current board if in a round
    if game_manager.state.phase.value in ['round_1', 'round_2']:
        round_num = 1 if game_manager.state.phase.value == 'round_1' else 2
        emit('board_update', {
            'round': round_num,
            'board': game_manager.get_board_state(round_num)
        })


@socketio.on('create_team')
def handle_create_team(data):
    """Create a new team."""
    team_name = data.get('name', '').strip()
    if not team_name:
        emit('error', {'message': 'Team name required'})
        return

    team = game_manager.create_team(team_name)
    logger.info(f"Team created: {team.name} (ID: {team.id})")
    emit('game_update', game_manager.get_game_summary(), broadcast=True)


@socketio.on('join_game')
def handle_join_game(data):
    """Player joins a team."""
    player_name = data.get('name', '').strip()
    team_id = data.get('team_id', '').strip()

    if not player_name or not team_id:
        emit('error', {'message': 'Name and team required'})
        return

    player = game_manager.add_player(player_name, team_id, request.sid)
    if not player:
        emit('error', {'message': 'Invalid team'})
        return

    join_room('players')
    join_room(team_id)

    emit('registration_success', {
        'role': 'player',
        'player_id': player.id,
        'team_id': team_id
    })
    emit('game_update', game_manager.get_game_summary(), broadcast=True)


@socketio.on('reconnect_player')
def handle_reconnect_player(data):
    """Player attempts to reconnect with existing ID."""
    player_id = data.get('player_id')
    team_id = data.get('team_id')

    # Verify player exists
    player = game_manager.state.players.get(player_id)
    if player and player.team_id == team_id:
        # Update session ID and mark as connected
        player.session_id = request.sid
        player.connected = True

        join_room('players')
        join_room(team_id)

        emit('registration_success', {
            'role': 'player',
            'player_id': player.id,
            'team_id': team_id
        })
        emit('game_update', game_manager.get_game_summary(), broadcast=True)
    else:
        # Player not found or invalid - clear localStorage on client
        emit('reconnect_failed')


@socketio.on('start_round')
def handle_start_round(data):
    """Start a game round."""
    if request.sid != game_manager.state.trebek_session_id:
        emit('error', {'message': 'Unauthorized'})
        return

    round_num = data.get('round', 1)
    game_manager.start_round(round_num)

    emit('game_update', game_manager.get_game_summary(), broadcast=True)
    emit('board_update', {
        'round': round_num,
        'board': game_manager.get_board_state(round_num)
    }, broadcast=True)


@socketio.on('select_question')
def handle_select_question(data):
    """Trebek selects a question."""
    if request.sid != game_manager.state.trebek_session_id:
        emit('error', {'message': 'Unauthorized'})
        return

    category = data.get('category')
    value = data.get('value')

    question = game_manager.select_question(category, value)
    if not question:
        emit('error', {'message': 'Question not available'})
        return

    emit('game_update', game_manager.get_game_summary(), broadcast=True)

    # Start buzz delay timer
    def enable_buzzing_callback():
        import time
        time.sleep(Config.BUZZ_DELAY_SECONDS)
        game_manager.enable_buzzing()
        socketio.emit('game_update', game_manager.get_game_summary())

    socketio.start_background_task(enable_buzzing_callback)


@socketio.on('buzz')
def handle_buzz(data):
    """Player buzzes in."""
    player_id = data.get('player_id')

    success = game_manager.buzz_in(player_id)
    if success:
        emit('game_update', game_manager.get_game_summary(), broadcast=True)
    else:
        emit('buzz_rejected', {'reason': 'Already buzzed or team already attempted'})


@socketio.on('adjudicate')
def handle_adjudicate(data):
    """Trebek adjudicates an answer."""
    if request.sid != game_manager.state.trebek_session_id:
        emit('error', {'message': 'Unauthorized'})
        return

    correct = data.get('correct', False)

    # Prepare defaults to avoid referencing undefined variables
    player_name = None
    team_id = None
    old_score = None

    # Get current buzzer info before adjudication if present
    if game_manager.state.buzz_queue:
        current_buzzer = game_manager.state.buzz_queue[0]
        player_name = getattr(current_buzzer, 'player_name', None)
        team_id = getattr(current_buzzer, 'team_id', None)
        team = game_manager.state.teams.get(team_id) if team_id else None
        if team:
            old_score = team.score

    # Perform adjudication which updates game state
    next_player_id, score_change = game_manager.adjudicate_answer(correct)

    # Determine authoritative new score if we have a team_id
    new_score = None
    if team_id:
        team_after = game_manager.state.teams.get(team_id)
        if team_after:
            new_score = team_after.score

    # Always broadcast updated game state so Trebek/Jennings see changes
    emit('game_update', game_manager.get_game_summary(), broadcast=True)

    # Send score update to display when we have a valid team to report on
    if team_id:
        payload = {
            'player_name': player_name,
            'team_id': team_id,
            'correct': correct,
            'score_change': score_change,
            'old_score': old_score,
            'new_score': new_score
        }
        print('Emitting score_update to display:', payload)
        emit('score_update', payload, to='display')
    else:
        if correct and not team_id:
            print('Warning: adjudicate marked correct but no buzzer/team found; skipping score_update emit')

    # If question ended (no current question), update the board for all displays
    current_round = 1 if game_manager.state.phase.value == 'round_1' else 2
    if game_manager.state.current_question is None:
        emit('board_update', {
            'round': current_round,
            'board': game_manager.get_board_state(current_round)
        }, broadcast=True)


@socketio.on('skip_question')
def handle_skip_question():
    """Trebek manually skips the current question and returns to the board."""
    if request.sid != game_manager.state.trebek_session_id:
        emit('error', {'message': 'Unauthorized'})
        return

    # Clear current question and reset relevant state
    game_manager.state.current_question = None
    game_manager.state.buzz_queue = []
    game_manager.state.teams_attempted = []
    game_manager.state.question_state = QuestionState.BOARD_ACTIVE

    # Broadcast updates so all clients return to board
    emit('game_update', game_manager.get_game_summary(), broadcast=True)
    current_round = 1 if game_manager.state.phase.value == 'round_1' else 2
    emit('board_update', {
        'round': current_round,
        'board': game_manager.get_board_state(current_round)
    }, broadcast=True)
