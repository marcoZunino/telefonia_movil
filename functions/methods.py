import time
from functions.codec import add_via_entry, encode, encode_via, pop_via_entry, update_to_proxy
from functions.dynamic_prints import waiting_print
from functions.send import send_message
from functions.read_write import add_user_to_sip_file, query_location_service, retrieve_proxy_data
from functions.state import State

location_service = "databases/location_service.txt"

def register(data, proxy_data = None):
    data_fields = data["Fields"]
    
    print("register...", data_fields["From"])

    client_ip = None

    try:
        contact = data_fields["Contact"]
    except:
        via = data_fields["Via"][0]
        contact = '<' + via["uri"]
        try:
            contact += '@' + via["received"] + '>'
        except:
            pass

    client_ip = contact.split('@')[1].strip('>').split(':')[0]
    
    add_user_to_sip_file(location_service, data_fields["Via"][0]["uri"], contact)

    send_response(200, data, (client_ip, 5060))


    # wait 200 OK or timer

def invite(data, proxy_data = None):
    data_fields = data["Fields"]
    print("invite...", data_fields["From"], 'to', data_fields["To"])
    
    send_response(100, data, (data["Fields"]["Via"][0]["received"], 5060))

    forward_message(proxy_data, data)



def ack(data, proxy_data = None):
    return

def cancel(data, proxy_data = None):
    return

def bye(data, proxy_data = None):
    return

def response(data, proxy_data = None):

    # print("response...", data["Request"]["Response Code"], data["Request"]["Response Description"])

    match int(data["Request"]["Response Code"]):

        case 100:
            print("Trying")

        case 180:
            print("Ringing")
            forward_response(proxy_data, data)
            
            time.sleep(3) # sustituir por respuesta del destinatario
            send_response(200, data, (data["Fields"]["Via"][0]["received"], 5060))

        case 200:
            print("OK")

        case 400:
            print("Bad Request")

        case 404:
            print("Not Found")

        case 483:
            print("Too Many Hops")

        case 603:
            print("Decline")

        case _:
            print("Unknown response")

    return

methods = {}
methods["REGISTER"] = register
methods["INVITE"] = invite
methods["ACK"] = ack
methods["CANCEL"] = cancel
methods["BYE"] = bye
methods["Response"] = response


def client_invite(data, state = None, proxy_data = None):
    data_fields = data["Fields"]
    print("invite received from", data_fields["From"], '...')
    
    send_response(180, data, (data["Fields"]["Via"][0]["received"], 8000))

def client_response(data, state = State(), proxy_data = None):
    
    # print("response...", data["Request"]["Response Code"], data["Request"]["Response Description"])

    match int(data["Request"]["Response Code"]):

        case 100:
            print("Trying")

        case 180:
            
            state.current_state = "ringing"
            # while state.current_state == "ringing":
            #     waiting_print("Ringing...", 1)
            waiting_print("Ringing...", state=state)
            
        case 200:
            print("OK")
            state.update()

            if state.current_state == "talking":
                waiting_print("Talking...", state=state)
                print("Call terminated")

        case 400:
            print("Bad Request")

        case 404:
            print("Not Found")

        case 483:
            print("Too Many Hops")

        case 603:
            print("Decline")

        case _:
            print("Unknown response")

    return


client_methods = {}
client_methods["INVITE"] = client_invite
client_methods["Response"] = client_response

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
        




