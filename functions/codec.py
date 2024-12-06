import re

# decoding message to data 'JSON'
def decode(msg):
    data = {
                "Request" : {},
                "Fields" : {
                    "Via" : []
                }
            }
    
    msg = correct_msg(msg)
    
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
                    via_entry['protocol'] = via[0]
                    
                    if len(via[1].split(':')) == 2:
                        via_entry['uri'] = via[1].split(':')[0]
                        via_entry['port'] = via[1].split(':')[1]
                    else:
                        via_entry['uri'] = via[1]

                    for v in via[2:]:
                        v = v.split('=')
                        via_entry[v[0]] = v[1]

                    data["Fields"]["Via"].append(via_entry)
                else:
                    data["Fields"][key_value[0]] = key_value[1]

            try:
                data["Fields"]["Contact"] = data["Fields"]["Contact"].strip('<>')
            except:
                pass

            # print(line)
    # print('decoding ok')
    return data

    # print("head >", head)
    # for d in data:
    #     print(d, ">", data[d])

def correct_msg(msg):
    return msg.replace('\r\n\t', '').replace('\n\t', '').replace('\n    ', '').replace(' branch', 'branch')


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
    if not "received" in data["Fields"]["Via"][0]:
        data["Fields"]["Via"][0]['received'] = address
        # agregar IP a la primera entrada de Via

# poner IP en la uri del request
def update_to_proxy(data, client_ip):
    uri = data["Request"]["uri"].split('@')[0]
    data["Request"]["uri"] = uri + '@' + client_ip

def add_via_entry(data, via_entry):
    data["Fields"]["Via"].insert(0, via_entry)

def pop_via_entry(data):
    return data["Fields"]["Via"].pop(0)

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

        elif key == 'Contact':
            msg += key + ': <' + data["Fields"][key] + '>'

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
    msg = ""
    for v in via_array:
        msg += 'Via: '

        msg += v['protocol'] + ' '
        msg += v['uri']

        if 'port' in v:
            msg += ':' + v['port']
        
        msg += ';'

        for subkey in v:
            
            if subkey not in ['protocol', 'uri', 'port']:
                msg += subkey + '=' + v[subkey] + ';'

        if msg[-1] == ';':
            msg = msg[:-1]

        msg += '\n'
        
    return msg

    
# msg = "SIP/2.0 180 Ringing\r\nVia: SIP/2.0/UDP atlanta.com; branch=tLfqir65XOvhyA\n    ;received=10.252.60.83\r\nVia: SIP/2.0/UDP LAPTOP-HCN5E63L.atlanta.com; branch=YAHy4a3PGGICoY\r\n\t;received=10.252.62.239\r\nTo: cffuidio <sip:cffuidio@atlanta.com>; tag=515923\nFrom: Bob <sip:bob@atlanta.com>; tag=1\r\nCall-ID: 7jQ9XSyLimahFo\r\nContact: <sip:cffuidio@10.252.60.83>\r\nCSeq: 314159 INVITE\r\nContent-Length: 0\r\n"

# msg = ''.join(['S', 'I', 'P', '/', '2', '.', '0', ' ', '1', '8', '0', ' ', 'R', 'i', 'n', 'g', 'i', 'n', 'g', '\r', '\n', 'V', 'i', 'a', ':', ' ', 'S', 'I', 'P', '/', '2', '.', '0', '/', 'U', 'D', 'P', ' ', 'a', 't', 'l', 'a', 'n', 't', 'a', '.', 'c', 'o', 'm', ';', ' ', 'b', 'r', 'a', 'n', 'c', 'h', '=', 'j', '6', 'X', 'y', 'm', 'S', 'v', 'A', 'z', 'H', 'A', 'Q', 'G', 'L', '\n', ' ', ' ', ' ', ' ', ';', 'r', 'e', 'c', 'e', 'i', 'v', 'e', 'd', '=', '1', '0', '.', '2', '5', '2', '.', '6', '0', '.', '8', '3', '\r', '\n', 'V', 'i', 'a', ':', ' ', 'S', 'I', 'P', '/', '2', '.', '0', '/', 'U', 'D', 'P', ' ', 'L', 'A', 'P', 'T', 'O', 'P', '-', 'H', 'C', 'N', '5', 'E', '6', '3', 'L', '.', 'a', 't', 'l', 'a', 'n', 't', 'a', '.', 'c', 'o', 'm', ';', ' ', 'b', 'r', 'a', 'n', 'c', 'h', '=', 'h', 'T', 'X', 'q', 'Y', 'W', 'D', 'x', 'N', 'a', 'S', 'n', 'N', 'z', '\n', ' ', ' ', ' ', ' ', ';', 'r', 'e', 'c', 'e', 'i', 'v', 'e', 'd', '=', '1', '0', '.', '2', '5', '2', '.', '6', '2', '.', '2', '3', '9', '\r', '\n', 'T', 'o', ':', ' ', 'c', 'f', 'f', 'u', 'i', 'd', 'i', 'o', ' ', '<', 's', 'i', 'p', ':', 'c', 'f', 'f', 'u', 'i', 'd', 'i', 'o', '@', 'a', 't', 'l', 'a', 'n', 't', 'a', '.', 'c', 'o', 'm', '>', ';', ' ', 't', 'a', 'g', '=', '8', '1', '3', '3', '7', '9', '\n', 'F', 'r', 'o', 'm', ':', ' ', 'A', 'l', 'i', 'c', 'e', ' ', '<', 's', 'i', 'p', ':', 'a', 'l', 'i', 'c', 'e', '@', 'a', 't', 'l', 'a', 'n', 't', 'a', '.', 'c', 'o', 'm', '>', ';', ' ', 't', 'a', 'g', '=', '1', '\n', 'C', 'a', 'l', 'l', '-', 'I', 'D', ':', ' ', 'z', '2', 'E', 'j', 'Z', 'Q', 'f', 'F', 'g', 'Y', 'd', 'L', 'B', 'K', '\n', 'C', 'o', 'n', 't', 'a', 'c', 't', ':', ' ', '<', 's', 'i', 'p', ':', 'c', 'f', 'f', 'u', 'i', 'd', 'i', 'o', '@', '1', '0', '.', '2', '5', '2', '.', '6', '0', '.', '8', '3', '>', '\n', 'C', 'S', 'e', 'q', ':', ' ', '3', '1', '4', '1', '5', '9', ' ', 'I', 'N', 'V', 'I', 'T', 'E', '\n', 'C', 'o', 'n', 't', 'e', 'n', 't', '-', 'L', 'e', 'n', 'g', 't', 'h', ':', ' ', '0', '\n'])


# print([m for m in msg])
# print(msg)
# import json
# data = decode(msg)
# print(check_fields(data))
# print(json.dumps(data, indent=4))
# print(encode(data))

