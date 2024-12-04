import socket
from functions.codec import decode, check_fields, add_received_IP
from functions.methods import client_methods
from functions.read_write import update_log
from functions.dns_manager import retrieve_proxy_data
from functions.send import send_message
from functions.state import State

import threading

# import subprocess

proxy = ("", 8000)
own_ip = socket.gethostbyname(socket.gethostname())
user = "Bob"
proxy_name = None

STATE = State()

# Launch client_listener.py after client_interface.py code is executed
# try:
#     result = subprocess.run(['python', 'client_listener.py'], check=True)
#     print("client_listener.py executed successfully")
# except subprocess.CalledProcessError as e:
#     print("Failed to execute client_listener.py:", e)


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

def manage_connection(client_socket, addr):
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

        client_methods[data["Request"]["Method"]](data, state=STATE, proxy_data=proxy_data) # llamar funcion segun metodo
        break

def handle_client(client_socket, addr):
    print(f"\nGot a connection from {addr}")
    manage_connection(client_socket, addr)
    client_socket.close()
    print("> ")

def accept_connections():
    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

# Start a thread to handle incoming connections
connection_thread = threading.Thread(target=accept_connections)
connection_thread.daemon = True
connection_thread.start()

commands = ['help', 'register', 'invite', 'proxy', 'user', 'user?', 'proxy?', 'exit']

while True:

    command = input("> ")
    
    match command.lower():
        case 'register':
            if not proxy_name:
                print("Please specify a proxy (command 'proxy')")
                continue
            # create and encode message
            message = f"REGISTER sip:registrar.{proxy_name} SIP/2.0\nVia: SIP/2.0/UDP {host}.{proxy_name}:{port};branch=z9hG4bKnashds7\nMax-Forwards: 70\nTo: {user} <sip:{user.lower()}@{proxy_name}>\nFrom: {user} <sip:{user.lower()}@{proxy_name}>;tag=456248\nCall-ID: 843817637684230\nCSeq: 1826 REGISTER\nContact: <sip:{user.lower()}@{own_ip}>\nExpires: 7200\nContent-Length: 0\r\n"
            send_message(proxy[0], proxy[1], message)
                
        case 'invite':
            user_to_invite = input("User to invite [username@proxy_name] > ")
            # alice@atlanta.com
            if not user_to_invite:
                continue
            if not proxy_name:
                print("Please specify a proxy (command 'proxy')")
                continue
            # create and encode message
            message = f"INVITE sip:{user_to_invite} SIP/2.0\nVia: SIP/2.0/UDP {host}.{proxy_name};branch=z9hG4bK776asdhds\nMax-Forwards: 70\nTo: {user_to_invite.split('@')[0]} <sip:{user_to_invite}>\nFrom: {user} <sip:{user.lower()}@{proxy_name}>;tag=1928301774\nCall-ID: a84b4c76e66710\nCSeq: 314159 INVITE\nContact: <sip:{user.lower()}@{host}.{proxy_name}>\nContent-Type: application/sdp\nContent-Length: 142\r\n"
            
            send_message(proxy[0], proxy[1], message)
            
            STATE.update('inviting')

        case 'state':
            print(f"Current state: {STATE.current_state}")

        
        case 'proxy':
            
            # ip = input("Please enter the proxy IP: ")
            # if not ip:
            #     print("IP error")
            #     continue
            
            # try:
            #     port = int(input("Please enter the proxy port (default=8000): "))
            # except:
            #     port = 8000

            # proxy = (ip, port)

            name = input("Proxy name > ")
            if not name:
                continue
            
            proxy_data = retrieve_proxy_data(name)

            if not proxy_data:
                print("Proxy not found")
                continue

            print(f"Proxy {name} found at {proxy_data[0]}:{proxy_data[1]}")
            proxy = proxy_data
            proxy_name = name

        case 'user':
            name = input("User name > ")
            if ' ' in name:
                print("User name cannot contain spaces")
                continue
            if name:
                user = name

        case 'user?':
            print(f"User: {user}")

        case 'proxy?':
            print(f"Proxy {proxy_name} address: {proxy[0]}:{proxy[1]}")

        case 'exit':
            print("Exiting...")
            break

        case 'q':
            match STATE.current_state:
                case 'ringing_back':
                    STATE.update('idle')
                    print("Call canceled")
                    # SEND CANCEL REQUEST
                case 'ringing':
                    STATE.update('idle')
                    # SEND RESPONSE 603 DECLINE
                    print("Call declined")
                case 'talking':
                    STATE.update('idle')
                    # SEND BYE REQUEST
                    print("Call terminated")
                case _:
                    print("Unknown command")
        
        case 'a':
            if STATE.current_state == 'ringing':
                pass
                # SEND RESPONSE 200 OK
            else:
                print("Unknown command")

        case 'help':
            print("Available commands:")
            for c in commands:
                print(f" - {c}")

        case _:
            print("Unknown command")


