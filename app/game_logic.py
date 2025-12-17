import csv
import time
from typing import List, Optional, Dict, Tuple
from app.models import GameState, Team, Player, Question, BuzzEntry, GamePhase, QuestionState
from config import Config

class GameManager:
    def __init__(self):
        self.state = GameState()
        self._team_colors = ["#FFD700", "#4169E1", "#DC143C", "#32CD32", "#FF8C00", "#9370DB"]
        self._next_color_idx = 0
    
    def load_questions(self) -> bool:
        """Load questions from CSV file."""
        try:
            with open(Config.QUESTIONS_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                self.state.questions = []
                for row in reader:
                    q = Question(
                        round=int(row['Round']),
                        category=row['Category'],
                        value=int(row['Value']),
                        question=row['Question'],
                        answer=row['Answer']
                    )
                    self.state.questions.append(q)
            return len(self.state.questions) > 0
        except Exception as e:
            print(f"Error loading questions: {e}")
            return False
    
    def create_team(self, name: str) -> Team:
        """Create a new team."""
        team_id = f"team_{len(self.state.teams) + 1}"
        color = self._team_colors[self._next_color_idx % len(self._team_colors)]
        self._next_color_idx += 1
        
        team = Team(id=team_id, name=name, color=color)
        self.state.teams[team_id] = team
        return team
    
    def add_player(self, name: str, team_id: str, session_id: str) -> Optional[Player]:
        """Add a player to a team."""
        if team_id not in self.state.teams:
            return None
        
        player_id = f"player_{len(self.state.players) + 1}"
        player = Player(id=player_id, name=name, team_id=team_id, session_id=session_id)
        
        self.state.players[player_id] = player
        self.state.teams[team_id].player_ids.append(player_id)
        
        return player
    
    def set_trebek(self, session_id: str):
        """Set the Trebek session."""
        self.state.trebek_session_id = session_id
    
    def start_round(self, round_num: int):
        """Start a game round."""
        if round_num == 1:
            self.state.phase = GamePhase.ROUND_1
        elif round_num == 2:
            self.state.phase = GamePhase.ROUND_2
        self.state.question_state = QuestionState.BOARD_ACTIVE
    
    def get_board_state(self, round_num: int) -> Dict:
        """Get the current board state for a round."""
        round_questions = [q for q in self.state.questions if q.round == round_num]
        
        # Organize by category
        categories = {}
        for q in round_questions:
            if q.category not in categories:
                categories[q.category] = []
            categories[q.category].append({
                'value': q.value,
                'used': q.used,
                'question': q.question,
                'answer': q.answer
            })
        
        # Sort values within each category
        for cat in categories:
            categories[cat].sort(key=lambda x: x['value'])
        
        return categories
    
    def select_question(self, category: str, value: int) -> Optional[Question]:
        """Select a question from the board."""
        current_round = 1 if self.state.phase == GamePhase.ROUND_1 else 2
        
        for q in self.state.questions:
            if (q.round == current_round and 
                q.category == category and 
                q.value == value and 
                not q.used):
                q.used = True
                self.state.current_question = q
                self.state.question_state = QuestionState.QUESTION_REVEALED
                self.state.buzz_queue = []
                self.state.teams_attempted = []
                self.state.buzz_timer_active = True
                return q
        return None
    
    def enable_buzzing(self):
        """Enable buzzing after timer expires."""
        self.state.question_state = QuestionState.BUZZING_OPEN
        self.state.buzz_timer_active = False
    
    def buzz_in(self, player_id: str) -> bool:
        """Player attempts to buzz in."""
        if self.state.question_state != QuestionState.BUZZING_OPEN:
            return False
        
        player = self.state.players.get(player_id)
        if not player:
            return False
        
        # Check if this team already attempted
        if player.team_id in self.state.teams_attempted:
            return False
        
        # Check if player already in queue
        if any(entry.player_id == player_id for entry in self.state.buzz_queue):
            return False
        
        team = self.state.teams[player.team_id]
        entry = BuzzEntry(
            player_id=player_id,
            player_name=player.name,
            team_id=player.team_id,
            team_name=team.name,
            timestamp=time.time()
        )
        
        self.state.buzz_queue.append(entry)
        return True
    
    def adjudicate_answer(self, correct: bool) -> Tuple[Optional[str], int]:
        """Adjudicate the current answer. Returns (next_player_id, score_change)."""
        if not self.state.current_question or not self.state.buzz_queue:
            return None, 0
        
        current_buzzer = self.state.buzz_queue[0]
        team = self.state.teams[current_buzzer.team_id]
        value = self.state.current_question.value
        
        if correct:
            # Correct answer - award points and end question
            team.score += value
            self.state.current_question = None
            self.state.buzz_queue = []
            self.state.teams_attempted = []
            self.state.question_state = QuestionState.BOARD_ACTIVE
            return None, value
        else:
            # Wrong answer - deduct points and move to next buzzer
            team.score -= value
            self.state.teams_attempted.append(current_buzzer.team_id)
            self.state.buzz_queue.pop(0)
            
            if self.state.buzz_queue:
                # More people in queue
                next_player_id = self.state.buzz_queue[0].player_id
                return next_player_id, -value
            else:
                # No one else buzzed, return to board
                self.state.current_question = None
                self.state.teams_attempted = []
                self.state.question_state = QuestionState.BOARD_ACTIVE
                return None, -value
    
    def get_game_summary(self) -> Dict:
        """Get summary of game state for clients."""
        teams_data = []
        for team in self.state.teams.values():
            players_data = [
                {
                    'id': p.id,
                    'name': p.name,
                    'connected': p.connected
                }
                for pid in team.player_ids
                if (p := self.state.players.get(pid))
            ]
            teams_data.append({
                'id': team.id,
                'name': team.name,
                'score': team.score,
                'color': team.color,
                'players': players_data
            })
        
        current_question_data = None
        if self.state.current_question:
            current_question_data = {
                'category': self.state.current_question.category,
                'value': self.state.current_question.value,
                'question': self.state.current_question.question,
                'answer': self.state.current_question.answer
            }
        
        buzz_queue_data = [
            {
                'player_id': entry.player_id,
                'player_name': entry.player_name,
                'team_name': entry.team_name,
                'team_id': entry.team_id
            }
            for entry in self.state.buzz_queue
        ]

        current_round = 1 if self.state.phase == GamePhase.ROUND_1 else 2 if self.state.phase == GamePhase.ROUND_2 else 0
        round_1_complete = self.is_round_complete(1) if current_round >= 1 else False
        round_2_complete = self.is_round_complete(2) if current_round >= 2 else False

        return {
            'phase': self.state.phase.value,
            'question_state': self.state.question_state.value,
            'teams': teams_data,
            'current_question': current_question_data,
            'buzz_queue': buzz_queue_data,
            'buzz_timer_active': self.state.buzz_timer_active,
            'round_1_complete': round_1_complete,
            'round_2_complete': round_2_complete
        }

    def is_round_complete(self, round_num: int) -> bool:
        """Check if all questions in a round have been used."""
        round_questions = [q for q in self.state.questions if q.round == round_num]
        return all(q.used for q in round_questions)

# Global game manager instance
game_manager = GameManager()
