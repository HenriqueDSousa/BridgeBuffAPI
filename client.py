#!/usr/local/bin/python

import socket
import json
import sys

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
            print(f"Socket error: {e}")
            break
        except Exception as e:
            print(f"Error: {e}")
            break
    print(response)
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

def analyze_best_performance(host, output_file):
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
    
    print(gas_stats)
    
    with open(output_file, "w") as f:
        for gas, stats in gas_stats.items():
            avg_sunk = stats["total_sunk"] / stats["count"]
            f.write(f"{gas},{stats['count']},{avg_sunk}\n")

def analyze_cannon_placements(host, output_file):
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
    
    with open(output_file, "w") as f:
        for placement, stats in sorted_placement_stats:
            avg_escaped = stats["total_escaped"] / stats["count"]
            f.write(f"{placement},{avg_escaped}\n")

def main():
    if len(sys.argv) != 5:
        print("Usage: ./client <IP> <port> <analysis> <output>")
        sys.exit(1)
    
    ip = sys.argv[1]
    port = int(sys.argv[2])
    analysis = int(sys.argv[3])
    output_file = sys.argv[4]
    host = f"{ip}:{port}"
        
    if analysis == 1:
        analyze_best_performance(host, output_file)
    elif analysis == 2:
        analyze_cannon_placements(host, output_file)
    else:
        print("Invalid analysis type. Use 1 or 2.")
        sys.exit(1)

if __name__ == "__main__":
    main()
