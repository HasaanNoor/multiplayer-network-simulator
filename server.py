import json
import socket

HOST = "127.0.0.1"
PORT = 5000
MAX_CLIENTS = 2
GAME_WIDTH = 640
GAME_HEIGHT = 480
MOVE_DISTANCE = 10
INITIAL_POSITIONS = {1: [100, 100], 2: [300, 100]}


def send_json(server, address, message):
    server.sendto(json.dumps(message).encode("utf-8"), address)


def register_client(server, address, clients, positions, tick):
    if address in clients:
        player_id = clients[address]
    elif len(clients) < MAX_CLIENTS:
        player_id = len(clients) + 1
        clients[address] = player_id
        print(f"Registered {address} as Player {player_id}")
    else:
        send_json(server, address, {"type": "server_full", "message": "Server is full."})
        print(f"Rejected {address}: server full")
        return

    send_json(server, address, {
        "type": "registered",
        "player_id": player_id,
        "tick": tick,
        "players": positions,
    })


def move_player(player_id, direction, positions):
    x, y = positions[player_id]
    if direction == "up":
        y -= MOVE_DISTANCE
    elif direction == "down":
        y += MOVE_DISTANCE
    elif direction == "left":
        x -= MOVE_DISTANCE
    else:
        x += MOVE_DISTANCE

    positions[player_id] = [
        min(max(x, 0), GAME_WIDTH - 1),
        min(max(y, 0), GAME_HEIGHT - 1),
    ]


def broadcast_state(server, clients, positions, tick):
    message = {"type": "state", "tick": tick, "players": positions}
    for address in clients:
        send_json(server, address, message)


def send_error(server, address, message):
    send_json(server, address, {"type": "error", "message": message})


def run_server():
    clients = {}
    positions = {player_id: position.copy() for player_id, position in INITIAL_POSITIONS.items()}
    last_sequences = {}
    tick = 0
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        server.bind((HOST, PORT))
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            data, address = server.recvfrom(4096)
            try:
                message = json.loads(data.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                send_error(server, address, "Malformed JSON.")
                continue

            if not isinstance(message, dict) or not isinstance(message.get("type"), str):
                send_error(server, address, "Message must be a JSON object with a type.")
                continue

            if message["type"] == "register":
                register_client(server, address, clients, positions, tick)
                continue

            if address not in clients:
                send_error(server, address, "Register before sending commands.")
                continue

            if message["type"] != "move":
                send_error(server, address, "Unsupported message type.")
                continue

            direction = message.get("direction")
            sequence = message.get("sequence")
            if direction not in {"up", "down", "left", "right"}:
                send_error(server, address, "Invalid movement direction.")
                continue
            if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 0:
                send_error(server, address, "Sequence must be a nonnegative integer.")
                continue

            player_id = clients[address]
            if sequence <= last_sequences.get(player_id, -1):
                send_json(server, address, {
                    "type": "ignored",
                    "message": "Stale or duplicate sequence.",
                    "tick": tick,
                })
                continue

            last_sequences[player_id] = sequence
            move_player(player_id, direction, positions)
            tick += 1
            print(f"Player {player_id} moved {direction}; tick {tick}")
            broadcast_state(server, clients, positions, tick)
    except KeyboardInterrupt:
        print("\nServer shutting down.")
    finally:
        server.close()


if __name__ == "__main__":
    run_server()
