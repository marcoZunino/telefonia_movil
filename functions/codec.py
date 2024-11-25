import re


def decode(msg):
    data = {
                "Request" : {},
                "Fields" : {
                    "Via" : {}
                }
            }
    
    # for line in re.split(r'[\r\n]', msg):
    for l in msg.split('\r\n'):
        for line in l.split('\n'):

            key_value = line.split(': ')
            
            if len(key_value) == 1 and key_value[0] != '':
                data["Request"] = request_decode(key_value[0])
            if len(key_value) > 1:
                if key_value[0] == 'Via':
                    via = re.split(r'[ ;]', key_value[1])
                    data["Fields"]["Via"]["protocol"] = via[0]
                    data["Fields"]["Via"]["uri"] = via[1]
                    for v in via[2:]:
                        v = v.split('=')
                        data["Fields"]["Via"][v[0]] = v[1]
                else:
                    data["Fields"][key_value[0]] = key_value[1]

            # print(line)
    # print('decoding ok')
    return data

    # print("head >", head)
    # for d in data:
    #     print(d, ">", data[d])

def add_received_IP(data, address):

    data["Fields"]["Via"]["received"] = address


def encode(data):

    msg = ""

    request = data["Request"]

    if request["Method"] == "Response":
        msg += 'SIP/2.0' + ' ' + request["Response Code"] + ' ' + request["Response Description"] + '\n'
    else:
        msg += request["Method"] + ' ' + request["uri"] + ' ' + 'SIP/2.0' + '\n'
    
    for key in data["Fields"]:
        msg += key + ': '
        if key == 'Via':
            for subkey in data["Fields"][key]:
                if subkey == 'protocol':
                    msg += key + ': ' + data["Fields"][key][subkey] + ' '
                elif subkey == 'uri':
                    msg += data["Fields"][key][subkey] + ';'
                else:
                    msg += subkey + '=' + data["Fields"][key][subkey] + ';'
        else:
            msg += data["Fields"][key]

        msg += '\n'
        

    msg = msg[:-1]
    msg += '\r\n'

    return msg



def check_fields(data):
    keys = data.keys()
    return 'Via' in keys and 'Max-Forwards' in keys and 'From' in keys and 'To' in keys and 'Call-ID' in keys and 'CSeq' in keys

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
                

# msg = 'REGISTER sip:bob@biloxi.com SIP/2.0\nVia: SIP/2.0/UDP pc33.atlanta.com;branch=z9hG4bK776asdhds\nMax-Forwards: 70\nTo: Bob <sip:bob@biloxi.com>\nFrom: Alice <sip:alice@atlanta.com>;tag=1928301774\nCall-ID: a84b4c76e66710@pc33.atlanta.com\nCSeq: 314159 INVITE\nContact: <sip:alice@pc33.atlanta.com>\nContent-Type: application/sdp\nContent-Length: 142\r\n'

# msg = 'REGISTER sip:registrar.claseTelefonia.com SIP/2.0\r\nVia: SIP/2.0/TCP 127.0.1.1:8080;branch=z9hG4bK12345678\r\nMax-Forwards: 70\r\nFrom: "Thomas" <sip:elProfe@claseTelefonia.com>;tag=77772\r\nTo: "Thomas" <sip:elProfe@claseTelefonia.com>\r\nCall-ID: a84b4c76e66710@127.0.1.1\r\nCSeq: 1 REGISTER\r\nContact: "Thomas" <sip:elProfe@127.0.1.1>\r\nExpires: 3600\r\nContent-Length: 0\r\n'

# msg = 'SIP/2.0 200 OK\nVia: SIP/2.0/UDP server10.biloxi.com;branch=z9hG4bKnashds8;received=192.0.2.3\nTo: Bob <sip:bob@biloxi.com>;tag=a6c85cf\nFrom: Alice <sip:alice@atlanta.com>;tag=1928301774\nCall-ID: a84b4c76e66710@pc33.atlanta.com\nCSeq: 314159 INVITE\nContact: <sip:bob@192.0.2.4>\nContent-Type: application/sdp\nContent-Length: 131\r\n'

# msg = "INVITE sip:bob@biloxi.com SIP/2.0\nVia: SIP/2.0/UDP pc33.atlanta.com;branch=z9hG4bKnashds8\nTo: Bob <sip:bob@biloxi.com>\nFrom: Alice <sip:alice@atlanta.com>;tag=1928301774\nCall-ID: a84b4c76e66710\nCSeq: 314159 INVITE\nMax-Forwards: 70\nContact: <sip:alice@pc33.atlanta.com>\nContent-Type: application/pkcs7-mime; smime-type=enveloped-data;name=smime.p7m\nContent-Disposition: attachment; filename=smime.p7m;handling=required\r\n"
# import json

# data = decode(msg)
# add_received_IP(data, "192.168.0.207")
# print(json.dumps(data, indent=4))
# print(encode(data))
# print(msg)
    