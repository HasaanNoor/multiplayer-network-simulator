import socket

SERVER_ADDRESS = ("127.0.0.1", 5000)
SOCKET_TIMEOUT = 5


def run_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.settimeout(SOCKET_TIMEOUT)

    try:
        while True:
            try:
                message = input("Enter a message (or 'quit' to exit): ")
            except EOFError:
                print("\nClient shutting down.")
                break

            if message.strip().lower() == "quit":
                print("Client shutting down.")
                break

            client.sendto(message.encode("utf-8"), SERVER_ADDRESS)

            try:
                data, address = client.recvfrom(1024)
                print(f"Server response: {data.decode('utf-8')}")
            except socket.timeout:
                print("Server did not respond. Try again or type 'quit' to exit.")
    except KeyboardInterrupt:
        print("\nClient shutting down.")
    finally:
        client.close()


if __name__ == "__main__":
    run_client()
