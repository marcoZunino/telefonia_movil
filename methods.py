from send import send_message


def register(client_socket, data):
    data_fields = data["Fields"]
    print("register...", data_fields["From"])
    # client_socket.send('200 OK'.encode('ascii'))

    message = 'SIP/2.0 200 OK\nVia: SIP/2.0/UDP server10.biloxi.com;branch=z9hG4bKnashds8;received=192.0.2.3\nTo: Bob <sip:bob@biloxi.com>;tag=a6c85cf\nFrom: Alice <sip:alice@atlanta.com>;tag=1928301774\nCall-ID: a84b4c76e66710@pc33.atlanta.com\nCSeq: 314159 INVITE\nContact: <sip:bob@192.0.2.4>\nContent-Type: application/sdp\nContent-Length: 131'
    send_message('192.168.0.207', 8000, message)


    # wait 200 OK or timer

def invite(client_socket, data):
    data_fields = data["Fields"]
    print("invite...", data_fields["From"], 'to', data_fields["To"])
    client_socket.send('100 Trying OK'.encode('ascii'))


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
