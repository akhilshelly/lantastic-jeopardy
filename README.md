# Jeopardy Web App

A fully-featured Jeopardy game webapp for local party hosting.

## Setup

1. Install Python 3.8 or higher

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create your questions file at `data/questions.csv` with format:

```csv
Round,Category,Value,Question,Answer
1,Geography,100,This is the capital of France,What is Paris?
1,Geography,200,This is the largest country by area,What is Russia?
```

## Running the Game

1. Start the server:

```bash
python app.py
```

2. The Trebek (host) opens a browser to `http://localhost:9001`

3. Players scan the QR code or navigate to the join URL shown on screen

4. Trebek creates teams in the lobby

5. Players join their teams

6. Trebek starts Round 1!

## Game Flow

1. **Lobby**: Trebek creates teams, players join
2. **Round 1**: $100-$500 questions
3. **Round 2**: $200-$1000 questions
4. **Scoring**: Team-based, negative points for wrong answers

## Features

- Real-time WebSocket communication
- QR code for easy mobile joining
- 4-second buzz delay for fair play
- Buzz queue system
- Team-based scoring with negatives
- Classic Jeopardy styling

## Backlog

- Final Jeopardy with wagering
- Redemption mode (multiple teammates per question)
- Audio/visual cues
- Daily Doubles

## Network Access

The server binds to 0.0.0.0 so any device on your local network can connect.
Find your computer's local IP address and share with players.