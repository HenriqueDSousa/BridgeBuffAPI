from flask import Flask, jsonify, request
import json
from flasgger import Swagger, swag_from

app = Flask(__name__)
swagger = Swagger(app, config={
    'headers': [],
    'specs': [
        {
            'endpoint': 'apispec',
            'route': '/apispec.json',
            'rule_filter': lambda rule: True,  # all in
            'model_filter': lambda tag: True,  # all in
        }
    ],
    'static_url_path': '/flasgger_static',
    'swagger_ui': True,
    'specs_route': '/swagger/'
})

scores = []

def load_data():
    global scores
    with open('scores.jsonl', 'r') as file:
        for line in file:
            scores.append(json.loads(line.strip()))

with app.app_context():
    load_data()

@app.route('/api/game/<int:id>', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'Game found',
            'schema': {
                'type': 'object',
                'properties': {
                    'game_id': {'type': 'integer'},
                    'game_stats': {'type': 'object'},
                },
                'example': {
                    "game_id": 1,
                    "game_stats": {
                        "cannons": [[3, 1], [1, 1], [8, 3], [3, 3], [7, 2], [2, 2], [3, 2], [6, 3]],
                        "escaped_ships": 312,
                        "getcannons_received": 8,
                        "getturn_received": 1089,
                        "last_turn": 272,
                        "remaining_life_on_escaped_ships": 491,
                        "ship_moves": 4438,
                        "shot_received": 1546,
                        "sunk_ships": 716,
                        "tstamp_auth_completion": 1713369173.8847864,
                        "tstamp_auth_start": 1713369153.8624742,
                        "tstamp_completion": 1713369232.3878376,
                        "valid_shots": 1546,
                        "gas": "ifs4:1:2c3bb3f0e946a1afde7d9d0c8c818762a6189e842abd8aaaf85c9faac5b784d2+ifs4:2:cf87a60a90159078acecca4415c0331939ebb28ac5528322ac03d7c26b140b98+e51d06a4174b5385c8daff714827b4b4cb4f93ff1b83af86defee3878c2ae90f"
                    }
                }
            }
        },
        404: {
            'description': 'Game not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
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
@swag_from({
    'parameters': [
        {
            'name': 'limit',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'default': 10,
            'description': 'Number of games to return'
        },
        {
            'name': 'start',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'default': 0,
            'description': 'Starting index for pagination'
        }
    ],
    'responses': {
        200: {
            'description': 'List of games ranked by sunk ships',
            'schema': {
                'type': 'object',
                'properties': {
                    'ranking': {'type': 'string'},
                    'limit': {'type': 'integer'},
                    'start': {'type': 'integer'},
                    'games': {'type': 'array', 'items': {'type': 'integer'}},
                    'prev': {'type': 'string', 'nullable': True},
                    'next': {'type': 'string', 'nullable': True}
                }
            }
        },
        400: {
            'description': 'Invalid request',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
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
@swag_from({
    'parameters': [
        {
            'name': 'limit',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'default': 10,
            'description': 'Number of games to return'
        },
        {
            'name': 'start',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'default': 0,
            'description': 'Starting index for pagination'
        }
    ],
    'responses': {
        200: {
            'description': 'List of games ranked by escaped ships',
            'schema': {
                'type': 'object',
                'properties': {
                    'ranking': {'type': 'string'},
                    'limit': {'type': 'integer'},
                    'start': {'type': 'integer'},
                    'games': {'type': 'array', 'items': {'type': 'integer'}},
                    'prev': {'type': 'string', 'nullable': True},
                    'next': {'type': 'string', 'nullable': True}
                }
            }
        },
        400: {
            'description': 'Invalid request',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
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
    app.run(debug=True, port=8000, host="0.0.0.0")
