import streamlit as st
import socket
import json

def create_http_request(method, path, host):
    return f"{method} {path} HTTP/1.1\r\nHost: {host}\r\nConnection: keep-alive\r\n\r\n"

def get_response(sock):
    response = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        response += chunk

    if response == b"":
        return {}
    headers, body = response.split(b"\r\n\r\n", 1)
    headers = headers.decode()
    content_length = int([line for line in headers.split("\r\n") if "Content-Length" in line][0].split(": ")[1])
    
    while len(body) < content_length:
        body += sock.recv(content_length - len(body))

    return json.loads(body.decode())

def get_game_by_id(game_id):
    path = f'/api/game/{game_id}'
    response = {"game": []}
    ip, port = host.split(":")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, int(port)))
        request = create_http_request("GET", path, host)
        sock.sendall(request.encode())
        response = get_response(sock)
    except (BrokenPipeError, ConnectionResetError) as e:
        st.error(f"Socket error: {e}")
        
    except Exception as e:
        st.error(f"Error: {e}")
        
    return response
       

def get_games(host, ranking_type, limit=50):
    path = f"/api/rank/{ranking_type}?limit={limit}&start=0"
    response = {"games": []}
    ip, port = host.split(":")
    while path:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, int(port)))
            request = create_http_request("GET", path, host)
            sock.sendall(request.encode())
            temp_resp = get_response(sock)
            response["games"] += temp_resp.get("games", [])
            path = temp_resp["next"] if temp_resp else None
        except (BrokenPipeError, ConnectionResetError) as e:
            st.error(f"Socket error: {e}")
            break
        except Exception as e:
            st.error(f"Error: {e}")
            break
    return response.get("games", [])

def get_game_details(host, game_id):
    path = f"/api/game/{game_id}"
    request = create_http_request("GET", path, host)
    ip, port = host.split(":")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, int(port)))
    sock.sendall(request.encode())
    response = get_response(sock)
    return response

def analyze_best_performance(host):
    games = get_games(host, "sunk")
    gas_stats = {}
    top100 = []

    for game_id in games:
        game_details = get_game_details(host, game_id)
        gas = game_details["game_stats"]["gas"]
        top100.append({"gas": gas, "sunk_ships": game_details["game_stats"]["sunk_ships"]})
        if gas not in gas_stats:
            gas_stats[gas] = {"count": 1, "total_sunk": 0}

    top100 = sorted(top100, key=lambda x: x['sunk_ships'], reverse=True)
    top100 = top100[:100]

    for elem in top100:
        gas_stats[elem['gas']]["count"] += 1
        gas_stats[elem['gas']]["total_sunk"] += elem["sunk_ships"]

    return gas_stats

def analyze_cannon_placements(host):
    games = get_games(host, "escaped")
    placement_stats = {}

    for game_id in games:
        game_details = get_game_details(host, game_id)
        placement = game_details["game_stats"]["cannons"]
        escaped_ships = game_details["game_stats"]["escaped_ships"]

        placement_counts = [0, 0, 0, 0, 0, 0, 0, 0]
        for elem in placement:
            placement_counts[elem[0] - 1] += 1

        normalized_placement = "".join([str(p) for p in placement_counts])

        if normalized_placement not in placement_stats:
            placement_stats[normalized_placement] = {"count": 0, "total_escaped": 0}

        placement_stats[normalized_placement]["count"] += 1
        placement_stats[normalized_placement]["total_escaped"] += escaped_ships

    sorted_placement_stats = sorted(placement_stats.items(), key=lambda x: x[1]["total_escaped"] / x[1]["count"])
    return sorted_placement_stats

# Streamlit UI
st.title("Game Analysis Tool")

host = st.text_input("Host (IP:Port)", "localhost:8000")
analysis = st.selectbox("Analysis Type", ["Best Performance", "Cannon Placements", "Select game by id"])

game_id = None
if analysis == "Select game by id":
    game_id = st.number_input("Enter Game ID:", min_value=1, step=1)

start_analysis = st.button("Start Analysis")

if start_analysis:
    if analysis == "Best Performance":
        results = analyze_best_performance(host)
        st.write("Gas Stats:")
        st.write(results)
    elif analysis == "Cannon Placements":
        results = analyze_cannon_placements(host)
        st.write("Cannon Placement Stats:")
        st.write(results)
    
    elif analysis == "Select game by id":
        result = get_game_by_id(game_id)
        st.write(f"Game {game_id}:")
        st.write(result)