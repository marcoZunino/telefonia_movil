import re

# decoding message to data 'JSON'
def decode(msg):
    data = {
                "Request" : {},
                "Fields" : {
                    "Via" : []
                }
            }
    
    # for line in re.split(r'[\r\n]', msg):
    for l in msg.split('\r\n'):
        for line in l.split('\n'):

            key_value = line.split(': ')
            
            # primera linea: decodificar request
            if len(key_value) == 1 and key_value[0] != '':
                data["Request"] = request_decode(key_value[0])

            # decodificar campos
            if len(key_value) > 1:

                if key_value[0] == 'Via':
                    # separar value por ' ' y ';'
                    via = re.split(r'[ ;]', key_value[1])

                    via_entry = {}
                    via_entry["protocol"] = via[0]
                    via_entry["uri"] = via[1]
                    for v in via[2:]:
                        v = v.split('=')
                        via_entry[v[0]] = v[1]

                    data["Fields"]["Via"].append(via_entry)
                else:
                    data["Fields"][key_value[0]] = key_value[1]

            # print(line)
    # print('decoding ok')
    return data

    # print("head >", head)
    # for d in data:
    #     print(d, ">", data[d])

# decode message as request or response
def request_decode(req):
    r = req.split(' ')
    request = {}

    if r[0] == 'SIP/2.0':
        request["Method"] = "Response"
        request["Response Code"] = r[1]
        request["Response Description"] = r[2]

    else:
        request["Method"] = r[0]
        request["uri"] = r[1]

    return request

# check if message has all the required fields
def check_fields(data):
    keys = data["Fields"].keys()
    if data["Request"]["Method"] == "Response":
        return 'Via' in keys and 'From' in keys and 'To' in keys and 'Call-ID' in keys and 'CSeq' in keys
    else:
        return 'Via' in keys and 'Max-Forwards' in keys and 'From' in keys and 'To' in keys and 'Call-ID' in keys and 'CSeq' in keys


def add_received_IP(data, address):
    data["Fields"]["Via"][0]["received"] = address
    # agregar IP a la primera entrada de Via

# poner IP en la uri del request
def update_to_proxy(data, client_ip):
    uri = data["Request"]["uri"].split('@')[0]
    data["Request"]["uri"] = uri + '@' + client_ip

def add_via_entry(data, via_entry):
    data["Fields"]["Via"].insert(0, via_entry)

# encode data 'JSON' to message
def encode(data):

    msg = ""

    request = data["Request"]

    if request["Method"] == "Response":
        msg += 'SIP/2.0' + ' ' + request["Response Code"] + ' ' + request["Response Description"] + '\n'
    else:
        msg += request["Method"] + ' ' + request["uri"] + ' ' + 'SIP/2.0' + '\n'
    
    for key in data["Fields"]:

        if key == 'Via':
            msg += encode_via(data["Fields"]["Via"])

        else:
            msg += key + ': ' + data["Fields"][key]
        
        if msg[-1] == ';':
            msg = msg[:-1]
        if msg[-1] != '\n':
            msg += '\n'
        
    msg = msg[:-1]
    msg += '\r\n'

    return msg

def encode_via(via_array):
    for v in via_array:
        msg += 'Via: '
        for subkey in v:
            if subkey == 'protocol':
                msg += v["protocol"] + ' '
            elif subkey == 'uri':
                msg += v["uri"] + ';'
            else:
                msg += subkey + '=' + v[subkey] + ';'
        if msg[-1] == ';':
            msg = msg[:-1]
        msg += '\n'


    

# msg = 'REGISTER sip:bob@biloxi.com SIP/2.0\nVia: SIP/2.0/UDP pc33.atlanta.com;branch=z9hG4bK776asdhds\nMax-Forwards: 70\nTo: Bob <sip:bob@biloxi.com>\nFrom: Alice <sip:alice@atlanta.com>;tag=1928301774\nCall-ID: a84b4c76e66710@pc33.atlanta.com\nCSeq: 314159 INVITE\nContact: <sip:alice@pc33.atlanta.com>\nContent-Type: application/sdp\nContent-Length: 142\r\n'

