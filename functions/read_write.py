from datetime import datetime

from functions.dns_manager import retrieve_all_proxys

# LOCATION SERVICE FUNCTIONS ---------------------

def ls_proxy(proxy_name):
    return f'location_services/ls_{proxy_name}.txt'

def add_user_to_sip_file(location_service, uri, port, contact, expires=3600):

    users = parse_sip_file(location_service)

    name_uri = f'{contact.split('@')[0].split(':')[1]}@{uri}' # username@uri

    if any(user['URI'].split(':')[0] == name_uri for user in users):
        modify_user_in_sip_file(location_service, name_uri, port, {"Contact": contact, "Expires": expires})
        print("...updating user data", name_uri)
        return

    with open(location_service, 'a') as file:

        file.write("\n[User]\n")
        file.write(f"URI: {name_uri}:{port}\n")
        file.write(f"Contact: {contact}\n")
        file.write(f"Expires: {expires}\n")

    print("new user registered:", name_uri)

def parse_sip_file(location_service):

    try:
        with open(location_service, 'r') as file:
            users = []
            user = {}

            for line in file:

                line = line.strip()
                if line.startswith("[User]"):
                    if user:
                        users.append(user)
                        user = {}

                elif line.startswith("URI:"):
                    user['URI'] = line.split("URI:")[1].strip()

                elif line.startswith("Contact:"):
                    user['Contact'] = line.split("Contact:")[1].strip()

                elif line.startswith("Expires:"):
                    user['Expires'] = line.split("Expires:")[1].strip()

            if user:
                users.append(user)

        return users
    
    except:
        return []

def modify_user_in_sip_file(location_service, name_uri, port, new_params):

    for p in new_params:

        with open(location_service, 'r') as file:
            lines = file.readlines()

        with open(location_service, 'w') as file:

            user_found = False
            for line in lines:

                if line.strip().startswith("URI:"):
                    if name_uri == line.split("URI:")[1].strip().split(':')[0]:
                        user_found = True
                        line = f"URI: {name_uri}:{port}\n"

                if user_found and line.strip().startswith(p):
                    line = f"{p}: {new_params[p]}\n"
                    user_found = False # Reset after modification
                                    
                file.write(line)

def query_location_service(file_path, uri=None, username=None, proxy_name=None):

    with open(file_path, 'r') as file:
        user_info = {}
        user_found = False

        for line in file:
            
            if line.strip().startswith("URI:"):

                user_info['URI'] = line.split("URI:")[1].strip()       # name@uri:port
                user_info['port'] = int(user_info['URI'].split(':')[1]) # port
                user_info['username'] = user_info['URI'].split(':')[0].split('@')[0]    # name
                user_info['URI'] = user_info['URI'].split(':')[0].split('@')[1]     # uri

                if uri and uri == user_info['URI']:
                    user_found = True
                    if username and username != user_info['username']:
                        user_found = False
            
            elif line.strip().startswith("Contact:"):
                user_info['Contact'] = line.split("Contact:")[1].strip()
                try:
                    user_info['username'] = user_info['Contact'].split('@')[0].strip('sip:')
                    user_info['IP'] = user_info['Contact'].split('@')[1]

                    if username and username == user_info['username']:
                        user_found = True
                        if proxy_name:
                            if proxy_name not in user_info['URI']:
                                user_found = False
                except:
                    continue

            elif line.strip().startswith("Expires:"):
                user_info['Expires'] = line.split("Expires:")[1].strip()
                
                if user_found:
                    break # Exit after finding all relevant information
                else:
                    user_info = {}

    return user_info

def search_port(data, proxy_data = None, username = None):

    if not username:
        username=data["Fields"]["From"].split(' ')[0].lower()

    dest_port = None

    try:
        # buscar si es cliente
        dest_port = query_location_service(ls_proxy(proxy_data["name"]),
                                           uri=data["Fields"]["Via"][0]['uri'],
                                           username=username
                                           )["port"]
    except:
        # buscar si es proxy
        for p in retrieve_all_proxys():
            if p["name"] in data["Fields"]["Via"][0]['uri']:
                dest_port = p["address"][1]
                break
        
    if not dest_port:
        print("Destination port not found", data["Fields"]["Via"][0])
    
    return dest_port

# LOGS
def update_log(log_file, msg):
    with open(log_file, 'a') as log_file:
        log_file.write(f'{datetime.now()}\n{msg}\n\n')    # guardar mensaje en log

