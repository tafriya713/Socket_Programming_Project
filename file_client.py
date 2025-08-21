import os
import socket

IP = socket.gethostbyname(socket.gethostname())
PORT = 4466
ADDR = (IP, PORT)
SIZE = 4096
FORMAT = "utf-8"

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)

    while True:
        data = client.recv(SIZE).decode(FORMAT)
        if not data:
            break

        if "@" in data:
            cmd, msg = data.split("@", 1)
            if cmd == "OK":
                print(msg)
            elif cmd == "DISCONNECTED":
                print(msg)
                break
        else:
            print(data)

        user_input = input("> ").strip().split(" ")
        cmd = user_input[0].upper()

        if cmd == "HELP":
            client.send(cmd.encode(FORMAT))

        elif cmd == "LIST":
            client.send(cmd.encode(FORMAT))

        elif cmd == "UPLOAD":
            if len(user_input) < 2:
                print("Usage: UPLOAD <path>")
                continue
            path = user_input[1]
            if not os.path.exists(path):
                print("File not found.")
                continue

            filesize = os.path.getsize(path)
            filename = os.path.basename(path)

            # Send metadata first
            header = f"UPLOAD@{filename}@{filesize}"
            client.send(header.encode(FORMAT))

            # Send file content in chunks
            with open(path, "rb") as f:
                while True:
                    bytes_read = f.read(SIZE)
                    if not bytes_read:
                        break
                    client.send(bytes_read)

        elif cmd == "DOWNLOAD":
            if len(user_input) < 2:
                print("Usage: DOWNLOAD <filename>")
                continue

            filename = user_input[1]
            client.send(f"DOWNLOAD@{filename}".encode(FORMAT))

            header = client.recv(SIZE).decode(FORMAT)
            if header.startswith("DOWNLOAD@"):
                _, filename, filesize = header.split("@")
                filesize = int(filesize)
                filepath = os.path.join(".", filename)

                # Receive file content
                with open(filepath, "wb") as f:
                    bytes_received = 0
                    while bytes_received < filesize:
                        chunk = client.recv(min(SIZE, filesize - bytes_received))
                        if not chunk:
                            break
                        f.write(chunk)
                        bytes_received += len(chunk)
                print(f"Downloaded file: {filename}")
            else:
                print(header.split("@",1)[1])

        elif cmd == "DELETE":
            if len(user_input) < 2:
                print("Usage: DELETE <filename>")
                continue
            client.send(f"{cmd}@{user_input[1]}".encode(FORMAT))

        elif cmd == "LOGOUT":
            client.send(cmd.encode(FORMAT))
            # wait for server confirmation
            data = client.recv(SIZE).decode(FORMAT)
            if "@" in data:
                print(data.split("@",1)[1])
            break

        else:
            print("Invalid command. Type HELP for options.")

    print("Disconnected from the server.")
    client.close()

if __name__ == "__main__":
    main()
