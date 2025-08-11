#import-required-modules
import socket
import threading

HOST = '127.0.0.1'
PORT = 1234
LISTENER_LIMIT = 5

# Main-function
def main():
    # creating the socket class object
    # we are using IPv4 addresses
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((HOST, PORT))
        print(f"Running the server on {HOST} {PORT}")
    except:
        print(f"Unable to bind to host {HOST} and port {PORT}")
        return  # Stop execution if binding fails

    # set server limit
    server.listen(LISTENER_LIMIT)
    print(f"Server listening with limit {LISTENER_LIMIT}...")

    while True:
        client, address = server.accept()
        print(f"Successfully connected to Client {address[0]}:{address[1]}")
        client.send("Hello from server!".encode())  # optional test
        client.close()

if __name__ == '__main__':
    main()
