import socket

def send_message(host, port, message):
    # Create a socket object
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to the listener socket
        client_socket.connect((host, port))
        
        # Send the message encoded in UTF-8
        client_socket.send(message.encode('utf-8'))
        
        print(f"Message sent to {host}:{port}")
    
    except Exception as e:
        print(f"Failed to send message: {e}")
    
    finally:
        # Close the socket connection
        client_socket.close()

# Define the host, port, and message
host = '192.168.0.207'  # Replace with the listener's IP address
port = 8000  # Replace with the listener's port number
message = 'REGISTER sip:bob@biloxi.com SIP/2.0\nVia: SIP/2.0/UDP pc33.atlanta.com;branch=z9hG4bK776asdhds\nMax-Forwards: 70\nTo: Bob <sip:bob@biloxi.com>\nFrom: Alice <sip:alice@atlanta.com>;tag=1928301774\nCall-ID: a84b4c76e66710@pc33.atlanta.com\nCSeq: 314159 INVITE\nContact: <sip:alice@pc33.atlanta.com>\nContent-Type: application/sdp\nContent-Length: 142\r\n'

# Send the message
send_message(host, port, message)
