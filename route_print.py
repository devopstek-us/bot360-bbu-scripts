import subprocess
import re
import datetime
import platform
import time

import psycopg2.extras
import socket

from ping3 import ping

if __name__ == "__main__":
    print("START TIME ")
    print(datetime.datetime.now())

    completed_process = subprocess.run("route PRINT", shell=True, text=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
    # Get the output and error as strings
    output = completed_process.stdout
    error = completed_process.stderr
    # print("Remote script output:")
    # print(output)
    # print("Remote script error:")
    # print(error)

    # Connect to the database
    try:
        dbname = 'bot360'
        user = 'postgres'
        password = 'postgresbot360'
        host = 'bot360-purplebox-dev.cqblstrpdwe8.us-east-2.rds.amazonaws.com'
        port = '5432'
        connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor = connection.cursor()

        # Truncate the table
        truncate_query = "TRUNCATE TABLE route_data;"
        cursor.execute(truncate_query)

        data_insert_values = []

        # Values to insert
        values = {
            'id': 1,
            'log': output,
            'update_time': datetime.datetime.now()
        }
        data_insert_values.append(values)

        # Example data to be inserted
        # data_to_insert = [(eth_info['interface_name'],  eth_info['admin_state'], datetime.datetime.now(), eth_info['port_eink_ip'] if eth_info['port_eink_ip'] else "N/A", eth_info['port_eink_mac_id'] if eth_info['port_eink_mac_id'] else "N/A")]

        # SQL query for insertion
        insert_query = "INSERT INTO route_data (id, log, update_time) VALUES (%(id)s, %(log)s, %(update_time)s);"
        # Insert data using a loop
        for record in data_insert_values:
            cursor.execute(insert_query, record)

        # Commit the changes
        connection.commit()

        print("Data inserted successfully!")
        print("END TIME ")
        print(datetime.datetime.now())
    except psycopg2.Error as e:
        print("Error:", e)

    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()
