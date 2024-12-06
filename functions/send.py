import socket

from functions.codec import add_via_entry, encode, encode_via, pop_via_entry, update_to_proxy
from functions.read_write import ls_proxy, query_location_service, search_port
from functions.dns_manager import retrieve_all_proxys, retrieve_proxy_data
import random
import string


# sending ----------------

def send_message(host, port, message):

    result = 200

    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to the listener socket
        client_socket.connect((host, port))
        
        # Send the message encoded in UTF-8
        client_socket.send(message.encode('utf-8'))
        
        print(f"Message sent to {host}:{port}")
    
    except:
        print(f"Failed to send message")
        result = 404
    
    finally:
        # Close the socket connection
        client_socket.close()
        return result

def send_ack(data, dest_user_info):

    data["Request"]["Method"] = "ACK"
    data["Request"].pop("Response Code")
    data["Request"].pop("Response Description")
    data["Request"]["uri"] = dest_user_info["uri"]

    data["Fields"]["Max-Forwards"] = "70"
    data["Fields"]["Content-Length"] = "0"
    data["Fields"]["CSeq"] = "314159 ACK"

    data["Fields"].pop("Contact", None)
    data["Fields"].pop("Content-Type", None)
    data["Fields"]["Via"][0].pop("received", None)

    return send_message(dest_user_info["ip"], dest_user_info["port"], encode(data))

def send_cancel(proxy_data, data):

    print("sending cancel to", data["Fields"]["To"].split(' ')[0])

    data["Request"]["Method"] = "CANCEL"
    data["Fields"]["CSeq"] = f'{data["Fields"]["CSeq"].split(' ')[0]} CANCEL'
    data["Fields"]["Max-Forwards"] = "70"
    data["Fields"]["Content-Length"] = "0"
    data["Fields"].pop("Content-Type", None)

    return send_message(proxy_data['ip'], proxy_data['port'], encode(data))

def send_bye(data, dest_user_info):

    data["Request"]["Method"] = "BYE"
    data["Request"].pop("Response Code", None)
    data["Request"].pop("Response Description", None)
    data["Request"]["uri"] = dest_user_info["uri"]

    data["Fields"]["Max-Forwards"] = "70"
    data["Fields"]["Content-Length"] = "0"
    data["Fields"]["CSeq"] = "231 BYE"

    data["Fields"].pop("Contact", None)
    data["Fields"].pop("Content-Type", None)
    data["Fields"]["Via"][0].pop("received", None)

    return send_message(dest_user_info["ip"], dest_user_info["port"], encode(data))


# forwarding ----------------

def forward_message(proxy_data, data):

    result = 200

    # update max-forwards
    
    data["Fields"]["Max-Forwards"] = str(int(data["Fields"]["Max-Forwards"]) - 1)

    if int(data["Fields"]["Max-Forwards"]) == 0:
        print("Max-Forwards reached")
        return 483  # send 483 Too Many Hops
    
    add_via_entry(data, {"protocol": "SIP/2.0/UDP", "uri": proxy_data["name"], "branch": generate_branch()})

    dest_proxy = data["Request"]["uri"].split('@')[1]
    dest_username = data["Request"]["uri"].split('@')[0].strip('sip:')

    if dest_proxy == proxy_data["name"]: # local client

        try:
            client_data = query_location_service(ls_proxy(proxy_data["name"]), username=dest_username, proxy_name=dest_proxy)
            client_ip = client_data["IP"]
            client_port = int(client_data["port"])

        except:
            print("Error forwarding message to client > ", dest_username)
            return 404

        print("forwarding message directly to client", dest_username, client_ip, client_port)
        update_to_proxy(data, client_ip)
        result = send_message(client_ip, client_port, encode(data))
        
    else:
        try:
            dest_proxy_addr = retrieve_proxy_data(dest_proxy)
        except:
            print("Error forwarding message to other proxy", dest_proxy)
            return 404
        
        print("forwarding message to", dest_proxy, dest_proxy_addr)
        result = send_message(dest_proxy_addr[0], dest_proxy_addr[1], encode(data))

    return result

def forward_response(proxy_data, data):

    if len(data["Fields"]["Via"]) == 1:
        print("response has only one via")
        return 200

    current_via = pop_via_entry(data)

    if current_via["received"] != proxy_data["ip"]:
        print("response not for me:", current_via)
        return 404
    
    dest_ip = data["Fields"]["Via"][0]["received"]
    dest_port = search_port(data, proxy_data=proxy_data)

    if not dest_port:
        return 404

    print("forwarding response", data["Request"]["Response Code"], "to", data["Fields"]["Via"][0]["uri"])
    return send_message(dest_ip, dest_port, encode(data))

# responses ----------------

response_codes = {
    100 : "Trying",
    180 : "Ringing",
    200 : "OK",
    400 : "Bad_Request",
    404 : "Not_Found",
    483 : "Too_Many_Hops",
    486 : "Busy_Here",
    603 : "Decline",
}

def send_response(code, data, addr, contact = None):

    print("sending response", code, addr)

    content_length = 0
    if code == 200:
        content_length = data["Fields"]["Content-Length"]

    message = f'SIP/2.0 {code} {response_codes[code]}\n{encode_via(data["Fields"]["Via"])}To: {data["Fields"]["To"]}\nFrom: {data["Fields"]["From"]}\nCall-ID: {data["Fields"]["Call-ID"]}'
    
    if contact:
        message += f'\nContact: <{contact}>'
    
    message += f'\nCSeq: {data["Fields"]["CSeq"]}\nContent-Length: {content_length}\r\n'

    send_message(addr[0], addr[1], message)

def manage_result(result, data, proxy_data):
    
    if result == 200:
            pass
    else:
        send_response(result, data, (data["Fields"]["Via"][0]["received"], search_port(data, proxy_data=proxy_data)))
        # send error response


# aux functions ----------------

def get_dest_user_info(data, proxy_data):

    if "Contact" in data["Fields"]:

        uri = data["Fields"]["Contact"]

        try:
            port = search_port(data, proxy_data = {
                    "name" : data["Fields"]["To"].split(' ')[1].strip('<>').split('@')[1]
                    }, username=data["Fields"]["To"].split(' ')[0].lower())
        except:
            port = 5060

        ip = data["Fields"]["Contact"].split("@")[1]
        
    else:

        uri = data["Fields"]["To"].split(' ')[1]
        ip = proxy_data["ip"]
        port = proxy_data["port"]

    return {
        'uri' : uri,
        'ip' : ip,
        'port' : port,
    }

def generate_branch():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=14))







