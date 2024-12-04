from datetime import datetime

# LOCATION SERVICE FUNCTIONS ---------------------

def ls_proxy(proxy_name):
    return f'databases/location_service_{proxy_name}.txt'

def add_user_to_sip_file(location_service, uri, contact, expires=3600):

    try:
        users = parse_sip_file(location_service)

        if any(user['URI'] == uri for user in users):
            modify_user_in_sip_file(location_service, uri, {"Contact": contact, "Expires": expires})
            return
    
    except:
        pass

    with open(location_service, 'a') as file:

        file.write("\n[User]\n")
        file.write(f"URI: {uri}\n")
        file.write(f"Contact: {contact}\n")
        file.write(f"Expires: {expires}\n")

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

def modify_user_in_sip_file(location_service, uri, new_params):

    for p in new_params:

        with open(location_service, 'r') as file:
            lines = file.readlines()

        with open(location_service, 'w') as file:

            user_found = False
            for line in lines:

                if line.strip().startswith("URI:") and uri in line:
                    user_found = True

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
                user_info['URI'] = line.split("URI:")[1].strip()
                user_info['port'] = int(user_info['URI'].split(':')[1])
                user_info['URI'] = user_info['URI'].split(':')[0]
                if uri and uri == user_info['URI']:
                    user_found = True
            
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


# LOGS
def update_log(log_file, msg):
    with open(log_file, 'a') as log_file:
        log_file.write(f'{datetime.now()}\n{msg}\n\n')    # guardar mensaje en log




# import requests

# # URL of the remote file
# url = 'https://drive.google.com/file/d/1gkzzGppYdSMRfRILeSY-xBOLWRB1FFiF/view?usp=drive_link'

# # Fetch the content of the remote file
# response = requests.get(url)

# # Check if the request was successful
# if response.status_code == 200:
#     # Get the content of the file
#     file_content = response.text
    
#     # Process the content as needed
#     print(file_content)
# else:
#     print(f"Failed to fetch the file. Status code: {response.status_code}")

# print(query_location_service('databases/location_service.txt', username='bob', proxy_name='personal.ar'))
