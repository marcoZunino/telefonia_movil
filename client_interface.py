import socket
from functions.codec import decode, check_fields, add_received_IP
# from functions.methods import methods
from functions.send import send_message

proxy = ("192.168.0.207", 8000)
own_ip = socket.gethostbyname(socket.gethostname())
user = "Bob"
proxy_name = "biloxi.com"

while True:
    command = input("Please enter a command (type 'exit' to quit): ")
    commands = ['help', 'register', 'invite', 'proxy', 'user', 'user?', 'proxy?', 'exit']
    
    match command.lower():
        case 'register':
            if not proxy[0]:
                print("Please enter a proxy address (command 'proxy')")
                continue
            # create and encode message
            message = f"REGISTER sip:registrar.{proxy_name} SIP/2.0\nVia: SIP/2.0/UDP bobspc.biloxi.com:5060;branch=z9hG4bKnashds7\nMax-Forwards: 70\nTo: {user} <sip:{user.lower()}@{proxy_name}>\nFrom: {user} <sip:{user.lower()}@{proxy_name}>;tag=456248\nCall-ID: 843817637684230@998sdasdh09\nCSeq: 1826 REGISTER\nContact: <sip:{user.lower()}@{own_ip}>\nExpires: 7200\nContent-Length: 0\r\n"
            send_message(proxy[0], proxy[1], message)
                
        case 'invite':
            user_to_invite = input("Please enter the user to invite [username@proxy_name]: ")
            # alice@atlanta.com
            if not user_to_invite:
                continue
            if not proxy[0]:
                print("Please enter a proxy address (command 'proxy')")
                continue
            # create and encode message
            message = f"INVITE sip:{user_to_invite} SIP/2.0\nVia: SIP/2.0/UDP bobspc.biloxi.com;branch=z9hG4bK776asdhds\nMax-Forwards: 70\nTo: {user_to_invite} <sip:{user_to_invite}>\nFrom: {user} <sip:{user.lower()}@{proxy_name}>;tag=1928301774\nCall-ID: a84b4c76e66710@pc33.atlanta.com\nCSeq: 314159 INVITE\nContact: <sip:{user.lower()}@{own_ip}>\nContent-Type: application/sdp\nContent-Length: 142\r\n"
            send_message(proxy[0], proxy[1], message)

        
        case 'proxy':
            
            ip = input("Please enter the proxy IP: ")
            if not ip:
                print("IP error")
                continue
            
            try:
                port = int(input("Please enter the proxy port (default=8000): "))
            except:
                port = 8000

            proxy = (ip, port)

            name = input("Please enter the proxy name: ")
            if not name:
                continue

            proxy_name = name
        
        case 'user':
            name = input("Please enter the user name: ")
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


