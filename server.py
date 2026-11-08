import socket

HOST = "127.0.0.1"
PORT = 5000
MAX_CLIENTS = 2


def get_player_id(address, clients):
    if address in clients:
        return clients[address]

    if len(clients) >= MAX_CLIENTS:
        return None

    player_id = len(clients) + 1
    clients[address] = player_id
    print(f"Registered {address} as Player {player_id}")
    return player_id


def run_server():
    clients = {}
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        server.bind((HOST, PORT))
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            data, address = server.recvfrom(1024)
            message = data.decode("utf-8")
            player_id = get_player_id(address, clients)

            if player_id is None:
                response = "Server full. Maximum of 2 players are already connected."
                print(f"Rejected {address}: server full")
            else:
                print(f"Received from Player {player_id} {address}: {message}")
                response = f"Player {player_id}: server received '{message}'"

            server.sendto(response.encode("utf-8"), address)
    except KeyboardInterrupt:
        print("\nServer shutting down.")
    finally:
        server.close()


if __name__ == "__main__":
    run_server()
