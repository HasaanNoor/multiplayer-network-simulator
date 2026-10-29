import socket

SERVER_ADDRESS = ("127.0.0.1", 5000)

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
client.settimeout(5)

message = "Hello Server!"
client.sendto(message.encode("utf-8"), SERVER_ADDRESS)

try:
    data, address = client.recvfrom(1024)
    print(f"Server response: {data.decode('utf-8')}")

except socket.timeout:
    print("Server did not respond!")

finally:
    client.close()
