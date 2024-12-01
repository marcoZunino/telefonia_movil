from functions.read_write import add_proxy_entry

name = 'proxy4'
ip = '192.168.1.4'
listener_port = 8080

add_proxy_entry(name, ip, listener_port)