# import re

# msg = 'REGISTER sip:registrar.claseTelefonia.com SIP/2.0\r\nVia: SIP/2.0/TCP 127.0.1.1:8080;branch=z9hG4bK12345678\r\nMax-Forwards: 70\r\nFrom: "Thomas" <sip:elProfe@claseTelefonia.com>;tag=77772\r\nTo: "Thomas" <sip:elProfe@claseTelefonia.com>\r\nCall-ID: a84b4c76e66710@127.0.1.1\r\nCSeq: 1 REGISTER\r\nContact: "Thomas" <sip:elProfe@127.0.1.1>\r\nExpires: 3600\r\nContent-Length: 0\r\n\r\n'


def decode(msg):
    data = {}
    
    # for line in re.split(r'[\r\n]', msg):
    for l in msg.split('\r\n'): # CAMBIAR POR '\r\n'
        for line in l.split('\n'):

            key_value = line.split(': ')
            if len(key_value) == 1 and key_value[0] != '':
                data["Request"] = request_decode(key_value[0])
            if len(key_value) > 1:
                data[key_value[0]] = key_value[1]

            # print(line)
    # print('decoding ok')
    return data

    # print("head >", head)
    # for d in data:
    #     print(d, ">", data[d])

def check_fields(data):
    keys = data.keys()
    return 'Via' in keys and 'Max-Forwards' in keys and 'From' in keys and 'To' in keys and 'Call-ID' in keys and 'CSeq' in keys

def request_decode(req):
    r = req.split(' ')
    request = {}

    if r[0] == 'SIP/2.0':
        request["Method"] = "response"
    else:
        request["Method"] = r[0]
        request["uri"] = r[1]

    return request
                



# data = decode(msg)
# for d in data:
#     print(d, ">", data[d])

# print(check_fields(data))
    