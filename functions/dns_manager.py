import psycopg2

# DNS DATABASE FUNCTIONS ---------------------
dns_params = {
        'dbname': 'sip_proxy_dns',
        'user': 'postgres',
        'password': 'postgres',
        'host': '10.252.62.239',
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
