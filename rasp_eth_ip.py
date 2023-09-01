import subprocess
import re
import datetime

import psycopg2.extras

def convert_to_snake_case(input_string):
    # Replace non-alphanumeric characters with underscores
    converted_string = re.sub(r'[^a-zA-Z0-9]+', '_', input_string)

    # Convert to lowercase
    converted_string = converted_string.lower()

    # Remove underscores from the beginning and end of the string
    converted_string = converted_string.strip('_')

    return converted_string


if __name__ == "__main__":
    print("START TIME ")
    print(datetime.datetime.now())
    completed_process = subprocess.run("netsh interface show interface", shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Get the output and error as strings
    output = completed_process.stdout
    error = completed_process.stderr
    # print("Remote script output:")
    # print(output)
    # print("Remote script error:")
    # print(error)

    lines = output.strip().split('\n')
    header_line = lines[0]
    data_lines = lines[2:]

    columns = [convert_to_snake_case(column.strip()) for column in re.split(r'\s{2,}', header_line)]
    data = []

    for line in data_lines:
        values = [value.strip() for value in re.split(r'\s{2,}', line)]
        entry = {columns[i]: values[i] for i in range(len(columns))}
        data.append(entry)

    # print(data)

    for data_info in data:
        data_info['port_purple_box_ip'] = "none"
        data_info['port_eink_ip'] = "none"
        data_info['port_eink_mac_id'] = "none"
        adapter_name = data_info['interface_name']
        command = f'netsh interface ip show address "{adapter_name}" '

        # stdin, stdout, stderr = client.exec_command(command)
        # ipconfig_output = stdout.read().decode('utf-8')

        ipconfig_process = subprocess.run(command, shell=True, text=True,
                                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Get the output and error as strings
        ipconfig_output = ipconfig_process.stdout
        ipconfig_error = ipconfig_process.stderr
        # print("ipconfig_output script output:")
        # print(ipconfig_output)
        # print("ipconfig_output script error:")
        # print(ipconfig_error)

        ip_address_pattern = re.compile(r'IP Address:\s+(\d+\.\d+\.\d+\.\d+)')
        match = ip_address_pattern.search(ipconfig_output)
        if match:
            ipv4_address = match.group(1)
            data_info['port_purple_box_ip'] = ipv4_address
            ipv4_address_split = ipv4_address.split(".")

            eink_command = f'arp -a '
            # eink_command = f'arp -a '

            # stdin, stdout, stderr = client.exec_command(command)
            # eink_output = stdout.read().decode('utf-8')

            # eink_process = subprocess.run(eink_command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            eink_process = subprocess.run(['arp', '-a', adapter_name], capture_output=True, text=True)
            # Get the output and error as strings
            eink_output = eink_process.stdout
            eink_error = eink_process.stderr
            # print("eink_output script output:")
            # print(eink_output)
            # print("eink_output script error:")
            # print(eink_error)

            # Regular expression pattern to match the block of data for "Interface: 169.254.173.31"
            pattern = re.compile(
                rf"Interface: {ipv4_address_split[0]}\.{ipv4_address_split[1]}\.{ipv4_address_split[2]}\.{ipv4_address_split[3]}\s+(.*?)\s+(?=Interface:|\Z)",
                re.DOTALL)

            # Search for the pattern in the input data
            match = pattern.search(eink_output)

            address_prefixes = ["28-cd-c1", "b8-27-eb", "dc-26-32", "e4-5f-01"]

            if match:
                matched_block = match.group(1)
                lines = matched_block.strip().split('\n')
                for line in lines[1:]:
                    # print(line)
                    if "dynamic" in line.lower() and any(prefix in line.lower() for prefix in address_prefixes):
                        values = [value.strip() for value in re.split(r'\s{2,}', line)]
                        # print(values)
                        data_info['port_eink_ip'] = values[1]
                        data_info['port_eink_mac_id'] = values[2]

    print(data)

    # Connect to the database
    try:
        dbname = 'bot360'
        user = 'postgres'
        password ='postgresbot360'
        host = 'bot360-purplebox-dev.cqblstrpdwe8.us-east-2.rds.amazonaws.com'
        port = '5432'
        connection = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        cursor = connection.cursor()

        # Truncate the table
        truncate_query = "TRUNCATE TABLE ethernet_info;"
        cursor.execute(truncate_query)

        data_insert_values = []
        for eth_info in data:
            # Values to insert
            values = {
                'eth': eth_info['interface_name'],
                'status': eth_info['state'],
                'update_time': datetime.datetime.now(),
                'ip_address': eth_info['port_eink_ip'],
                'mac_address': eth_info['port_eink_mac_id'],
                'combination': ''
            }
            data_insert_values.append(values)

            # Example data to be inserted
            # data_to_insert = [(eth_info['interface_name'],  eth_info['admin_state'], datetime.datetime.now(), eth_info['port_eink_ip'] if eth_info['port_eink_ip'] else "N/A", eth_info['port_eink_mac_id'] if eth_info['port_eink_mac_id'] else "N/A")]

        # SQL query for insertion
        insert_query = "INSERT INTO ethernet_info (eth, status, update_time, ip_address, mac_address, combination) VALUES (%(eth)s, %(status)s, %(update_time)s, %(ip_address)s, %(mac_address)s, %(combination)s);"
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

