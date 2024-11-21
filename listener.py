import socket
from functions import decode, check_fields
from methods import methods

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get local machine name
host = socket.gethostname()
port = 8000

# Bind the socket to the port
server_socket.bind((host, port))

# Start listening for incoming connections
server_socket.listen(5)

ip_address = socket.gethostbyname(host)

print(f"Server listening on {host} {ip_address} : {port}")

LOCATION_SERVICE = {}

while True:
    # Establish a connection
    
    client_socket, addr = server_socket.accept()
    print(f"Got a connection from {addr}")
    LOCATION_SERVICE[client_socket] = {
        'Address' : addr
    }
    
    # Send a thank you message to the client
    message = 'Thank you for connecting\nClose socket connection with "Q"\n'
    client_socket.send(message.encode('ascii'))

    while True:
        # Receive data from the client
        rx = client_socket.recv(1024)

        if not rx:
            continue
        
        msg = rx.decode('utf-8')[:-2]
        print(f"> {msg}")

        with open('log.txt', 'a') as log_file:
            log_file.write(msg + '\n')

        if msg == "Q":
            print("salir")
            client_socket.close()
            break


        try:
            data = decode(msg)

            # print(data)

            if not check_fields(data):
                print('fields error')
                client_socket.send('fields error!!'.encode('ascii'))
                continue
            
            client_socket.send("fields check ok!".encode('ascii'))

            methods[data["Request"]["Method"]](client_socket, data) # llamar funcion segun metodo

        except:
            pass
        # if msg == "SIP INVITE":
        #     trying = True
        #     # print("SIP INVITE")
        #     message = '> SIP 100 Trying\n'
        #     client_socket.send(message.encode('ascii'))
        
        # if trying:
            # if msg == "SIP PRACK":
            #     trying = False
            #     print("SIP PRACK")
    

    
    client_socket.close()   
    # Close the connection with the client

