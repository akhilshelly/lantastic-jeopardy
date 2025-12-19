"""
Tests for player creation and team assignment functionality.
"""
import pytest
from app.game_logic import GameManager
from app.models import Player


class TestPlayerCreation:
    """Tests for creating and adding players."""

    def test_add_player_to_valid_team(self, game_manager):
        """Test adding a player to an existing team."""
        team = game_manager.create_team('Alpha')
        player = game_manager.add_player('Alice', team.id, 'session_1')

        assert player is not None
        assert player.name == 'Alice'
        assert player.team_id == team.id
        assert player.session_id == 'session_1'
        assert player.connected is True

    def test_add_player_to_invalid_team(self, game_manager):
        """Test that adding player to non-existent team fails."""
        player = game_manager.add_player('Alice', 'invalid_team', 'session_1')

        assert player is None

    def test_add_player_generates_id(self, game_manager):
        """Test that player ID is generated correctly."""
        team = game_manager.create_team('Alpha')
        player = game_manager.add_player('Alice', team.id, 'session_1')

        assert player.id is not None
        assert player.id == 'player_1'

    def test_add_multiple_players_increments_id(self, game_manager):
        """Test that player IDs increment correctly."""
        team1 = game_manager.create_team('Alpha')
        team2 = game_manager.create_team('Beta')

        p1 = game_manager.add_player('Alice', team1.id, 's1')
        p2 = game_manager.add_player('Bob', team2.id, 's2')
        p3 = game_manager.add_player('Charlie', team1.id, 's3')

        assert p1.id == 'player_1'
        assert p2.id == 'player_2'
        assert p3.id == 'player_3'

    def test_add_player_added_to_state(self, game_manager):
        """Test that player is added to game state."""
        team = game_manager.create_team('Alpha')
        player = game_manager.add_player('Alice', team.id, 'session_1')

        assert player.id in game_manager.state.players
        assert game_manager.state.players[player.id] == player

    def test_add_player_added_to_team_player_list(self, game_manager):
        """Test that player is added to team's player list."""
        team = game_manager.create_team('Alpha')
        player = game_manager.add_player('Alice', team.id, 'session_1')

        assert player.id in team.player_ids
        assert player.id in game_manager.state.teams[team.id].player_ids


class TestPlayerProperties:
    """Tests for player properties and attributes."""

    def test_player_initializes_connected_true(self, game_manager):
        """Test that new players are marked as connected."""
        team = game_manager.create_team('Alpha')
        player = game_manager.add_player('Alice', team.id, 'session_1')

        assert player.connected is True

    def test_player_can_be_disconnected(self, game_manager):
        """Test that player connection status can be changed."""
        team = game_manager.create_team('Alpha')
        player = game_manager.add_player('Alice', team.id, 'session_1')

        player.connected = False
        assert player.connected is False

    def test_player_session_id_stored(self, game_manager):
        """Test that player session ID is properly stored."""
        team = game_manager.create_team('Alpha')
        session_id = 'abc123def456'
        player = game_manager.add_player('Alice', team.id, session_id)

        assert player.session_id == session_id


class TestMultiplePlayers:
    """Tests for scenarios with multiple players."""

    def test_multiple_players_same_team(self, game_manager):
        """Test adding multiple players to the same team."""
        team = game_manager.create_team('Alpha')

        p1 = game_manager.add_player('Alice', team.id, 's1')
        p2 = game_manager.add_player('Bob', team.id, 's2')

        assert len(team.player_ids) == 2
        assert p1.id in team.player_ids
        assert p2.id in team.player_ids
        assert p1.team_id == p2.team_id

    def test_multiple_players_different_teams(self, game_manager):
        """Test adding players to different teams."""
        team1 = game_manager.create_team('Alpha')
        team2 = game_manager.create_team('Beta')

        p1 = game_manager.add_player('Alice', team1.id, 's1')
        p2 = game_manager.add_player('Bob', team2.id, 's2')

        assert p1.team_id == team1.id
        assert p2.team_id == team2.id
        assert p1.team_id != p2.team_id

    def test_multiple_players_independent_connections(self, game_manager):
        """Test that multiple players have independent connection status."""
        team = game_manager.create_team('Alpha')

        p1 = game_manager.add_player('Alice', team.id, 's1')
        p2 = game_manager.add_player('Bob', team.id, 's2')

        p1.connected = False

        assert p1.connected is False
        assert p2.connected is True


class TestPlayerGameState:
    """Tests for player interaction with game state."""

    def test_add_player_increases_player_count(self, game_manager):
        """Test that player count increases with each addition."""
        team = game_manager.create_team('Alpha')

        assert len(game_manager.state.players) == 0

        game_manager.add_player('Alice', team.id, 's1')
        assert len(game_manager.state.players) == 1

        game_manager.add_player('Bob', team.id, 's2')
        assert len(game_manager.state.players) == 2

    def test_add_player_multiple_teams(self, game_manager):
        """Test adding players to multiple teams and tracking."""
        team1 = game_manager.create_team('Alpha')
        team2 = game_manager.create_team('Beta')
        team3 = game_manager.create_team('Gamma')

        p1 = game_manager.add_player('Alice', team1.id, 's1')
        p2 = game_manager.add_player('Bob', team2.id, 's2')
        p3 = game_manager.add_player('Charlie', team3.id, 's3')
        p4 = game_manager.add_player('Diana', team1.id, 's4')

        assert len(game_manager.state.players) == 4
        assert len(game_manager.state.teams[team1.id].player_ids) == 2
        assert len(game_manager.state.teams[team2.id].player_ids) == 1
        assert len(game_manager.state.teams[team3.id].player_ids) == 1


class TestPlayerNaming:
    """Tests for player naming edge cases."""

    def test_add_player_empty_name(self, game_manager):
        """Test adding player with empty name (edge case)."""
        team = game_manager.create_team('Alpha')
        player = game_manager.add_player('', team.id, 'session_1')

        # Should still create player (no validation in current code)
        assert player is not None
        assert player.name == ''

    def test_add_player_special_characters_in_name(self, game_manager):
        """Test adding player with special characters."""
        team = game_manager.create_team('Alpha')
        player = game_manager.add_player('Alice-Bob @123', team.id, 'session_1')

        assert player.name == 'Alice-Bob @123'

    def test_add_player_duplicate_names_allowed(self, game_manager):
        """Test that duplicate player names are allowed."""
        team = game_manager.create_team('Alpha')

        p1 = game_manager.add_player('Alice', team.id, 's1')
        p2 = game_manager.add_player('Alice', team.id, 's2')

        assert p1.name == p2.name
        assert p1.id != p2.id


class TestPlayerRetrievalFromState:
    """Tests for retrieving players from game state."""

    def test_retrieve_player_by_id(self, game_manager):
        """Test retrieving a player by ID from state."""
        team = game_manager.create_team('Alpha')
        added_player = game_manager.add_player('Alice', team.id, 'session_1')

        retrieved_player = game_manager.state.players[added_player.id]

        assert retrieved_player == added_player
        assert retrieved_player.name == 'Alice'

    def test_retrieve_team_players(self, game_manager):
        """Test retrieving all players from a team."""
        team = game_manager.create_team('Alpha')

        p1 = game_manager.add_player('Alice', team.id, 's1')
        p2 = game_manager.add_player('Bob', team.id, 's2')

        team_data = game_manager.state.teams[team.id]
        retrieved_players = [
            game_manager.state.players[pid] for pid in team_data.player_ids
        ]

        assert len(retrieved_players) == 2
        assert p1 in retrieved_players
        assert p2 in retrieved_players

