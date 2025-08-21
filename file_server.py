import os
import socket
import threading

IP = socket.gethostbyname(socket.gethostname())
PORT = 4466
ADDR = (IP, PORT)
SIZE = 4096  # larger chunk size for file transfer
FORMAT = "utf-8"
SERVER_DATA_PATH = "server_data"

# Ensure server_data folder exists
if not os.path.exists(SERVER_DATA_PATH):
    os.makedirs(SERVER_DATA_PATH)

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected")
    try:
        conn.send("OK@Welcome to the File Server.".encode(FORMAT))

        while True:
            data = conn.recv(SIZE).decode(FORMAT)
            if not data:
                break

            parts = data.split("@")
            cmd = parts[0]

            if cmd == "HELP":
                send_data = "OK@" \
                    "LIST: List all the files from the server.\n" \
                    "UPLOAD <path>: Upload a file to the server.\n" \
                    "DOWNLOAD <filename>: Download a file from the server.\n" \
                    "DELETE <filename>: Delete a file from the server.\n" \
                    "LOGOUT: Disconnect from the server.\n" \
                    "HELP: List all the commands"
                conn.send(send_data.encode(FORMAT))

            elif cmd == "LIST":
                files = os.listdir(SERVER_DATA_PATH)
                send_data = "OK@" + ("\n".join(files) if files else "The server directory is empty.")
                conn.send(send_data.encode(FORMAT))

            elif cmd == "UPLOAD":
                filename = parts[1]
                filesize = int(parts[2])
                filepath = os.path.join(SERVER_DATA_PATH, filename)

                with open(filepath, "wb") as f:
                    bytes_received = 0
                    while bytes_received < filesize:
                        chunk = conn.recv(min(SIZE, filesize - bytes_received))
                        if not chunk:
                            break
                        f.write(chunk)
                        bytes_received += len(chunk)

                conn.send("OK@File uploaded.".encode(FORMAT))

            elif cmd == "DOWNLOAD":
                filename = parts[1]
                filepath = os.path.join(SERVER_DATA_PATH, filename)

                if os.path.exists(filepath):
                    filesize = os.path.getsize(filepath)
                    # Send metadata first
                    header = f"DOWNLOAD@{filename}@{filesize}"
                    conn.send(header.encode(FORMAT))

                    # Send file in chunks
                    with open(filepath, "rb") as f:
                        while True:
                            bytes_read = f.read(SIZE)
                            if not bytes_read:
                                break
                            conn.send(bytes_read)
                else:
                    conn.send("OK@File not found.".encode(FORMAT))

            elif cmd == "DELETE":
                filename = parts[1]
                files = os.listdir(SERVER_DATA_PATH)
                if filename in files:
                    os.remove(os.path.join(SERVER_DATA_PATH, filename))
                    conn.send("OK@File deleted.".encode(FORMAT))
                else:
                    conn.send("OK@File not found.".encode(FORMAT))

            elif cmd == "LOGOUT":
                conn.send("DISCONNECTED@Goodbye!".encode(FORMAT))
                break

            else:
                conn.send("OK@Invalid command. Type HELP for options.".encode(FORMAT))

    except ConnectionResetError:
        print(f"[DISCONNECTED] {addr} forcibly closed the connection")
    finally:
        conn.close()
        print(f"[DISCONNECTED] {addr} closed connection")

def main():
    print("[STARTING] Server is starting...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen()
    print("[LISTENING] Server is listening.")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    main()
