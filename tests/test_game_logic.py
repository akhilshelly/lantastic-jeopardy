import pytest

from app.game_logic import GameManager
from app.models import Question, BuzzEntry, QuestionState


def setup_simple_game():
    gm = GameManager()
    # Create two teams and players
    t1 = gm.create_team('Alpha')
    t2 = gm.create_team('Beta')

    p1 = gm.add_player('Alice', t1.id, 's1')
    p2 = gm.add_player('Bob', t2.id, 's2')

    # Create a question and set as current
    q = Question(round=1, category='Cat', value=100, question='Q?', answer='A')
    gm.state.questions = [q]
    gm.state.current_question = q
    gm.state.question_state = QuestionState.BUZZING_OPEN
    gm.state.buzz_timer_active = False

    return gm, t1, t2, p1, p2


def test_adjudicate_correct_clears_question():
    gm, t1, t2, p1, p2 = setup_simple_game()

    # Simulate buzz from player 1
    gm.state.buzz_queue = [
        BuzzEntry(player_id=p1.id, player_name=p1.name, team_id=p1.team_id, team_name=gm.state.teams[p1.team_id].name,
                  timestamp=0)
    ]

    next_player, score_change = gm.adjudicate_answer(True)

    assert next_player is None
    assert score_change == 100
    assert gm.state.current_question is None
    assert gm.state.buzz_queue == []
    assert gm.state.question_state == QuestionState.BOARD_ACTIVE
    assert gm.state.teams_attempted == []
    assert gm.state.teams[t1.id].score == 100


def test_adjudicate_wrong_no_queued_buzzers_keeps_question_open():
    gm, t1, t2, p1, p2 = setup_simple_game()

    # Simulate buzz from player 1, but no other buzzers
    gm.state.buzz_queue = [
        BuzzEntry(player_id=p1.id, player_name=p1.name, team_id=p1.team_id, team_name=gm.state.teams[p1.team_id].name,
                  timestamp=0)
    ]

    # Ensure team list has at least two teams so remaining_teams will be non-empty
    assert len(gm.state.teams) >= 2

    next_player, score_change = gm.adjudicate_answer(False)

    # After wrong, since there are remaining teams, question should remain active and allow buzzing
    assert next_player is None
    assert score_change == -100
    assert gm.state.current_question is not None
    assert gm.state.question_state == QuestionState.BUZZING_OPEN
    assert p1.team_id in gm.state.teams_attempted
    assert gm.state.teams[t1.id].score == -100


if __name__ == '__main__':
    pytest.main(['-q'])
