import subprocess
import re
import datetime
import platform
import time

import psycopg2.extras
import socket

from ping3 import ping


def convert_to_snake_case(input_string):
    # Replace non-alphanumeric characters with underscores
    converted_string = re.sub(r'[^a-zA-Z0-9]+', '_', input_string)

    # Convert to lowercase
    converted_string = converted_string.lower()

    # Remove underscores from the beginning and end of the string
    converted_string = converted_string.strip('_')

    return converted_string


# def check_host_reachable(host):
#     port = 22
#     try:
#         # Create a socket object
#         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#
#         # Set a timeout for the connection attempt
#         sock.settimeout(10)
#
#         # Attempt to connect to the host on the specified port
#         sock.connect((host, port))
#
#         print(f"Host {host}:{port} is reachable.")
#     except (socket.timeout, ConnectionRefusedError):
#         print(f"Host {host}:{port} is not reachable.")
#     except Exception as e:
#         print(f"An error occurred {e}")
#         print(e)
#     finally:
#         # Close the socket
#         sock.close()
#     return f"IP address {host}"
#
# def ping_ip(ip_address, retry_count=2, max_attempts=1):
#     for attempt in range(1, max_attempts + 1):
#         try:
#             # Determine the appropriate option for the ping command based on the platform
#             # if platform.system() == "Windows":
#             #     ping_option = "-n"
#             # else:
#             ping_option = "-n"
#
#             # Execute the ping command
#             result = subprocess.run(['ping', ping_option, '4', ip_address], capture_output=True, text=True, timeout=10)
#
#             # Split the output into lines
#             lines = result.stdout.splitlines()
#             print(lines)
#
#             # Check if all packets were sent and received successfully
#             if len(lines) >= 5 and "100% packet loss" not in lines[-2]:
#                 return f"IP address {ip_address} is reachable on attempt {attempt}."
#             else:
#                 print(f"Attempt {attempt}: IP address {ip_address} is169.254.238.227 not reachable.")
#         except subprocess.TimeoutExpired:
#             print(f"Attempt {attempt}: Timed out while pinging IP address {ip_address}.")
#         except Exception as e:
#             print(f"An error occurred on attempt {attempt}: {e}")
#
#         if attempt < max_attempts:
#             print(f"Retrying IP address {ip_address}...")
#
#         return f"IP address {ip_address} is not reachable after {max_attempts} attempts."

def ping_eink(sources, destination):
    # destinations = [
    #     {"source": ["169.254.66.167", "169.254.66.209", "169.254.91.1"], "destination": "169.254.93.82"},
    #     {"source": ["169.254.66.167", "169.254.66.209", "169.254.91.1"], "destination": "169.254.199.140"},
    #     {"source": ["169.254.66.167", "169.254.66.209", "169.254.91.1"], "destination": "169.254.238.227"}
    # ]

    start_time = time.time()

    for dest_info in destination:
        for s_info in sources:
            source_ip = s_info
            destination_ip = dest_info

            if source_ip not in completed_sources:
                response_time = ping(destination_ip, src_addr=source_ip)

                if response_time is not None:
                    print(f"Ping response from {source_ip} to {destination_ip}: {response_time} ms")
                    if response_time > 0:
                        completed_sources.append(source_ip)
                else:
                    print(f"Ping failed from {source_ip} to {destination_ip}")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time elapsed for this loop iteration: {elapsed_time:.2f} seconds")
    return True


def clear_arp_cache():
    try:

        subprocess.run(["arp", "-d"], capture_output=True, text=True, shell=True)

        print("ARP cache cleared.")

    except Exception as e:

        print("Error:", e)


if __name__ == "__main__":
    clear_arp_cache()

    print("START TIME ")
    print(datetime.datetime.now())

    completed_process = subprocess.run("netsh interface show interface", shell=True, text=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE)
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
    print("ETH ADAPTER TIME ")
    print(datetime.datetime.now())
    for data_info in data:
        data_info['state'] = data_info['state']
        data_info['bb_status'] = "Down"
        data_info['subnet_prefix'] = ""
        data_info['gateway_metric'] = ""
        data_info['interface_metric'] = ""
        data_info['ipv4_address'] = ""

        adapter_name = data_info['interface_name']
        command = f'netsh interface ip show address "{adapter_name}" '

        # stdin, stdout, stderr = client.exec_command(command)
        # ipconfig_output = stdout.read().decode('utf-8')
        if data_info['state'] == "Connected":
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
            gateway_address_pattern = re.compile(r'Default Gateway:\s+(\d+\.\d+\.\d+\.\d+)')
            subnet_prefix_pattern = re.compile(r'Subnet Prefix:\s+(.*?)\n')
            gateway_metric_pattern = re.compile(r'Gateway Metric:\s+(.*?)\n')
            interface_metric_pattern = re.compile(r'InterfaceMetric:\s+(.*?)\n')

            match = ip_address_pattern.search(ipconfig_output)
            gateway_match = gateway_address_pattern.search(ipconfig_output)
            subnet_prefix_match = subnet_prefix_pattern.search(ipconfig_output)
            gateway_metric_match = gateway_metric_pattern.search(ipconfig_output)
            interface_metric_match  = interface_metric_pattern.search(ipconfig_output)
            if match:
                ipv4_address = match.group(1)
                data_info['ipv4_address'] = ipv4_address
                # ipv4_address_split = ipv4_address.split(".")

            if gateway_match:
                gateway_address = gateway_match.group(1)
                if "169.254.2.2" == gateway_address:
                    data_info['bb_status'] = "Up"

            if subnet_prefix_match:
                subnet_prefix = subnet_prefix_match.group(1)
                data_info['subnet_prefix'] = subnet_prefix

            if gateway_metric_match:
                gateway_metric = gateway_metric_match.group(1)
                data_info['gateway_metric'] = gateway_metric

            if interface_metric_match:
                interface_metric = interface_metric_match.group(1)
                data_info['interface_metric'] = interface_metric

    print(data)

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
        truncate_query = "TRUNCATE TABLE bb_info;"
        cursor.execute(truncate_query)

        data_insert_values = []
        for eth_info in data:
            # Values to insert
            values = {
                'eth': eth_info['interface_name'],
                'state': eth_info['state'],
                'update_time': datetime.datetime.now(),
                'bb_status': eth_info['bb_status'],
                'ip_address': eth_info['ipv4_address'],
                'subnet_mask': eth_info['subnet_prefix'],
                'gateway_metric': eth_info['gateway_metric'],
                'interface_metric': eth_info['interface_metric']
            }
            data_insert_values.append(values)

            # Example data to be inserted
            # data_to_insert = [(eth_info['interface_name'],  eth_info['admin_state'], datetime.datetime.now(), eth_info['port_eink_ip'] if eth_info['port_eink_ip'] else "N/A", eth_info['port_eink_mac_id'] if eth_info['port_eink_mac_id'] else "N/A")]

        # SQL query for insertion
        insert_query = "INSERT INTO bb_info (eth, state, update_time, bb_status, ip_address, subnet_mask, gateway_metric, interface_metric) VALUES (%(eth)s, %(state)s, %(update_time)s, %(bb_status)s, %(ip_address)s, %(subnet_mask)s, %(gateway_metric)s, %(interface_metric)s);"
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
