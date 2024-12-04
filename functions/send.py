import socket

from functions.codec import add_via_entry, encode, encode_via, pop_via_entry, update_to_proxy
from functions.read_write import query_location_service
from functions.dns_manager import retrieve_proxy_data

location_service = "databases/location_service.txt"

def send_message(host, port, message):
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to the listener socket
        client_socket.connect((host, port))
        
        # Send the message encoded in UTF-8
        client_socket.send(message.encode('utf-8'))
        
        print(f"Message sent to {host}:{port}")
    
    except Exception as e:
        print(f"Failed to send message: {e}")
    
    finally:
        # Close the socket connection
        client_socket.close()

response_codes = {
    100 : "Trying",
    180 : "Ringing",
    200 : "OK",
    400 : "Bad Request",
    404 : "Not Found",
    483 : "Too Many Hops",
    603 : "Decline",
}

def send_response(code, data, addr):

    print("sending response", code, addr)

    message = f'SIP/2.0 {code} {response_codes[code]}\n{encode_via(data["Fields"]["Via"])}To: {data["Fields"]["To"]}\nFrom: {data["Fields"]["From"]}\nCall-ID: {data["Fields"]["Call-ID"]}\nCSeq: {data["Fields"]["CSeq"]}\nContent-Length: {data["Fields"]["Content-Length"]}\r\n'

    send_message(addr[0], addr[1], message)

def forward_message(proxy_data, data):

    # update max-forwards
    
    data["Fields"]["Max-Forwards"] = str(int(data["Fields"]["Max-Forwards"]) - 1)

    if int(data["Fields"]["Max-Forwards"]) == 0:
        print("Max-Forwards reached")
        # SEND ERROR RESPONSE
        return
    
    add_via_entry(data, {"protocol": "SIP/2.0/UDP", "uri": proxy_data["name"]}) # AGREGAR BRANCH

    dest_proxy = data["Request"]["uri"].split('@')[1]
    dest_username = data["Request"]["uri"].split('@')[0].strip('sip:')

    if dest_proxy == proxy_data["name"]: # local client

        try:
            client_ip = query_location_service(location_service, username=dest_username, proxy_name=dest_proxy)["IP"]
        except Exception as e:
            print("Error forwarding message to client > ", e, dest_username)
            return

        print("forwarding message directly to client in", client_ip)
        update_to_proxy(data, client_ip)
        send_message(client_ip, 5060, encode(data))
        # WAIT 180 RINGING
        
    
    else:
        try:
            dest_proxy_addr = retrieve_proxy_data(dest_proxy)
        except Exception as e:
            print("Error forwarding message", e)
            return
        
        print("forwarding message to", dest_proxy, dest_proxy_addr)
        send_message(dest_proxy_addr[0], dest_proxy_addr[1], encode(data))
        # WAIT 100 TRYING

def forward_response(proxy_data, data):
    
    current_via = pop_via_entry(data)

    if current_via["received"] != proxy_data["ip"]:
        return

    print("forwarding response", data["Request"]["Response Code"], "to", data["Fields"]["From"])
    send_message(data["Fields"]["Via"][0]["received"], 5060, encode(data))

def send_ack(data, proxy_data):

    # if data["Request"]["Method"] != "Response" or data["Request"]["Response Code"] != 200:
    #     return
    
    if "Contact" not in data["Fields"]:
        uri = data["Fields"]["To"].split(' ')[0]
        dest = proxy_data
    else:
        uri = data["Fields"]["Contact"].strip('<>')
        dest = (uri.split("@")[1], 5060)
    
    data["Request"]["Method"] = "ACK"
    data["Request"].pop("Response Code")
    data["Request"].pop("Response Description")
    data["Request"]["uri"] = uri

    data["Fields"]["Max-Forwards"] = "70"
    data["Fields"]["Content-Length"] = "0"
    data["Fields"]["CSeq"] = "314159 ACK"

    data["Fields"].pop("Contact", None)
    data["Fields"].pop("Content-Type", None)
    data["Fields"]["Via"][0].pop("received", None)

    send_message(dest[0], dest[1], encode(data))

