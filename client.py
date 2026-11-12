import json
import select
import socket
import sys

SERVER_ADDRESS = ("127.0.0.1", 5000)
SOCKET_TIMEOUT = 5
DIRECTIONS = {"w": "up", "a": "left", "s": "down", "d": "right"}


def send_json(client, message):
    client.sendto(json.dumps(message).encode("utf-8"), SERVER_ADDRESS)


def receive_json(client):
    data, _ = client.recvfrom(4096)
    return json.loads(data.decode("utf-8"))


def display_message(message):
    message_type = message.get("type")
    if message_type in {"state", "registered"}:
        players = message["players"]
        print(f"Tick {message['tick']}: Player 1 {players.get('1')}, Player 2 {players.get('2')}")
    elif message_type in {"error", "ignored", "server_full"}:
        print(f"Server: {message.get('message', message_type)}")
    else:
        print(f"Server sent an unexpected message: {message}")


def register(client):
    send_json(client, {"type": "register"})
    try:
        message = receive_json(client)
    except socket.timeout:
        print("Server did not respond to registration.")
        return False
    except (UnicodeDecodeError, json.JSONDecodeError):
        print("Server sent an invalid registration response.")
        return False

    if message.get("type") != "registered":
        display_message(message)
        return False

    print(f"Registered as Player {message['player_id']}")
    display_message(message)
    return True


def run_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(SOCKET_TIMEOUT)

    try:
        if not register(client):
            return

        client.setblocking(False)
        sequence = 0
        print("Commands: w=up, a=left, s=down, d=right, quit=exit")
        print("> ", end="", flush=True)

        while True:
            readable, _, _ = select.select([client, sys.stdin], [], [], SOCKET_TIMEOUT)
            if not readable:
                print("\nNo server updates received recently.")
                print("> ", end="", flush=True)
                continue

            if client in readable:
                try:
                    message = receive_json(client)
                    print()
                    display_message(message)
                except (BlockingIOError, UnicodeDecodeError, json.JSONDecodeError):
                    print("\nReceived an invalid server response.")
                print("> ", end="", flush=True)

            if sys.stdin in readable:
                command = sys.stdin.readline()
                if command == "":
                    print("\nClient shutting down.")
                    break

                command = command.strip().lower()
                if command == "quit":
                    print("Client shutting down.")
                    break
                if command not in DIRECTIONS:
                    print("Invalid command. Use w, a, s, d, or quit.")
                else:
                    send_json(client, {
                        "type": "move",
                        "direction": DIRECTIONS[command],
                        "sequence": sequence,
                    })
                    sequence += 1
                print("> ", end="", flush=True)
    except KeyboardInterrupt:
        print("\nClient shutting down.")
    except OSError as error:
        print(f"Network error: {error}")
    finally:
        client.close()


if __name__ == "__main__":
    run_client()
