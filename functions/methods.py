import time

from functions.dynamic_prints import waiting_print
from functions.send import forward_message, forward_response, send_ack, send_message, send_response
from functions.read_write import add_user_to_sip_file, ls_proxy, search_port
from functions.state import State

# ------------ PROXY METHODS ------------

def register(data, proxy_data = None):
    data_fields = data["Fields"]
    
    print("register...", data_fields["From"])

    client_ip = None

    try:
        contact = data_fields["Contact"]
    except:
        via = data_fields["Via"][0]
        contact = via['uri']
        try:
            contact += '@' + via['received']
        except:
            pass

    client_ip = contact.split('@')[1]

    client_port = int(data_fields["Via"][0]['port'])
    
    add_user_to_sip_file(ls_proxy(proxy_data["name"]),
                         f'{data_fields["Via"][0]['uri']}:{client_port}',
                         contact)

    send_response(200, data, (client_ip, client_port))

def invite(data, proxy_data = None):
    data_fields = data["Fields"]
    print("invite...", data_fields["From"], 'to', data_fields["To"])

    port = search_port(data, proxy_data=proxy_data)
        
    send_response(100, data, (data["Fields"]["Via"][0]["received"], port))

    forward_message(proxy_data, data)

def cancel(data, proxy_data = None):
    # FORWARD CANCEL TO DESTINATION
    print("cancel...")
    return

def ack(data, proxy_data = None):
    # forward message to destination (optional)
    print("ack...")
    return

def bye(data, proxy_data = None):
    # forward message to destination (optional)
    print("bye...")
    return

def response(data, proxy_data = None):

    # print("response...", data["Request"]["Response Code"], data["Request"]["Response Description"])

    match int(data["Request"]["Response Code"]):

        case 100:
            print("Trying")

        case 180:
            print("Ringing")
            forward_response(proxy_data, data)

        case 200:
            print("OK")
            forward_response(proxy_data, data)

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


# ------------ CLIENT METHODS ------------

def client_invite(data, state = State(), user_data = None, proxy_data = None):
    data_fields = data["Fields"]
    print("invite received from", data_fields["From"], '...')

    port = search_port(data)
    
    send_response(180, data, (data["Fields"]["Via"][0]["received"], port), contact = f'sip:{user_data["name"].lower()}@{user_data["ip"]}')

    if state.current_state == 'idle':
        state.update('ringing')
        state.save_data(data)
        print("\nIncoming call from", data["Fields"]["From"])
        print("Press 'a' (+ enter) to accept")
        print("Press 'q' (+ enter) to decline")
        waiting_print("Ringing...", state=state)

def client_ack(data, state = State(), user_data = None, proxy_data = None):

    if state.current_state == 'ringing':
        state.update('talking')
        state.save_data(data)

        print("Call accepted, press 'q' (+ enter) to terminate")
        waiting_print("Talking...", state=state)

def client_cancel(data, state = State(), user_data = None, proxy_data = None):

    if state.current_state == 'ringing':
        state.update('idle')
        print("Call canceled from", data["Fields"]["From"])

def client_bye(data, state = State(), user_data = None, proxy_data = None):

    if state.current_state == 'talking':
        state.update('idle')
        print("Call terminated")

    # SEND RESPONSE 200 OK

def client_response(data, state = State(), user_data = None, proxy_data = None):
    
    # print("response...", data["Request"]["Response Code"], data["Request"]["Response Description"])

    match int(data["Request"]["Response Code"]):

        case 100:
            print("Trying")

        case 180:
            print("Ringing")
            
            if state.current_state == "inviting":
                state.update("ringing_back")
                print("Waiting response, press 'q' (+ enter) to cancel")
                waiting_print("Ringing back...", state=state)
            
        case 200:
            print("OK")
            # state.update()
            if state.current_state == "ringing_back":
                
                state.update("talking")
                state.save_data(data)

                send_ack(data, proxy_data)

                print("Call accepted, press 'q' (+ enter) to terminate")
                waiting_print("Talking...", state=state)

                

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
client_methods["ACK"] = client_ack
client_methods["CANCEL"] = client_cancel
client_methods["BYE"] = client_bye
client_methods["Response"] = client_response








