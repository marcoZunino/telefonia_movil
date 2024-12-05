import socket
from functions.codec import decode, check_fields, add_received_IP
from functions.methods import methods
from functions.read_write import update_log
from functions.dns_manager import add_dns_entry

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Get local machine name
host = socket.gethostname()
port = 8000

proxy_name = input("Please enter the proxy name: ")

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

print(f"Proxy {proxy_name} listening on {host} {ip_address} : {port}")
add_dns_entry(proxy_name, ip_address, port)

proxy_data = {
    'hostname': host,
    'name': proxy_name,
    'ip': ip_address,
    'port': port
}


while True:
    # Establish a connection
    
    client_socket, addr = server_socket.accept()
    print(f"\nGot a connection from {addr}")

    while True:
        # Receive data from the client
        rx = client_socket.recv(1024)

        if not rx:
            continue # esperar mensajes
        
        msg = rx.decode('utf-8')
        # [:-2]   # decodificar y quitar \r\n

        update_log('logs_proxy/log_' + proxy_name + '.txt', msg) # actualizar log
        # print(msg)


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

        methods[data["Request"]["Method"]](data, proxy_data) # llamar funcion segun metodo
        break

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