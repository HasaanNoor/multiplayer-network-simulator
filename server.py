import socket

HOST = "127.0.0.1"
PORT = 5000

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((HOST, PORT))

print(f"Server listening on {HOST}: {PORT}")

while True:
    data, address = server.recvfrom(1024)
    message = data.decode("utf-8")
    print(f"Received from {address}: {message}")
    server.sendto("Hello Client!". encode("utf-8"), address)