# msg = 'REGISTER sip:registrar.claseTelefonia.com SIP/2.0\r\nVia: SIP/2.0/TCP 127.0.1.1:8080;branch=z9hG4bK12345678\r\nMax-Forwards: 70\r\nFrom: "Thomas" <sip:elProfe@claseTelefonia.com>;tag=77772\r\nTo: "Thomas" <sip:elProfe@claseTelefonia.com>\r\nCall-ID: a84b4c76e66710@127.0.1.1\r\nCSeq: 1 REGISTER\r\nContact: "Thomas" <sip:elProfe@127.0.1.1>\r\nExpires: 3600\r\nContent-Length: 0\r\n'

# msg = 'SIP/2.0 200 OK\nVia: SIP/2.0/UDP server10.biloxi.com;branch=z9hG4bKnashds8;received=192.0.2.3\nTo: Bob <sip:bob@biloxi.com>;tag=a6c85cf\nFrom: Alice <sip:alice@atlanta.com>;tag=1928301774\nCall-ID: a84b4c76e66710@pc33.atlanta.com\nCSeq: 314159 INVITE\nContact: <sip:bob@192.0.2.4>\nContent-Type: application/sdp\nContent-Length: 131\r\n'

# msg = "INVITE sip:bob@biloxi.com SIP/2.0\nVia: SIP/2.0/UDP pc33.atlanta.com;branch=z9hG4bKnashds8\nTo: Bob <sip:bob@biloxi.com>\nFrom: Alice <sip:alice@atlanta.com>;tag=1928301774\nCall-ID: a84b4c76e66710\nCSeq: 314159 INVITE\nMax-Forwards: 70\nContact: <sip:alice@pc33.atlanta.com>\nContent-Type: application/pkcs7-mime; smime-type=enveloped-data;name=smime.p7m\nContent-Disposition: attachment; filename=smime.p7m;handling=required\r\n"


# msg = "SIP/2.0 100 Trying\nVia: SIP/2.0/UDP pc33.atlanta.com;branch=z9hG4bKnashds8;received=192.0.2.1\nTo: Bob <sip:bob@biloxi.com>\nFrom: Alice <sip:alice@atlanta.com>;tag=1928301774\nCall-ID: a84b4c76e66710\nCSeq: 314159 INVITE\nContent-Length: 0"


# msg = "SIP/2.0 200 OK\nVia: SIP/2.0/UDP pc33.atlanta.com;branch=z9hG4bKnashds8\nTo: Bob <sip:bob@claro.uy>\nFrom: Bob <sip:bob@claro.uy>;tag=456248\nCall-ID: 843817637684230@998sdasdh09\nCSeq: 1826 REGISTER\nContent-Length: 0"

# msg = "INVITE sip:bob@claro.uy SIP/2.0\nVia: SIP/2.0/UDP bobspc.biloxi.com;branch=z9hG4bK776asdhds\nMax-Forwards: 70\nTo: bob@claro.uy <sip:bob@claro.uy>\nFrom: Bob <sip:bob@claro.uy>;tag=1928301774\nCall-ID: a84b4c76e66710@pc33.atlanta.com\nCSeq: 314159 INVITE\nContact: <sip:bob@192.168.1.7>\nContent-Type: application/sdp\nContent-Length: 142"

# msg = "SIP/2.0 180 Ringing\nVia: SIP/2.0/UDP server10.biloxi.com;branch=z9hG4bK4b43c2ff8.1;received=192.0.2.3\nVia: SIP/2.0/UDP bigbox3.site3.atlanta.com;branch=z9hG4bK77ef4c2312983.1;received=192.0.2.2\nVia: SIP/2.0/UDP pc33.atlanta.com;branch=z9hG4bKnashds8;received=192.0.2.1\nTo: Bob <sip:bob@biloxi.com>;tag=a6c85cf\nFrom: Alice <sip:alice@atlanta.com>;tag=1928301774\nCall-ID: a84b4c76e66710\nContact: <sip:bob@192.0.2.4>\nCSeq: 314159 INVITE\nContent-Length: 0"


# import json


# data = decode(msg)
# add_received_IP(data, '192.168.10.10')

# print(check_fields(data))

# add_via_entry(data, {
#     "protocol": "SIP/2.0",
#     "uri": "server10.biloxi.com",
#     "branch": "z9hG4bK4b43c2ff8.1",
#     })


# print(json.dumps(data, indent=4))

# print(encode(data))
