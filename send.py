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


