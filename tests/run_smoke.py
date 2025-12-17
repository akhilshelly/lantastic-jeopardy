from app.game_logic import GameManager
from app.models import Question, BuzzEntry, QuestionState


def setup_simple_game():
    gm = GameManager()
    t1 = gm.create_team('Alpha')
    t2 = gm.create_team('Beta')
    p1 = gm.add_player('Alice', t1.id, 's1')
    p2 = gm.add_player('Bob', t2.id, 's2')
    q = Question(round=1, category='Cat', value=100, question='Q?', answer='A')
    gm.state.questions = [q]
    gm.state.current_question = q
    gm.state.question_state = QuestionState.BUZZING_OPEN
    gm.state.buzz_timer_active = False
    return gm, t1, t2, p1, p2


def test_correct_flow():
    gm, t1, t2, p1, p2 = setup_simple_game()
    gm.state.buzz_queue = [
        BuzzEntry(player_id=p1.id, player_name=p1.name, team_id=p1.team_id, team_name=gm.state.teams[p1.team_id].name,
                  timestamp=0)]
    next_player, score_change = gm.adjudicate_answer(True)
    print('Correct flow -> next_player:', next_player, 'score_change:', score_change)
    assert next_player is None
    assert score_change == 100
    assert gm.state.current_question is None
    assert gm.state.buzz_queue == []
    assert gm.state.teams_attempted == []
    assert gm.state.teams[t1.id].score == 100
    print('Correct flow passed')


def test_wrong_no_queue_flow():
    gm, t1, t2, p1, p2 = setup_simple_game()
    gm.state.buzz_queue = [
        BuzzEntry(player_id=p1.id, player_name=p1.name, team_id=p1.team_id, team_name=gm.state.teams[p1.team_id].name,
                  timestamp=0)]
    next_player, score_change = gm.adjudicate_answer(False)
    print('Wrong/no-queue flow -> next_player:', next_player, 'score_change:', score_change)
    # Since there is another team (t2), question should remain active and buzzing open
    assert next_player is None
    assert score_change == -100
    assert gm.state.current_question is not None
    assert gm.state.question_state == QuestionState.BUZZING_OPEN
    assert p1.team_id in gm.state.teams_attempted
    assert gm.state.teams[t1.id].score == -100
    print('Wrong/no-queue flow passed')


if __name__ == '__main__':
    test_correct_flow()
    test_wrong_no_queue_flow()
    print('All smoke tests passed')
