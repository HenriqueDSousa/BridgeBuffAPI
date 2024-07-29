from flask import Flask, jsonify, request
import json

app = Flask(__name__)
scores = []

def load_data():
    global scores
    with open('scores.jsonl', 'r') as file:
        for line in file:
            scores.append(json.loads(line.strip()))

with app.app_context():
    load_data()

@app.route('/api/game/<int:id>', methods=['GET'])
def get_game_by_id(id):
    game = next((score for score in scores if score['id'] == id), None)

    if game:
        return jsonify({
            "game_id": game['id'],
            "game_stats": {
                "cannons": game['cannons'],
                "escaped_ships": game['escaped_ships'],
                "getcannons_received": game['getcannons_received'],
                "getturn_received": game['getturn_received'],
                "last_turn": game['last_turn'],
                "remaining_life_on_escaped_ships": game['remaining_life_on_escaped_ships'],
                "ship_moves": game['ship_moves'],
                "shot_received": game['shot_received'],
                "sunk_ships": game['sunk_ships'],
                "tstamp_auth_completion": game['tstamp_auth_completion'],
                "tstamp_auth_start": game['tstamp_auth_start'],
                "tstamp_completion":game['tstamp_completion'],
                "valid_shots": game['valid_shots'],
                "gas": game['auth']
            }   
        })

    else:
        return jsonify({"error": "Game not found"}), 404

@app.route('/api/rank/sunk', methods=['GET'])
def rank_sunk():
    try:
        limit = int(request.args.get('limit', 10))
        start = int(request.args.get('start', 0))
        print(limit, start)
    except ValueError:
        return jsonify({"error": "Invalid limit or start parameter"}), 400

    if limit > 50:
        return jsonify({"error": "Limit must be 50 or less"}), 400

    games = [game for game in scores if 'sunk_ships' in game]
    sorted_games = sorted(games, key=lambda x:x['sunk_ships'], reverse=True)
    
    paginated_games = sorted_games[start:start + limit]
    total_games = len(sorted_games)

    response = {
        "ranking": "sunk",
        "limit": limit,
        "start": start,
        "games": [game['id'] for game in paginated_games],
        "prev": None if start <= 0 else f"/api/rank/sunk?limit={limit}&start={max(0, start - limit)}",
        "next": None if start+limit >= total_games else f"/api/rank/sunk?limit={limit}&start={start+limit}"
    }

    return jsonify(response)

@app.route('/api/rank/escaped', methods=['GET'])
def rank_escaped():
    try:
        limit = int(request.args.get('limit', 10))
        start = int(request.args.get('start', 0))
        print(limit, start)
    except ValueError:
        return jsonify({"error": "Invalid limit or start parameter"}), 400

    if limit > 50:
        return jsonify({"error": "Limit must be 50 or less"}), 400

    games = [game for game in scores if 'sunk_ships' in game]
    sorted_games = sorted(games, key=lambda x:x['escaped_ships'], reverse=False)
    
    paginated_games = sorted_games[start:start + limit]
    total_games = len(sorted_games)

    response = {
        "ranking": "escaped",
        "limit": limit,
        "start": start,
        "games": [game['id'] for game in paginated_games],
        "prev": f"/api/rank/escaped?limit={limit}&start={max(0, start - limit)}" if start > 0 else None,
        "next": f"/api/rank/escaped?limit={limit}&start={start+limit}" if start+limit < total_games else None
    }

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)