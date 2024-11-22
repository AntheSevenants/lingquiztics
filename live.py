from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
import os
import json
import argparse
import lingquiztics.questions

app = Flask(__name__, template_folder="live/template/", static_folder="live/static/")
app.secret_key = 'secret_key_for_sessions'
socketio = SocketIO(app)

# Load teams from teams.txt
def load_teams():
    with open(args.team_names, 'r') as f:
        return [line.strip() for line in f if line.strip()]

# Load data from JSON file
def load_data():
    if not os.path.exists(DATA_FILE):
        teams = load_teams()
        data = {
            'num_rounds': len(rounds),
            'rounds': list(rounds.keys()),
            'scores': {team: [0] * len(rounds) for team in teams},
            'double_rounds': {team: None for team in teams}
        }
        save_data(data)
    else:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    return data

# Save data to JSON file
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Broadcast data to all clients
def broadcast_scores():
    data = load_data()
    total_scores = calculate_total_scores(data)
    socketio.emit('update_scores', {'scores': data['scores'], 'double_rounds': data['double_rounds'], 'totals': total_scores})

@app.route('/')
def index():
    data = load_data()
    return render_template('index.html', teams=list(data['scores'].keys()), num_rounds=data['num_rounds'])

@app.route('/set_rounds', methods=['POST'])
def set_rounds():
    data = load_data()
    num_rounds = int(request.form['num_rounds'])
    data['num_rounds'] = num_rounds
    data['scores'] = {team: [0] * num_rounds for team in data['scores'].keys()}
    data['double_rounds'] = {team: None for team in data['scores'].keys()}
    save_data(data)
    broadcast_scores()
    return redirect(url_for('index'))

@app.route('/input_scores')
def input_scores():
    data = load_data()
    total_scores = calculate_total_scores(data)
    return render_template('input_scores.html', teams=data['scores'].keys(), num_rounds=data['num_rounds'], scores=data['scores'], double_rounds=data['double_rounds'], rounds=data['rounds'], totals=total_scores)

@app.route('/leaderboard')
def leaderboard():
    data = load_data()
    total_scores = calculate_total_scores(data)

    # Sort by scores in descending order
    sorted_scores = dict(sorted(total_scores.items(), key=lambda item: item[1], reverse=True))
    
    return render_template('leaderboard.html', scores=sorted_scores)

@socketio.on('update_score')
def handle_update_score(data):
    round_num = data['round_num']
    team = data['team']
    score = float(data['score'])

    file_data = load_data()

    # Same score, do not do anything
    if score == file_data['scores'][team][round_num - 1]:
        return
    
    file_data['scores'][team][round_num - 1] = score
    save_data(file_data)
    
    # Recalculate the total for the updated team and broadcast only the updated cell and total
    total_score = calculate_team_total(file_data, team)
    socketio.emit('update_single_cell', {
        'team': team,
        'round_num': round_num,  # send as 1-indexed for client
        'score': score,
        'total_score': total_score
    })

@socketio.on('update_double_round')
def handle_update_double_round(data):
    team = data['team']
    round_num = data['round_num']

    file_data = load_data()
    file_data['double_rounds'][team] = round_num
    save_data(file_data)

    # Recalculate the total for the updated team based on the new double round
    total_score = calculate_team_total(file_data, team)
    socketio.emit('update_single_cell', {
        'team': team,
        'round_num': None,  # No specific cell to update; only total
        'total_score': total_score
    })

def calculate_total_scores(data):
    total_scores = {}
    for team, scores in data['scores'].items():
        double_round = data['double_rounds'].get(team)
        total = 0
        for i, score in enumerate(scores):
            if double_round == i + 1:
                total += score * 2
            else:
                total += score
        total_scores[team] = total
    return total_scores

def calculate_team_total(data, team):
    scores = data['scores'][team]
    double_round = data['double_rounds'].get(team)
    total = 0
    for i, score in enumerate(scores):
        if double_round == i + 1:
            total += score * 2
        else:
            total += score
    return total

#
# Argument parsing
#

parser = argparse.ArgumentParser(description='lingquiztics - live score input and display')
parser.add_argument('questions', type=str,
					help='Path to the JSON file containing the questions')
parser.add_argument('team_names', type=str,
					help='Path to text file with team names (one per line)')
parser.add_argument('data_file', type=str,
					help='Path where state will be stored')
parser.add_argument('--port', type=int, nargs='?', default="5000", help='Port to run the application on')
args = parser.parse_args()

DATA_FILE = args.data_file
rounds = lingquiztics.questions.load(args.questions)

if __name__ == '__main__':
    app.run(debug=True, port=args.port, host="0.0.0.0")