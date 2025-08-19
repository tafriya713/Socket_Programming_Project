#import-required-modules
import socket
import threading

HOST = '127.0.0.1'
PORT = 1234
LISTENER_LIMIT = 5
active_clients=[] #List of all currently connected users

#Function to listen for upcoming message from a client
def listen_for_messages(client,username):

    while 1:

       message = client.recv(2048).decode('utf-8')
       if message != '':

            final_msg = username+ '~' + message
            send_message_to_all(final_msg)
            
       else:
            print(f"This message sent from client {username}is empty")


#Function to send message to a single client
def send_message_to_client(client,message):
     
     client.sendall(message.encode())
            

#Function to send any message to all the clients that
#are currently connected to this server
def send_message_to_all(message):
    

     for user in active_clients:
          
          send_message_to_client(user[1],message)

#Function to handle client
def client_handler(client):
    
    #server will listen for client message that will contain
    #the username
    while 1:

        username=client.recv(2048).decode('utf-8')
        if username !='' :
            active_clients.append((username,client))
            prompt_message = "SERVER~" + f"{username} added to the chat" 
            send_message_to_all(prompt_message)
            break

        else:
            print("Client username is empty")
    
    threading.Thread(target=listen_for_messages,args=(client,username, )).start()


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
        
        
        threading.Thread(target=client_handler,args=(client, )).start()

if __name__ == '__main__':
    main()
