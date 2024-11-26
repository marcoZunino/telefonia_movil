from functions.send import send_message
from functions.read_write import add_user_to_sip_file

location_service = "databases/location_service.txt"

def register(client_socket, data):
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

    print("sending response", data_fields["Via"]["received"])

    message = 'SIP/2.0 200 OK\nVia: SIP/2.0/UDP server10.biloxi.com;branch=z9hG4bKnashds8;received=192.0.2.3\nMax-Forwards: 70\nTo: Bob <sip:bob@biloxi.com>;tag=a6c85cf\nFrom: Alice <sip:alice@atlanta.com>;tag=1928301774\nCall-ID: a84b4c76e66710@pc33.atlanta.com\nCSeq: 314159 INVITE\nContact: <sip:bob@192.0.2.4>\nContent-Type: application/sdp\nContent-Length: 131'

    # try:
    #     client_socket.send(message.encode('utf-8'))
    # except:
    #     send_message(data_fields["Via"]["received"], 8000, message)

    send_message(data_fields["Via"]["received"], 5060, message)


    # wait 200 OK or timer

def invite(client_socket, data):
    data_fields = data["Fields"]
    print("invite...", data_fields["From"], 'to', data_fields["To"])
    
    print("sending response", data_fields["Via"]["received"])

    message = 'SIP/2.0 100 Trying\nVia: SIP/2.0/UDP pc33.atlanta.com;branch=z9hG4bKnashds8;\nTo: Bob <sip:bob@biloxi.com>\nFrom: Alice <sip:alice@atlanta.com>;tag=1928301774\nCall-ID: a84b4c76e66710\nCSeq: 314159 INVITE\nContent-Length: 0\r\n'

    # try:
    #     client_socket.send(message.encode('utf-8'))
    # except:
    #     send_message(data_fields["Via"]["received"], 8000, message)

    send_message(data_fields["Via"]["received"], 5060, message)


def ack(client_socket, data):
    return

def cancel(client_socket, data):
    return

def bye(client_socket, data):
    return

def response(client_socket, data):
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

