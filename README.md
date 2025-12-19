# Jeopardy Web App

A fully-featured Jeopardy game webapp for local party hosting.

## Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone/navigate to the project directory:**
```bash
cd jeopardy-webapp
```

2. **(Optional but Recommended) Create and activate a virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Create your questions file at `data/questions.csv` with format:**
```csv
Round,Category,Value,Question,Answer
1,Geography,100,This is the capital of France,What is Paris?
1,Geography,200,This is the largest country by area,What is Russia?
```

## Running the Game

1. **Activate virtual environment** (if you created one):
```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. **Start the server:**
```bash
python app.py
```

3. The server will output connection URLs:
```
============================================================
🎮 JEOPARDY GAME SERVER
============================================================
🌐 Host Interface: 0.0.0.0
🔌 Port: 9001
📱 Trebek URL: http://<local-ip>:9001/
📱 Players Join: http://<local-ip>:9001/join
📺 Display: http://<local-ip>:9001/display
============================================================
```

### Three Interfaces

The app has three separate interfaces:

1. **Trebek (Host Control)** - `http://<local-ip>:9001/`
   - Controls the game (start round, reveal questions, adjudicate answers)
   - Creates teams and manages the lobby
   - Displays QR code for player joining
   - For the person running/hosting the game

2. **Jennings (Player Interface)** - `http://<local-ip>:9001/join`
   - Players use this to join teams and buzz in during gameplay
   - Typically accessed via QR code or direct URL from another device
   - Responsive design works on mobile phones and tablets

3. **Display (TV/Projector)** - `http://<local-ip>:9001/display`
   - Shows the game board with all categories and values
   - Displays current questions and answers
   - Should be projected or displayed on a large screen for all to see
   - No interaction needed here; it updates automatically based on game state

### Game Setup Steps

4. **Open the display interface** on your TV/projector: `http://<local-ip>:9001/display`

5. **Open the Trebek interface** on your host computer: `http://<local-ip>:9001/`

6. **Players join** by scanning the QR code displayed in Trebek or navigating to the join URL

7. **Trebek creates teams** in the lobby

8. **Players join their teams** via the Jennings interface on their devices

9. **Trebek starts Round 1!**

## Game Flow

1. **Lobby**: Trebek creates teams, players join
2. **Round 1**: $100-$500 questions
3. **Round 2**: $200-$1000 questions
4. **Scoring**: Team-based, negative points for wrong answers

## Testing

### Test Suite Overview

This project includes a **comprehensive Phase 1 test suite** with **81 passing tests** covering core game logic:

- ✅ **Team Management** (16 tests) - Team creation, ID generation, color assignment
- ✅ **Player Management** (14 tests) - Player creation, team assignment, connection tracking
- ✅ **Question Loading** (35 tests) - CSV parsing, board state, question organization
- ✅ **Adjudication** (24 tests) - Answer scoring, queue management, edge cases
- ✅ **Overall Coverage**: ~80% of core game logic

### Running Tests

Tests use pytest. Make sure your virtual environment is activated, then:

```bash
# Run all tests
python -m pytest tests/ -v

# Run all tests (without verbose)
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_team_management.py -v
python -m pytest tests/test_player_management.py -v
python -m pytest tests/test_question_loading.py -v
python -m pytest tests/test_adjudication_scenarios.py -v

# Run specific test class
python -m pytest tests/test_team_management.py::TestTeamCreation -v

# Run specific test
python -m pytest tests/test_team_management.py::TestTeamCreation::test_create_single_team -v

# Run with coverage report
python -m pytest tests/ --cov=app --cov-report=html
```

**Important**: Use `python -m pytest` rather than just `pytest` to ensure proper module imports.

### Test Files

- **conftest.py** - Shared fixtures and utilities (6 reusable fixtures)
- **test_team_management.py** - Team creation, color assignment, multiple teams
- **test_player_management.py** - Player creation, team assignment, connection management
- **test_question_loading.py** - CSV loading, board state, question organization
- **test_adjudication_scenarios.py** - Answer scoring, buzz queue, edge cases
- **test_game_logic.py** - Original smoke tests (preserved, still passing)

## Architecture

- **Backend**: Flask web framework with Flask-SocketIO for real-time WebSocket communication
- **Frontend**: Three HTML/CSS/JavaScript interfaces:
  - **Trebek**: Host control interface for managing the game
  - **Jennings**: Player interface for joining teams and buzzing in
  - **Display**: TV/projector interface for showing the game board to all players
