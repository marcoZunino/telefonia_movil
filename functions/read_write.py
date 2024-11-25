

def add_user_to_sip_file(location_service, uri, contact, expires=3600):

    with open(location_service, 'a') as file:

        file.write("\n[User]\n")
        file.write(f"URI: {uri}\n")
        file.write(f"Contact: {contact}\n")
        file.write(f"Expires: {expires}\n")


def parse_sip_file(location_service):

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


def modify_user_in_sip_file(location_service, uri, parameter, new_value):

    with open(location_service, 'r') as file:
        lines = file.readlines()

    with open(location_service, 'w') as file:
        user_found = False

        for line in lines:

            if line.strip().startswith("URI:") and uri in line:
                user_found = True

            if user_found and line.strip().startswith(parameter):
                line = f"{parameter}: {new_value}\n"
                user_found = False # Reset after modification
                
            file.write(line)

def query_location_server(file_path, uri):

    with open(file_path, 'r') as file:
        user_info = {}
        user_found = False

        for line in file:
            
            if line.strip().startswith("URI:") and uri in line:
                user_found = True
                user_info['URI'] = line.split("URI:")[1].strip()

            elif user_found and line.strip().startswith("Contact:"):
                user_info['Contact'] = line.split("Contact:")[1].strip()

            elif user_found and line.strip().startswith("Expires:"):
                user_info['Expires'] = line.split("Expires:")[1].strip()
                break # Exit after finding all relevant information

    return user_info

def update_log(log_file, msg):
    with open(log_file, 'a') as log_file:
        log_file.write(msg + '\n\n')    # guardar mensaje en log

