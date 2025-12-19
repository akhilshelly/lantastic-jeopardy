"""
Tests for team creation and management functionality.
"""
import pytest
from app.game_logic import GameManager
from app.models import Team


class TestTeamCreation:
    """Tests for creating teams."""

    def test_create_single_team(self, game_manager):
        """Test creating a single team."""
        team = game_manager.create_team('Alpha')

        assert team is not None
        assert team.name == 'Alpha'
        assert team.id == 'team_1'
        assert team.score == 0
        assert team.player_ids == []
        assert team.color == '#FFD700'  # Gold - first color

    def test_create_team_added_to_state(self, game_manager):
        """Test that created team is added to game state."""
        team = game_manager.create_team('Alpha')

        assert team.id in game_manager.state.teams
        assert game_manager.state.teams[team.id] == team

    def test_create_multiple_teams_increments_id(self, game_manager):
        """Test that team IDs increment correctly."""
        team1 = game_manager.create_team('Alpha')
        team2 = game_manager.create_team('Beta')
        team3 = game_manager.create_team('Gamma')

        assert team1.id == 'team_1'
        assert team2.id == 'team_2'
        assert team3.id == 'team_3'

    def test_create_multiple_teams_cycles_colors(self, game_manager):
        """Test that team colors cycle through the palette."""
        expected_colors = ["#FFD700", "#4169E1", "#DC143C", "#32CD32", "#FF8C00", "#9370DB"]

        teams = []
        for i in range(len(expected_colors)):
            team = game_manager.create_team(f'Team{i}')
            teams.append(team)

        for i, team in enumerate(teams):
            assert team.color == expected_colors[i]

    def test_create_teams_wraps_color_palette(self, game_manager):
        """Test that color palette wraps around after all colors used."""
        expected_colors = ["#FFD700", "#4169E1", "#DC143C", "#32CD32", "#FF8C00", "#9370DB"]

        # Create more teams than colors
        for i in range(10):
            team = game_manager.create_team(f'Team{i}')
            expected_color = expected_colors[i % len(expected_colors)]
            assert team.color == expected_color

    def test_create_team_empty_name(self, game_manager):
        """Test creating a team with empty name (edge case)."""
        team = game_manager.create_team('')

        # Should still create the team (no validation in current code)
        assert team is not None
        assert team.name == ''

    def test_create_team_special_characters_in_name(self, game_manager):
        """Test creating team with special characters."""
        team = game_manager.create_team('Team #1 & Friends!')

        assert team.name == 'Team #1 & Friends!'


class TestTeamProperties:
    """Tests for team properties and attributes."""

    def test_team_initializes_with_zero_score(self, game_manager):
        """Test that teams start with score of 0."""
        team = game_manager.create_team('Alpha')

        assert team.score == 0

    def test_team_initializes_with_empty_players(self, game_manager):
        """Test that teams start with empty player list."""
        team = game_manager.create_team('Alpha')

        assert len(team.player_ids) == 0
        assert team.player_ids == []

    def test_team_score_can_be_modified(self, game_manager):
        """Test that team score can be modified."""
        team = game_manager.create_team('Alpha')

        team.score = 100
        assert team.score == 100

        team.score = -50
        assert team.score == -50

    def test_team_players_can_be_added_to_list(self, game_manager):
        """Test that player IDs can be added to team."""
        team = game_manager.create_team('Alpha')

        team.player_ids.append('player_1')
        team.player_ids.append('player_2')

        assert len(team.player_ids) == 2
        assert 'player_1' in team.player_ids
        assert 'player_2' in team.player_ids


class TestMultipleTeams:
    """Tests for scenarios with multiple teams."""

    def test_multiple_teams_independent_scores(self, game_manager):
        """Test that multiple teams have independent scores."""
        team1 = game_manager.create_team('Alpha')
        team2 = game_manager.create_team('Beta')

        team1.score = 100
        team2.score = 200

        assert game_manager.state.teams[team1.id].score == 100
        assert game_manager.state.teams[team2.id].score == 200

    def test_multiple_teams_all_in_state(self, game_manager):
        """Test that all created teams are in game state."""
        teams = [
            game_manager.create_team('Alpha'),
            game_manager.create_team('Beta'),
            game_manager.create_team('Gamma')
        ]

        assert len(game_manager.state.teams) == 3
        for team in teams:
            assert team.id in game_manager.state.teams

    def test_teams_are_distinct_objects(self, game_manager):
        """Test that each team is a distinct object."""
        team1 = game_manager.create_team('Alpha')
        team2 = game_manager.create_team('Beta')

        assert team1 is not team2
        assert team1.id != team2.id
        assert team1.name != team2.name


class TestTeamIntegration:
    """Integration tests for team functionality."""

    def test_create_team_then_add_player(self, game_manager):
        """Test workflow: create team, then add player."""
        team = game_manager.create_team('Alpha')
        player = game_manager.add_player('Alice', team.id, 'session_1')

        assert player is not None
        assert player.team_id == team.id
        assert player.id in team.player_ids

    def test_team_persists_across_operations(self, game_manager):
        """Test that team state persists across multiple operations."""
        team = game_manager.create_team('Alpha')
        initial_id = team.id

        # Modify team
        team.score = 100
        game_manager.add_player('Alice', team.id, 's1')

        # Retrieve and verify
        retrieved_team = game_manager.state.teams[initial_id]
        assert retrieved_team.score == 100
        assert len(retrieved_team.player_ids) == 1

