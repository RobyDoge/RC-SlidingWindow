import random
import socket
import threading


def getRandomNumber()->int:
    return random.randint(1,100)


class PackageServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.lock = threading.Lock()
        self.data_store = []

    def handle_client(self, client_socket, client_address):
        with client_socket:
            while True:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    decoded_data = data.decode('utf-8')
                    
                    # Save the package
                    with self.lock:
                        self.data_store.append(decoded_data)

                    if getRandomNumber()<10:
                        print(f"Oops! ACK not sent for package: {decoded_data}")
                        continue
                    # Send ACK
                    ack_message = "ACK"
                    
                    client_socket.sendall(ack_message.encode('utf-8'))
                    print(f"Sent ACK for pachage {decoded_data}")
                except socket.error as e:
                    break

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen()

            while True:
                client_socket, client_address = server_socket.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
                client_thread.start()

# Example usage
if __name__ == "__main__":
    host = "localhost"
    port = 12345

    server = PackageServer(host, port)
    server.start_server()
