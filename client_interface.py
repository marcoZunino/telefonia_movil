import socket
from functions.codec import decode, check_fields, add_received_IP
# from functions.methods import methods
from functions.read_write import update_log
from functions.send import send_message

proxy = ("192.168.0.207", 8000)

while True:
    command = input("Please enter a command (type 'exit' to quit): ")
    commands = ['help', 'register', 'proxy', 'proxy?', 'exit']
    match command.lower():
        case 'register':
            if proxy[0] and proxy[1]:
                # create and encode message
                message = "REGISTER sip:registrar.biloxi.com SIP/2.0\nVia: SIP/2.0/UDP bobspc.biloxi.com:5060;branch=z9hG4bKnashds7\nMax-Forwards: 70\nTo: Bob <sip:bob@biloxi.com>\nFrom: Bob <sip:bob@biloxi.com>;tag=456248\nCall-ID: 843817637684230@998sdasdh09\nCSeq: 1826 REGISTER\nContact: <sip:bob@192.0.2.4>\nExpires: 7200\nContent-Length: 0\r\n"
                send_message(proxy[0], proxy[1], message)
            else:
                print("Please enter a proxy address (command 'proxy')")
        
        case 'proxy':
            ip = input("Please enter the proxy IP: ")
            if not ip:
                print("IP error")
            else:
                port = None
                try:
                    port = int(input("Please enter the proxy port (default=8000): "))
                except:
                    port = 8000
                proxy = (ip, port)

        case "proxy?":
            print(f"Proxy address: {proxy[0]}:{proxy[1]}")

        case 'exit':
            print("Exiting...")
            break

        case 'help':
            print("Available commands:")
            for c in commands:
                print(f" - {c}")

        case _:
            print("Unknown command")


