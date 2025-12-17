from flask import Blueprint, render_template_string, request, jsonify
import qrcode
import io
import base64
from app.game_logic import game_manager

bp = Blueprint('main', __name__)

def get_local_ip():
    """Get local IP address for QR code."""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

@bp.route('/')
def index():
    """Trebek's main interface."""
    return render_template_string(TREBEK_TEMPLATE)

@bp.route('/join')
def join():
    """Jennings join and game interface."""
    return render_template_string(JENNINGS_TEMPLATE)

@bp.route('/qr')
def qr_code():
    """Generate QR code for join URL."""
    local_ip = get_local_ip()
    port = request.host.split(':')[-1]
    url = f"http://{local_ip}:{port}/join"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    img_base64 = base64.b64encode(buf.getvalue()).decode()
    return jsonify({
        'qr_code': f"data:image/png;base64,{img_base64}",
        'url': url
    })


TREBEK_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Jeopardy - Trebek Control</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            background: #060CE9;
            color: white;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        h1 {
            font-size: 3em;
            text-align: center;
            margin-bottom: 30px;
            text-shadow: 3px 3px 6px rgba(0,0,0,0.5);
            font-weight: bold;
            letter-spacing: 3px;
        }
        
        .lobby-section, .game-section {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255,215,0,0.3);
        }
        
        .section-title {
            font-size: 1.8em;
            margin-bottom: 20px;
            color: #FFD700;
            border-bottom: 3px solid #FFD700;
            padding-bottom: 10px;
        }
        
        .team-input {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        input[type="text"] {
            flex: 1;
            padding: 15px;
            font-size: 1.1em;
            border: none;
            border-radius: 5px;
            background: white;
            color: #060CE9;
        }
        
        button {
            padding: 15px 30px;
            font-size: 1.1em;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .btn-primary {
            background: #FFD700;
            color: #060CE9;
        }
        
        .btn-primary:hover {
            background: #FFA500;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255,215,0,0.4);
        }
        
        .btn-success {
            background: #32CD32;
            color: white;
        }
        
        .btn-success:hover {
            background: #228B22;
        }
        
        .btn-danger {
            background: #DC143C;
            color: white;
        }
        
        .btn-danger:hover {
            background: #8B0000;
        }
        
        .teams-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .team-card {
            background: rgba(255,255,255,0.15);
            padding: 20px;
            border-radius: 8px;
            border-left: 5px solid #FFD700;
        }
        
        .team-name {
            font-size: 1.4em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .team-score {
            font-size: 2em;
            color: #FFD700;
            margin-bottom: 10px;
        }
        
        .player-list {
            font-size: 0.95em;
            opacity: 0.9;
        }
        
        .board {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 10px;
            margin-top: 20px;
        }
        
        .category-header {
            background: #000;
            padding: 20px;
            text-align: center;
            font-size: 1.2em;
            font-weight: bold;
            color: #FFD700;
            border-radius: 5px;
            text-transform: uppercase;
        }
        
        .question-cell {
            background: #060CE9;
            padding: 30px;
            text-align: center;
            font-size: 2em;
            font-weight: bold;
            color: #FFD700;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
            border: 2px solid #FFD700;
        }
        
        .question-cell:hover {
            background: #0A0FFF;
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(255,215,0,0.5);
        }
        
        .question-cell.used {
            background: #333;
            color: #666;
            cursor: not-allowed;
            border-color: #666;
        }
        
        .question-cell.used:hover {
            transform: none;
            box-shadow: none;
        }
        
        .question-display {
            background: #000;
            padding: 40px;
            border-radius: 10px;
            margin: 20px 0;
            border: 3px solid #FFD700;
        }
        
        .question-text {
            font-size: 1.8em;
            text-align: center;
            margin-bottom: 20px;
            color: white;
        }
        
        .answer-text {
            font-size: 1.4em;
            text-align: center;
            color: #FFD700;
            font-style: italic;
        }
        
        .buzz-queue {
            background: rgba(0,0,0,0.5);
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }
        
        .buzz-entry {
            background: rgba(255,255,255,0.1);
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-left: 4px solid #FFD700;
        }
        
        .buzz-entry.active {
            background: rgba(255,215,0,0.2);
            border-left-color: #32CD32;
        }
        
        .buzz-actions {
            display: flex;
            gap: 10px;
        }
        
        .qr-section {
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 10px;
            margin-top: 20px;
        }
        
        .qr-code {
            max-width: 300px;
            margin: 20px auto;
        }
        
        .join-url {
            color: #060CE9;
            font-size: 1.2em;
            font-weight: bold;
            margin-top: 15px;
        }
        
        .hidden {
            display: none;
        }
        
        .timer-display {
            font-size: 3em;
            text-align: center;
            color: #FFD700;
            margin: 20px 0;
            font-weight: bold;
            animation: pulse 1s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.6; }
        }
        
        .round-controls {
            display: flex;
            gap: 15px;
            justify-content: center;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 JEOPARDY! HOST CONTROL</h1>
        
        <div id="lobbyView" class="lobby-section">
            <h2 class="section-title">Pre-Game Lobby</h2>
            
            <div class="team-input">
                <input type="text" id="teamNameInput" placeholder="Enter team name...">
                <button class="btn-primary" onclick="createTeam()">Create Team</button>
            </div>
            
            <div class="teams-list" id="teamsList"></div>
            
            <div class="qr-section">
                <h3>Players Join Here:</h3>
                <img id="qrCode" class="qr-code" alt="QR Code">
                <div id="joinUrl" class="join-url"></div>
            </div>
            
            <div class="round-controls">
                <button class="btn-success" onclick="startRound(1)">Start Round 1</button>
            </div>
        </div>
        
        <div id="gameView" class="game-section hidden">
            <h2 class="section-title">Game Control - <span id="currentRound">Round 1</span></h2>
            
            <div class="teams-list" id="gameTeamsList"></div>
            
            <div id="timerDisplay" class="timer-display hidden"></div>
            
            <div id="questionDisplay" class="question-display hidden">
                <div class="question-text" id="questionText"></div>
                <div class="answer-text" id="answerText"></div>
            </div>
            
            <div id="buzzQueue" class="buzz-queue hidden">
                <h3>Buzz Queue:</h3>
                <div id="buzzList"></div>
            </div>
            
            <div id="board" class="board"></div>
            
            <div class="round-controls">
                <button id="round2Button" class="btn-primary" onclick="startRound(2)" disabled>Start Round 2</button>
            </div>
        </div>
    </div>
    
    <script>
        const socket = io();
        let gameState = null;
        let currentBoard = null;
        let myRole = null;
        let timerInterval = null;
        
        socket.on('connect', () => {
            console.log('Connected to server');
            socket.emit('register_trebek');
            loadQRCode();
        });
        
        socket.on('registration_success', (data) => {
            myRole = data.role;
            console.log('Registered as:', myRole);
        });
        
        socket.on('game_update', (data) => {
            gameState = data;
            updateUI();
        });
        
        socket.on('board_update', (data) => {
            currentBoard = data;
            renderBoard();
        });
        
        function loadQRCode() {
            fetch('/qr')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('qrCode').src = data.qr_code;
                    document.getElementById('joinUrl').textContent = data.url;
                });
        }
        
        function createTeam() {
            const name = document.getElementById('teamNameInput').value.trim();
            if (name) {
                socket.emit('create_team', { name });
                document.getElementById('teamNameInput').value = '';
            }
        }
        
        function startRound(round) {
            socket.emit('start_round', { round });
            document.getElementById('lobbyView').classList.add('hidden');
            document.getElementById('gameView').classList.remove('hidden');
            document.getElementById('currentRound').textContent = `Round ${round}`;
        }
        
        function selectQuestion(category, value) {
            socket.emit('select_question', { category, value });
        }
        
        function adjudicate(correct) {
            socket.emit('adjudicate', { correct });
        }
        
        function updateUI() {
            if (!gameState) return;
            
            // Update teams in lobby
            const teamsList = document.getElementById('teamsList');
            teamsList.innerHTML = '';
            gameState.teams.forEach(team => {
                const card = document.createElement('div');
                card.className = 'team-card';
                card.style.borderLeftColor = team.color;
                card.innerHTML = `
                    <div class="team-name">${team.name}</div>
                    <div class="player-list">
                        ${team.players.map(p => `${p.name}${p.connected ? '' : ' (disconnected)'}`).join('<br>')}
                    </div>
                `;
                teamsList.appendChild(card);
            });
            
            // Update teams in game
            const gameTeamsList = document.getElementById('gameTeamsList');
            gameTeamsList.innerHTML = '';
            gameState.teams.forEach(team => {
                const card = document.createElement('div');
                card.className = 'team-card';
                card.style.borderLeftColor = team.color;
                card.innerHTML = `
                    <div class="team-name">${team.name}</div>
                    <div class="team-score">${team.score}</div>
                    <div class="player-list">
                        ${team.players.map(p => `${p.name}`).join(', ')}
                    </div>
                `;
                gameTeamsList.appendChild(card);
            });
            
            // Handle question display
            const questionDisplay = document.getElementById('questionDisplay');
            const timerDisplay = document.getElementById('timerDisplay');
            const buzzQueue = document.getElementById('buzzQueue');
            
            if (gameState.current_question) {
                questionDisplay.classList.remove('hidden');
                document.getElementById('questionText').textContent = gameState.current_question.question;
                document.getElementById('answerText').textContent = gameState.current_question.answer;
                
                if (gameState.buzz_timer_active) {
                    startTimer(4);
                    timerDisplay.classList.remove('hidden');
                    buzzQueue.classList.add('hidden');
                } else {
                    stopTimer();
                    timerDisplay.classList.add('hidden');
                    
                    if (gameState.buzz_queue.length > 0) {
                        buzzQueue.classList.remove('hidden');
                        renderBuzzQueue();
                    } else {
                        buzzQueue.classList.add('hidden');
                    }
                }
            } else {
                questionDisplay.classList.add('hidden');
                timerDisplay.classList.add('hidden');
                buzzQueue.classList.add('hidden');
                stopTimer();
            }
            
            // Update round 2 button state
            const round2Button = document.getElementById('round2Button');
            if (round2Button) {
                if (gameState.phase === 'round_1') {
                    // Enable Round 2 button only if Round 1 is complete
                    round2Button.disabled = !gameState.round_1_complete;
                    round2Button.style.display = 'block';
                } else if (gameState.phase === 'round_2') {
                    // Hide button once in Round 2
                    round2Button.style.display = 'none';
                }
            }
        }
        
        function renderBoard() {
            if (!currentBoard) return;
            
            const board = document.getElementById('board');
            board.innerHTML = '';
            
            const categories = Object.keys(currentBoard.board);
            
            // Determine expected values based on round
            const round = currentBoard.round;
            const expectedValues = round === 1 
                ? [100, 200, 300, 400, 500] 
                : [200, 400, 600, 800, 1000];
            
            // Set grid to have correct number of rows
            board.style.gridTemplateRows = `auto repeat(${expectedValues.length}, 1fr)`;
            
            // Add category headers with explicit grid positioning
            categories.forEach((cat, colIndex) => {
                const header = document.createElement('div');
                header.className = 'category-header';
                header.textContent = cat;
                header.style.gridColumn = colIndex + 1;
                header.style.gridRow = 1;
                board.appendChild(header);
            });
            
            // Add question cells with explicit grid positioning
            categories.forEach((cat, colIndex) => {
                const questions = currentBoard.board[cat];
                
                expectedValues.forEach((expectedValue, rowIndex) => {
                    const cell = document.createElement('div');
                    cell.style.gridColumn = colIndex + 1;
                    cell.style.gridRow = rowIndex + 2; // +2 because row 1 is headers
                    
                    // Find the question with this value
                    const q = questions.find(question => question.value === expectedValue);
                    
                    if (q) {
                        cell.className = 'question-cell' + (q.used ? ' used' : '');
                        cell.textContent = '$' + q.value;
                        if (!q.used) {
                            cell.onclick = () => selectQuestion(cat, q.value);
                        }
                    } else {
                        // No question for this value - show empty/missing cell
                        cell.className = 'question-cell used';
                        cell.textContent = '—';
                        cell.style.opacity = '0.3';
                    }
                    
                    board.appendChild(cell);
                });
            });
        }
        
        function renderBuzzQueue() {
            const buzzList = document.getElementById('buzzList');
            buzzList.innerHTML = '';
            
            gameState.buzz_queue.forEach((entry, index) => {
                const div = document.createElement('div');
                div.className = 'buzz-entry' + (index === 0 ? ' active' : '');
                div.innerHTML = `
                    <div>
                        <strong>${entry.player_name}</strong> (${entry.team_name})
                    </div>
                    ${index === 0 ? `
                        <div class="buzz-actions">
                            <button class="btn-success" onclick="adjudicate(true)">✓ Correct</button>
                            <button class="btn-danger" onclick="adjudicate(false)">✗ Wrong</button>
                        </div>
                    ` : ''}
                `;
                buzzList.appendChild(div);
            });
        }
        
        function startTimer(seconds) {
            stopTimer();
            let remaining = seconds;
            const display = document.getElementById('timerDisplay');
            display.textContent = remaining;
            
            timerInterval = setInterval(() => {
                remaining--;
                if (remaining >= 0) {
                    display.textContent = remaining;
                } else {
                    stopTimer();
                }
            }, 1000);
        }
        
        function stopTimer() {
            if (timerInterval) {
                clearInterval(timerInterval);
                timerInterval = null;
            }
        }
    </script>
</body>
</html>
"""

JENNINGS_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Jeopardy - Player</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            background: #060CE9;
            color: white;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            width: 100%;
            max-width: 500px;
        }
        
        h1 {
            font-size: 2.5em;
            text-align: center;
            margin-bottom: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            color: #FFD700;
        }
        
        .join-section, .game-section {
            background: rgba(255,255,255,0.1);
            padding: 30px;
            border-radius: 10px;
            backdrop-filter: blur(10px);
            border: 2px solid rgba(255,215,0,0.3);
        }
        
        input[type="text"] {
            width: 100%;
            padding: 15px;
            font-size: 1.1em;
            border: none;
            border-radius: 5px;
            margin-bottom: 15px;
            background: white;
            color: #060CE9;
        }
        
        select {
            width: 100%;
            padding: 15px;
            font-size: 1.1em;
            border: none;
            border-radius: 5px;
            margin-bottom: 20px;
            background: white;
            color: #060CE9;
        }
        
        button {
            width: 100%;
            padding: 20px;
            font-size: 1.3em;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .btn-join {
            background: #FFD700;
            color: #060CE9;
        }
        
        .btn-join:hover {
            background: #FFA500;
            transform: translateY(-2px);
        }
        
        .buzz-button {
            background: #DC143C;
            color: white;
            font-size: 2em;
            padding: 60px;
            border-radius: 50%;
            width: 250px;
            height: 250px;
            margin: 30px auto;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 10px 30px rgba(220,20,60,0.5);
        }
        
        .buzz-button:hover:not(:disabled) {
            background: #8B0000;
            transform: scale(1.1);
            box-shadow: 0 15px 40px rgba(220,20,60,0.7);
        }
        
        .buzz-button:active:not(:disabled) {
            transform: scale(0.95);
        }
        
        .buzz-button:disabled {
            background: #666;
            cursor: not-allowed;
            opacity: 0.5;
        }
        
        .team-info {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .team-name {
            font-size: 1.8em;
            color: #FFD700;
            margin-bottom: 10px;
        }
        
        .team-score {
            font-size: 3em;
            font-weight: bold;
        }
        
        .status-message {
            text-align: center;
            font-size: 1.2em;
            padding: 20px;
            background: rgba(0,0,0,0.3);
            border-radius: 5px;
            margin-top: 20px;
        }
        
        .question-info {
            background: rgba(0,0,0,0.5);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .category {
            font-size: 1.3em;
            color: #FFD700;
            margin-bottom: 5px;
        }
        
        .value {
            font-size: 1.8em;
            font-weight: bold;
        }
        
        .hidden {
            display: none;
        }
        
        .buzz-position {
            font-size: 1.5em;
            color: #32CD32;
            margin-top: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>JEOPARDY!</h1>
        
        <div id="joinView" class="join-section">
            <input type="text" id="playerName" placeholder="Enter your name...">
            <select id="teamSelect">
                <option value="">Select your team...</option>
            </select>
            <button class="btn-join" onclick="joinGame()">Join Game</button>
        </div>
        
        <div id="gameView" class="game-section hidden">
            <div class="team-info">
                <div class="team-name" id="teamName"></div>
                <div class="team-score" id="teamScore">$0</div>
            </div>
            
            <div id="questionInfo" class="question-info hidden">
                <div class="category" id="questionCategory"></div>
                <div class="value" id="questionValue"></div>
            </div>
            
            <button id="buzzButton" class="buzz-button" onclick="buzz()" disabled>
                BUZZ!
            </button>
            
            <div id="statusMessage" class="status-message"></div>
        </div>
    </div>
    
    <script>
        const socket = io();
        let myPlayerId = null;
        let myTeamId = null;
        let gameState = null;
        
        // Check if player was already registered
        function checkExistingPlayer() {
            const savedPlayerId = localStorage.getItem('jeopardy_player_id');
            const savedTeamId = localStorage.getItem('jeopardy_team_id');
            
            if (savedPlayerId && savedTeamId) {
                // Try to reconnect as existing player
                socket.emit('reconnect_player', { 
                    player_id: savedPlayerId, 
                    team_id: savedTeamId 
                });
            }
        }
        
        socket.on('connect', () => {
            console.log('Connected to server');
            // Request initial game state
            socket.emit('request_game_state');
            // Check if we're reconnecting
            checkExistingPlayer();
        });
        
        socket.on('game_update', (data) => {
            gameState = data;
            
            // Update team dropdown if still in join view
            if (!myPlayerId) {
                loadTeams();
            }
            
            updateUI();
        });
        
        socket.on('registration_success', (data) => {
            if (data.role === 'player') {
                myPlayerId = data.player_id;
                myTeamId = data.team_id;
                
                // Save to localStorage for reconnection
                localStorage.setItem('jeopardy_player_id', myPlayerId);
                localStorage.setItem('jeopardy_team_id', myTeamId);
                
                document.getElementById('joinView').classList.add('hidden');
                document.getElementById('gameView').classList.remove('hidden');
            }
        });
        
        socket.on('buzz_rejected', (data) => {
            setStatus('Buzz rejected: ' + data.reason, 'error');
        });
        
        socket.on('error', (data) => {
            alert('Error: ' + data.message);
        });
        
        socket.on('reconnect_failed', () => {
            // Clear invalid stored credentials
            localStorage.removeItem('jeopardy_player_id');
            localStorage.removeItem('jeopardy_team_id');
        });
        
        function loadTeams() {
            const select = document.getElementById('teamSelect');
            
            if (!gameState || !gameState.teams || gameState.teams.length === 0) {
                select.innerHTML = '<option value="">No teams created yet...</option>';
                return;
            }
            
            select.innerHTML = '<option value="">Select your team...</option>';
            gameState.teams.forEach(team => {
                const option = document.createElement('option');
                option.value = team.id;
                option.textContent = team.name;
                select.appendChild(option);
            });
        }
        
        function joinGame() {
            const name = document.getElementById('playerName').value.trim();
            const teamId = document.getElementById('teamSelect').value;
            
            if (!name || !teamId) {
                alert('Please enter your name and select a team');
                return;
            }
            
            socket.emit('join_game', { name, team_id: teamId });
        }
        
        function buzz() {
            socket.emit('buzz', { player_id: myPlayerId });
        }
        
        function updateUI() {
            if (!gameState || !myTeamId) return;
            
            const myTeam = gameState.teams.find(t => t.id === myTeamId);
            if (!myTeam) return;
            
            document.getElementById('teamName').textContent = myTeam.name;
            document.getElementById('teamScore').textContent = `${myTeam.score}`;
            
            const buzzButton = document.getElementById('buzzButton');
            const questionInfo = document.getElementById('questionInfo');
            
            if (gameState.current_question) {
                questionInfo.classList.remove('hidden');
                document.getElementById('questionCategory').textContent = gameState.current_question.category;
                document.getElementById('questionValue').textContent = `${gameState.current_question.value}`;
                
                if (gameState.buzz_timer_active) {
                    buzzButton.disabled = true;
                    setStatus('Reading question... wait for buzz activation');
                } else if (gameState.question_state === 'buzzing_open') {
                    // Check if my team already attempted
                    const myTeamAttempted = gameState.buzz_queue.some(entry => entry.team_id === myTeamId);
                    const myBuzzPosition = gameState.buzz_queue.findIndex(entry => entry.player_id === myPlayerId);
                    
                    if (myBuzzPosition >= 0) {
                        buzzButton.disabled = true;
                        if (myBuzzPosition === 0) {
                            setStatus("You're up! Answer the question!", 'active');
                        } else {
                            setStatus(`You buzzed in! Position: ${myBuzzPosition + 1}`, 'waiting');
                        }
                    } else if (myTeamAttempted) {
                        buzzButton.disabled = true;
                        setStatus('Your team already attempted this question');
                    } else {
                        buzzButton.disabled = false;
                        setStatus('BUZZ IN NOW!', 'ready');
                    }
                }
            } else {
                questionInfo.classList.add('hidden');
                buzzButton.disabled = true;
                setStatus('Waiting for next question...');
            }
        }
        
        function setStatus(message, type = '') {
            const statusEl = document.getElementById('statusMessage');
            statusEl.textContent = message;
            statusEl.style.background = type === 'ready' ? 'rgba(50,205,50,0.3)' :
                                       type === 'active' ? 'rgba(255,215,0,0.3)' :
                                       type === 'error' ? 'rgba(220,20,60,0.3)' :
                                       'rgba(0,0,0,0.3)';
        }
    </script>
</body>
</html>
"""