- **Game Logic**: `app/game_logic.py` contains core GameManager and game state management
- **Real-time Communication**: Events handled in `app/events.py` for player actions and game updates
- **Port**: Configured to 9001 (see `config.py`)

## Environment Variables

Optional environment variables (from `config.py`):

```bash
# Secret key for session management (change in production)
export SECRET_KEY="your-secret-key"

# Currently not configurable but hardcoded:
# - DEBUG=True (development mode)
# - BUZZ_DELAY_SECONDS=4 (delay before players can buzz)
```

## Features

- Real-time WebSocket communication (Flask-SocketIO)
- QR code generation for easy mobile joining
- 4-second buzz delay for fair play
- Buzz queue system to track player responses
- Team-based scoring with negative points for incorrect answers
- Classic Jeopardy styling
- Responsive design for desktop hosts and mobile players

## Network Access

The server binds to `0.0.0.0` so any device on your local network can connect.

1. Find your computer's local IP address:
   - **Linux/Mac**: Run `ifconfig` and look for inet address on your WiFi interface
   - **Windows**: Run `ipconfig` and look for IPv4 Address

2. Share with players: `http://<your-local-ip>:9001/join`

3. The QR code on the Trebek interface also encodes this URL for easy scanning

## Troubleshooting

### Tests Won't Run

**Error**: `ModuleNotFoundError: No module named 'app'`
- **Solution**: Always use `python -m pytest` instead of just `pytest`
- **Why**: The `-m` flag ensures the current directory is in the Python path

**Tests fail to import fixtures**:
- Make sure `tests/conftest.py` exists
- Verify you're running tests from the project root directory
- Try: `python -m pytest tests/ --fixtures` to see available fixtures

**Some tests fail but others pass**:
- Check if temporary files are being created (CSV files in temp_path)
- Ensure no port conflicts if running integration tests
- See individual test file docstrings for specific requirements

### Test Results Troubleshooting

**Coverage report not generated**:
```bash
# Install coverage if missing
pip install pytest-cov

# Generate HTML coverage report
python -m pytest tests/ --cov=app --cov-report=html
open htmlcov/index.html  # View in browser
```

**Tests run slowly**:
- Check system resources (CPU/memory)
- File I/O operations may be slower on network drives
- Consider running subset: `python -m pytest tests/test_team_management.py -v` to test individually

### Game Runtime Issues

### Can't Connect from Another Device
- Check that your firewall allows port 9001
- Verify you're using the correct local IP address (not `localhost`)
- Ensure both devices are on the same network
- Try `python app.py` and look at the output URLs

### Port 9001 Already in Use
- Find and kill the process: `lsof -i :9001` (Mac/Linux) or `netstat -ano | findstr :9001` (Windows)
- Or change the port in `config.py` and restart (probably better)

### WebSocket Connection Fails
- Check browser console for errors (F12 → Console)
- Ensure you're allowing WebSocket connections
- Verify Flask-SocketIO is installed: `pip list | grep Flask-SocketIO`
- Check app logs for connection errors

## Code Quality & Confidence

### Comprehensive Logging

This application includes detailed logging throughout to help with debugging and understanding game flow:

- **app/__init__.py** - Logs app initialization, config loading, and startup
- **app/routes.py** - Logs route access, QR code generation, and IP detection
- **app/game_logic.py** - Logs all game state changes, question loading, scoring
- **app/events.py** - Logs WebSocket connections, player joins, and game events
- **app/logging_config.py** - Centralized logging configuration

All logs are output to console by default with timestamps and log levels.

### Test-Driven Development

The codebase is developed with test-driven development principles:

- ✅ **81 passing tests** validate core functionality
- ✅ **~80% code coverage** of game logic
- ✅ **Tests document expected behavior** (see test files for usage examples)
- ✅ **Regression protection** - tests catch breaking changes automatically
- ✅ **Confidence in refactoring** - tests ensure changes don't break functionality

### Development Workflow

When making changes:
1. Write or update tests first
2. Run tests to verify they fail (test-driven approach)
3. Implement the feature/fix
4. Run tests to verify they pass: `python -m pytest tests/ -v`
5. Check coverage: `python -m pytest tests/ --cov=app`
6. Commit with confidence knowing tests validate behavior

## Backlog

- Final Jeopardy with wagering
- Redemption mode (multiple teammates per question)
- Audio/visual cues
- Daily Doubles

## AI Usage
Some portions of this project were assisted by AI tools for code generation and suggestions. 
All code was reviewed and tested to ensure quality and correctness. 
While efforts have been made to ensure accuracy, users should verify functionality independently.
