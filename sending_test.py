from functions.send import send_message

# Define the host, port, and message
host = '192.168.0.191'  # Replace with the listener's IP address
port = 8000  # Replace with the listener's port number
# message = 'REGISTER sip:bob@biloxi.com SIP/2.0\nVia: SIP/2.0/UDP pc33.atlanta.com;branch=z9hG4bK776asdhds\nMax-Forwards: 70\nTo: Bob <sip:bob@biloxi.com>\nFrom: Alice <sip:alice@atlanta.com>;tag=1928301774\nCall-ID: a84b4c76e66710@pc33.atlanta.com\nCSeq: 314159 INVITE\nContact: <sip:alice@pc33.atlanta.com>\nContent-Type: application/sdp\nContent-Length: 142\r\n'

message = "REGISTER sip:registrar.biloxi.com SIP/2.0\nVia: SIP/2.0/UDP bobspc.biloxi.com:5060;branch=z9hG4bKnashds7\nMax-Forwards: 70\nTo: Bob <sip:bob@biloxi.com>\nFrom: Bob <sip:bob@biloxi.com>;tag=456248\nCall-ID: 843817637684230@998sdasdh09\nCSeq: 1826 REGISTER\nContact: <sip:bob@192.0.2.4>\nExpires: 7200\nContent-Length: 0\r\n"

# Send the message
send_message(host, port, message)