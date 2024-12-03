import socket
from functions.codec import decode, check_fields, add_received_IP
from functions.methods import client_methods
from functions.read_write import update_log

log = 'databases/log_client.txt'

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get local machine name
host = socket.gethostname()
port = 5060

socket_ready = False
while not socket_ready:
    try:
        # Bind the socket to the port
        server_socket.bind((host, port))
        # Start listening for incoming connections
        server_socket.listen(5)

        socket_ready = True
    except:
        port += 1


ip_address = socket.gethostbyname(host)

print(f"Server listening on {host} {ip_address} : {port}")


while True:
    # Establish a connection
    
    client_socket, addr = server_socket.accept()
    print(f"Got a connection from {addr}")

    while True:
        # Receive data from the client
        rx = client_socket.recv(1024)

        if not rx:
            continue # esperar mensajes
        
        msg = rx.decode('utf-8')
        # [:-2]   # decodificar y quitar \r\n

        update_log(log, msg) # actualizar log

        if msg == "Q":
            print("salir")
            client_socket.close()
            break

        try:
            data = decode(msg)  # decodificar mensaje
        except Exception as e:
            print("Error: ", e)
            break
    
        if not check_fields(data):
            print('fields error')
            client_socket.send('fields error!!'.encode('ascii')) 
            continue

        add_received_IP(data, addr[0]) # agregar IP de origen

        client_methods[data["Request"]["Method"]](data) # llamar funcion segun metodo
        break

        
    
    
    client_socket.close()   
    # Close the connection with the client