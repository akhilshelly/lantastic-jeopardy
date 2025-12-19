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

### Running Tests

Tests use pytest. Make sure your virtual environment is activated, then:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_game_logic.py

# Run with verbose output
python -m pytest tests/ -v

# Run smoke tests
python -m pytest tests/run_smoke.py
```

Note: Use `python -m pytest` rather than just `pytest` to ensure proper module imports.

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
- **Error**: `ModuleNotFoundError: No module named 'app'`
- **Solution**: Always use `python -m pytest` instead of just `pytest`
- **Why**: The `-m` flag ensures the current directory is in the Python path

### Can't Connect from Another Device
- Check that your firewall allows port 9001
- Verify you're using the correct local IP address (not `localhost`)
- Ensure both devices are on the same network
- Try `python app.py` and look at the output URLs

### Port 9001 Already in Use
- Find and kill the process: `lsof -i :9001` (Mac/Linux) or `netstat -ano | findstr :9001` (Windows)
- Or change the port in `config.py` and restart

### WebSocket Connection Fails
- Check browser console for errors
- Ensure you're allowing WebSocket connections
- Verify Flask-SocketIO is installed: `pip install Flask-SocketIO`

## Backlog

- Final Jeopardy with wagering
- Redemption mode (multiple teammates per question)
- Audio/visual cues
- Daily Doubles

