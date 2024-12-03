import socket
from functions.codec import decode, check_fields, add_received_IP
# from functions.methods import methods
from functions.read_write import retrieve_proxy_data
from functions.send import send_message
# import subprocess

proxy = ("", 8000)
own_ip = socket.gethostbyname(socket.gethostname())
user = "Bob"
proxy_name = None

# Launch client_listener.py after client_interface.py code is executed
# try:
#     result = subprocess.run(['python', 'client_listener.py'], check=True)
#     print("client_listener.py executed successfully")
# except subprocess.CalledProcessError as e:
#     print("Failed to execute client_listener.py:", e)

while True:
    command = input("Please enter a command (type 'exit' to quit): ")
    commands = ['help', 'register', 'invite', 'proxy', 'user', 'user?', 'proxy?', 'exit']
    
    match command.lower():
        case 'register':
            if not proxy_name:
                print("Please specify a proxy (command 'proxy')")
                continue
            # create and encode message
            message = f"REGISTER sip:registrar.{proxy_name} SIP/2.0\nVia: SIP/2.0/UDP bobspc.biloxi.com:5060;branch=z9hG4bKnashds7\nMax-Forwards: 70\nTo: {user} <sip:{user.lower()}@{proxy_name}>\nFrom: {user} <sip:{user.lower()}@{proxy_name}>;tag=456248\nCall-ID: 843817637684230@998sdasdh09\nCSeq: 1826 REGISTER\nContact: <sip:{user.lower()}@{own_ip}>\nExpires: 7200\nContent-Length: 0\r\n"
            send_message(proxy[0], proxy[1], message)
                
        case 'invite':
            user_to_invite = input("Please enter the user to invite [username@proxy_name]: ")
            # alice@atlanta.com
            if not user_to_invite:
                continue
            if not proxy_name:
                print("Please specify a proxy (command 'proxy')")
                continue
            # create and encode message
            message = f"INVITE sip:{user_to_invite} SIP/2.0\nVia: SIP/2.0/UDP bobspc.biloxi.com;branch=z9hG4bK776asdhds\nMax-Forwards: 70\nTo: {user_to_invite} <sip:{user_to_invite}>\nFrom: {user} <sip:{user.lower()}@{proxy_name}>;tag=1928301774\nCall-ID: a84b4c76e66710@pc33.atlanta.com\nCSeq: 314159 INVITE\nContact: <sip:{user.lower()}@{own_ip}>\nContent-Type: application/sdp\nContent-Length: 142\r\n"
            send_message(proxy[0], proxy[1], message)

        
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

            name = input("Please enter the proxy name: ")
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
            name = input("Please enter the user name: ")
            if ' ' not in name:
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

        case 'help':
            print("Available commands:")
            for c in commands:
                print(f" - {c}")

        case _:
            print("Unknown command")


