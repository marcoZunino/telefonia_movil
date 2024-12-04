from datetime import datetime
import psycopg2


# DNS DATABASE FUNCTIONS ---------------------
dns_params = {
        'dbname': 'sip_proxy_dns',
        'user': 'postgres',
        'password': 'postgres',
        'host': '192.168.1.7',
        'port': '5434'
    }

def add_dns_entry(name, ip, listener_port):
    # Database connection parameters

    connection = None
    cursor = None
    
    try:
        # Connect to the database
        connection = psycopg2.connect(**dns_params)
        connection.set_client_encoding('UTF8')
        cursor = connection.cursor()

        # SQL query to insert a new row
        insert_query = '''
        INSERT INTO public.proxy (name, ip, listener_port) VALUES (%s, %s, %s) ON CONFLICT (name) DO UPDATE SET ip = EXCLUDED.ip, listener_port = EXCLUDED.listener_port; '''

        # Execute the query
        cursor.execute(insert_query, (name, ip, listener_port))

        # Commit the transaction
        connection.commit()
        print("DNS entry added successfully")

    except Exception as error:
        print("Failed to insert record into the DNS proxy table", error)

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def retrieve_proxy_data(name):
    # Database connection parameters

    connection = None
    cursor = None
    data = None

    try:
        # Connect to the database
        connection = psycopg2.connect(**dns_params)
        connection.set_client_encoding('UTF8')
        cursor = connection.cursor()

        # SQL query to insert a new row
        select_query = '''
        SELECT ip, listener_port
        FROM public.proxy
        WHERE name = %s;
        '''

        # Execute the query
        cursor.execute(select_query, (name,))
        data = cursor.fetchone()

    except Exception as error:
        print("Failed to retrieve data from the DNS proxy table", error)
        return None

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return data


# LOCATION SERVICE FUNCTIONS ---------------------

def add_user_to_sip_file(location_service, uri, contact, expires=3600):

    users = parse_sip_file(location_service)

    if any(user['URI'] == uri for user in users):
        modify_user_in_sip_file(location_service, uri, {"Contact": contact, "Expires": expires})
        return

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
                if uri and uri == user_info['URI']:
                    user_found = True
            
            elif line.strip().startswith("Contact:"):
                user_info['Contact'] = line.split("Contact:")[1].strip()
                try:
                    user_info['username'] = user_info['Contact'].split('@')[0].strip('<sip:')
                    user_info['IP'] = user_info['Contact'].split('@')[1].strip('>').split(':')[0]

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