def register(client_socket, data):
    print("register...", data["From"])
    client_socket.send('200 OK'.encode('ascii'))

    # wait 200 OK or timer

def invite(client_socket, data):
    print("invite...", data["From"], 'to', data["To"])
    client_socket.send('100 Trying OK'.encode('ascii'))


def ack(client_socket, data):
    return

def cancel(client_socket, data):
    return

def bye(client_socket, data):
    return

methods = {}
methods["REGISTER"] = register
methods["INVITE"] = invite
methods["ACK"] = ack
methods["CANCEL"] = cancel
methods["BYE"] = bye
