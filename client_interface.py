import socket
from functions.codec import decode, check_fields, add_received_IP
from functions.methods import client_methods
from functions.read_write import update_log
from functions.dns_manager import retrieve_proxy_data
from functions.send import generate_branch, send_bye, send_cancel, send_message, send_response
from functions.state import State

import threading

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


own_ip = socket.gethostbyname(host)

print(f"Server listening on {host} {own_ip} : {port}")


user_data = {
    'hostname' : host,
    'name' : "Bob",
    'ip' : own_ip,
    'port' : port
}

proxy_data = {
    'name': None,
    'ip': None,
    'port': 8000
}

def manage_connection(client_socket, addr):
    while True:
        # Receive data from the client
        rx = client_socket.recv(1024)

        if not rx:
            continue # esperar mensajes
        
        msg = rx.decode('utf-8')
        # [:-2]   # decodificar y quitar \r\n

        update_log(f'logs_client/log_{user_data["name"]}.txt', msg) # actualizar log

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

        client_methods[data["Request"]["Method"]](data, state=STATE, user_data=user_data, proxy_data=proxy_data) # llamar funcion segun metodo
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


commands = ['help', 'register', 'invite', 'proxy', 'user', 'state', 'reset state', 'last data', 'dest user', 'user?', 'proxy?', 'exit']

STATE = State()

while True:

    command = input("> ")
    
    match command.lower():
        case 'register':
            if not proxy_data["name"]:
                print("Please specify a proxy (command 'proxy')")
                continue
            # create and encode message
            message = f"REGISTER sip:registrar.{proxy_data["name"]} SIP/2.0\nVia: SIP/2.0/UDP {host}.{proxy_data["name"]}:{port};branch={generate_branch()}\nMax-Forwards: 70\nTo: {user_data["name"]} <sip:{user_data["name"].lower()}@{proxy_data["name"]}>\nFrom: {user_data["name"]} <sip:{user_data["name"].lower()}@{proxy_data["name"]}>;tag=456248\nCall-ID: 843817637684230\nCSeq: 1826 REGISTER\nContact: <sip:{user_data["name"].lower()}@{own_ip}>\nExpires: 7200\nContent-Length: 0\r\n"
            send_message(proxy_data["ip"], proxy_data["port"], message)
                
        case 'invite':
            user_to_invite = input("User to invite [username@proxy_name] > ")
            # alice@atlanta.com
            if not user_to_invite:
                continue
            if not proxy_data["name"]:
                print("Please specify a proxy (command 'proxy')")
                continue
            # create and encode message
            message = f"INVITE sip:{user_to_invite} SIP/2.0\nVia: SIP/2.0/UDP {host}.{proxy_data["name"]};branch={generate_branch()}\nMax-Forwards: 70\nTo: {user_to_invite.split('@')[0]} <sip:{user_to_invite}>\nFrom: {user_data["name"]} <sip:{user_data["name"].lower()}@{proxy_data["name"]}>;tag=1928301774\nCall-ID: a84b4c76e66710\nCSeq: 314159 INVITE\nContact: <sip:{user_data["name"].lower()}@{host}.{proxy_data["name"]}>\nContent-Type: application/sdp\nContent-Length: 142\r\n"
            
            send_message(proxy_data["ip"], proxy_data["port"], message)
            
            STATE.save_data(decode(message))
            STATE.update('inviting')

        case 'state':
            print(f"Current state: {STATE.current_state}")
        
        case 'reset state':
            STATE = State()

        case 'last data':
            print(f"Last saved data: {STATE.last_data}")
        
        case 'dest user':
            print(f"Destination user info: {STATE.dest_user_info}")
        
        case 'proxy':

            name = input("Proxy name > ")
            if not name:
                continue
            
            proxy_address = retrieve_proxy_data(name)

            if not proxy_address:
                print("Proxy not found")
                continue

            print(f"Proxy {name} found at {proxy_address[0]}:{proxy_address[1]}")
            
            proxy_data["name"] = name
            proxy_data["ip"] = proxy_address[0]
            proxy_data["port"] = proxy_address[1]

        case 'user':
            name = input("User name > ")
            if ' ' in name:
                print("User name cannot contain spaces")
                continue
            if name:
                user_data["name"] = name

        case 'user?':
            print(f"User: {user_data["name"]}")

        case 'proxy?':
            print(f"Proxy {proxy_data["name"]} address: {proxy_data["ip"]}:{proxy_data["port"]}")

        case 'exit':
            print("Exiting...")
            break

        case 'q':
            match STATE.current_state:

                case 'ringing_back': # cancelar antes de que contesten
                    # SEND CANCEL REQUEST
                    send_cancel(proxy_data, STATE.last_data)
                    STATE.reset()
                    print("Call canceled")

                case 'ringing': # rechazar llamada
                    # send response 603 Decline
                    send_response(603, STATE.last_data, (proxy_data["ip"], proxy_data["port"]))
                    STATE.reset()
                    print("Call declined")
                    
                case 'talking':
                    # send BYE request
                    send_bye(STATE.last_data, STATE.dest_user_info)
                    STATE.reset()
                    print("Call terminated")

                case _:
                    print("Unknown command")
        
        case 'a':
            if STATE.current_state == 'ringing':
                
                send_response(200, STATE.last_data, (proxy_data["ip"], proxy_data["port"]), contact=f'sip:{user_data["name"].lower()}@{user_data["ip"]}')
                
            else:
                print("Unknown command")

        case 'help':
            print("Available commands:")
            for c in commands:
                print(f" - {c}")

        case _:
            print("Unknown command")


