import time

from functions.dynamic_prints import waiting_print
from functions.send import forward_message, forward_response, get_dest_user_info, manage_result, send_ack, send_response
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
                         data_fields["Via"][0]['uri'],
                         client_port, contact)

    send_response(200, data, (client_ip, client_port))

def invite(data, proxy_data = None):
    
    print("invite...", data["Fields"]["From"], 'to', data["Fields"]["To"])

    port = search_port(data, proxy_data=proxy_data)
    send_response(100, data, (data["Fields"]["Via"][0]["received"], port))

    result = forward_message(proxy_data, data)
    print("result for forward_message is:", result)
    manage_result(result, data, proxy_data) # send possible error response
    
def cancel(data, proxy_data = None):
    # forward message to destination
    print("cancel...")
    result = forward_message(proxy_data, data)
    manage_result(result, data, proxy_data)

def ack(data, proxy_data = None):
    # forward message to destination
    print("ack...")
    result = forward_message(proxy_data, data)
    manage_result(result, data, proxy_data)
    
def bye(data, proxy_data = None):
    # forward message to destination
    print("bye...")
    result = forward_message(proxy_data, data)
    manage_result(result, data, proxy_data)

def response(data, proxy_data = None):

    # print("response...", data["Request"]["Response Code"], data["Request"]["Response Description"])

    result = 200

    match int(data["Request"]["Response Code"]):

        case 100:
            print("Trying")

        case 180:
            print("Ringing")
            result = forward_response(proxy_data, data)

        case 200:
            print("OK")
            result = forward_response(proxy_data, data)

        case 400:
            print("Bad Request")
            result = forward_response(proxy_data, data)

        case 404:
            print("Not Found")
            result = forward_response(proxy_data, data)

        case 483:
            print("Too Many Hops")
            result = forward_response(proxy_data, data)
        
        case 486:
            print("Busy Here")
            result = forward_response(proxy_data, data)

        case 603:
            print("Decline")
            result = forward_response(proxy_data, data)

        case _:
            print(data["Request"]["Response Description"])

    manage_result(result, data, proxy_data)


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

    if state.current_state == 'idle':

        send_response(180, data, (data["Fields"]["Via"][0]["received"], port), contact = f'sip:{user_data["name"].lower()}@{user_data["ip"]}')

        state.update('ringing')

        state.save_data(data)

        print("\nIncoming call from", data["Fields"]["From"])
        print("Press 'a' (+ enter) to accept")
        print("Press 'q' (+ enter) to decline")
        waiting_print("Ringing...", state=state)
    
    else:
        # ocupado
        send_response(486, data, (data["Fields"]["Via"][0]["received"], port))

def client_ack(data, state = State(), user_data = None, proxy_data = None):

    if state.current_state == 'ringing':

        data["Fields"]["Via"][0]['received'] = state.last_data["Fields"]["Via"][-1]['received']
        data["Fields"]["Contact"] = f'{state.last_data["Fields"]["Contact"].split('@')[0]}@{data["Fields"]["Via"][0]['received']}'
        # Contact: sip:name@uri -> Contact: sip:name@ip
        to = data["Fields"]["To"].split(';')[0]
        data["Fields"]["To"] = data["Fields"]["From"].split(';')[0]
        data["Fields"]["From"] = to
        # to <-> from

        state.save_data(data)

        state.update('talking')
        state.save_dest_user_info(get_dest_user_info(data, proxy_data))

        print("Call accepted, press 'q' (+ enter) to terminate")
        waiting_print("Talking...", state=state)

def client_cancel(data, state = State(), user_data = None, proxy_data = None):

    if state.current_state == 'ringing':

        print("Call canceled from", data["Fields"]["From"])

        state.reset()

def client_bye(data, state = State(), user_data = None, proxy_data = None):

    if state.current_state == 'talking':

        print("Call terminated")
        send_response(200, data, (state.dest_user_info["ip"], state.dest_user_info["port"]))
        state.reset()

def client_response(data, state = State(), user_data = None, proxy_data = None):
    
    # print("response...", data["Request"]["Response Code"], data["Request"]["Response Description"])

    match int(data["Request"]["Response Code"]):

        case 100:
            print("Trying")

        case 180:
            print("Ringing")
            
            if state.current_state == "inviting":
                state.update("ringing_back")
                print(f"Waiting response from {data["Fields"]["To"].split(' ')[0]}, press 'q' (+ enter) to cancel")
                waiting_print("Ringing back...", state=state)
            
        case 200:
            print("OK")

            if state.current_state == 'idle':
                state.user_registered = True

            if state.current_state == "ringing_back":
                
                state.update("talking")
                data["Fields"]["From"] = data["Fields"]["From"].split(';')[0]
                data["Fields"]["To"] = data["Fields"]["To"].split(';')[0]
                state.save_data(data)
                state.save_dest_user_info(get_dest_user_info(data, proxy_data))

                send_ack(data, state.dest_user_info)

                print("Call accepted, press 'q' (+ enter) to terminate")
                waiting_print("Talking...", state=state)

        case 400:
            print("Bad Request")
            state.reset()

        case 404:
            print("Not Found")
            state.reset()

        case 483:
            print("Too Many Hops")
            state.reset()
        
        case 486:
            print("Busy Here")
            if state.current_state == "inviting":
                print(data["Fields"]["To"].split(' ')[0], "is busy")
                state.reset()

        case 603:
            print("Decline")
            if state.current_state == "ringing_back":
                state.update("idle")
                print("Call declined from", data["Fields"]["To"].split(' ')[0])

        case _:
            print(data["Request"]["Response Description"])
            state.reset()

    return

client_methods = {}
client_methods["INVITE"] = client_invite
client_methods["ACK"] = client_ack
client_methods["CANCEL"] = client_cancel
client_methods["BYE"] = client_bye
client_methods["Response"] = client_response








