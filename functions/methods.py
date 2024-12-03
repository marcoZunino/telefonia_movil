from functions.codec import encode, update_to_proxy
from functions.send import send_message
from functions.read_write import add_user_to_sip_file, query_location_service, retrieve_proxy_data

location_service = "databases/location_service.txt"

def register(data, proxy_data = None):
    data_fields = data["Fields"]
    
    print("register...", data_fields["From"])

    try:
        contact = data_fields["Contact"]
    except:
        contact = data_fields["Via"]
        try:
            contact += ';received = ' + data_fields["Via"]["received"]
        except:
            pass
    
    add_user_to_sip_file(location_service, data_fields["Via"]["uri"], contact)

    send_response(200, data, (data["Fields"]["Via"]["received"], 5060))


    # wait 200 OK or timer

def invite(data, proxy_data = None):
    data_fields = data["Fields"]
    print("invite...", data_fields["From"], 'to', data_fields["To"])
    
    send_response(100, data, (data["Fields"]["Via"]["received"], 5060))

    forward_message(proxy_data, data)
    


def ack(data, proxy_data = None):
    return

def cancel(data, proxy_data = None):
    return

def bye(data, proxy_data = None):
    return

def response(data, proxy_data = None):
    data_fields = data["Fields"]
    print("response...", data["Request"]["Response Code"], data["Request"]["Response Description"])
    return

methods = {}
methods["REGISTER"] = register
methods["INVITE"] = invite
methods["ACK"] = ack
methods["CANCEL"] = cancel
methods["BYE"] = bye
methods["Response"] = response


def client_invite(data, proxy_data = None):
    data_fields = data["Fields"]
    print("invite received from", data_fields["From"], '...')
    
    send_response(180, data, (data["Fields"]["Via"]["received"], 8000))

client_methods = {}
client_methods["INVITE"] = client_invite
client_methods["Response"] = response

response_codes = {}
response_codes[100] = "Trying"
response_codes[180] = "Ringing"
response_codes[200] = "OK"


def send_response(code, data, addr):

    print("sending response", addr)

    message = f'SIP/2.0 {code} {response_codes[code]}\nVia: SIP/2.0/UDP pc33.atlanta.com;branch=z9hG4bKnashds8\nTo: {data["Fields"]["To"]}\nFrom: {data["Fields"]["From"]}\nCall-ID: {data["Fields"]["Call-ID"]}\nCSeq: {data["Fields"]["CSeq"]}\nContent-Length: {data["Fields"]["Content-Length"]}\r\n'

    send_message(addr[0], addr[1], message)

def forward_message(proxy_data, data):

    dest_proxy = data["Request"]["uri"].split('@')[1]
    dest_username = data["Request"]["uri"].split('@')[0].strip('sip:')

    if dest_proxy == proxy_data["name"]: # local client

        try:
            client_ip = query_location_service(location_service, username=dest_username)["IP"]
        except Exception as e:
            print("Error forwarding message to client", e)
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





