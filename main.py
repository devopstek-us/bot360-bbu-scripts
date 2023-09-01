import subprocess
import json
import socket

import requests


def get_ethernet_details():
    command = [
        "powershell",
        "-Command",
        "Get-NetAdapter | Where-Object { $_.InterfaceDescription -like '*Ethernet*' } | Select-Object Name, MacAddress, Status | ConvertTo-Json"
    ]

    result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
    output = result.stdout.strip()

    ethernet_details = json.loads(output)
    return ethernet_details


def get_ip_addresses(adapter_name):
    ip_command = [
        "powershell",
        "-Command",
        f"Get-NetIPAddress -InterfaceAlias '{adapter_name}' | Select-Object IPAddress | ConvertTo-Json"
    ]

    ip_result = subprocess.run(ip_command, stdout=subprocess.PIPE, text=True)
    ip_output = ip_result.stdout.strip()

    ip_addresses = json.loads(ip_output)
    return ip_addresses


if __name__ == "__main__":
    ethernet_details = get_ethernet_details()
    for adapter in ethernet_details:
        print(f"Adapter Name: {adapter['Name']}")
        print(f"MAC Address: {adapter['MacAddress']}")
        print(f"Status: {adapter['Status']}")

        ip_addresses = get_ip_addresses(adapter['Name'])
        if ip_addresses:
            print("IP Addresses:")
            for ip in ip_addresses:
                print(f"- {ip['IPAddress']}")

        print("=" * 40)

    response = requests.get('https://api64.ipify.org?format=json')
    data = response.json()
    print("PUBLIC IP")
    print(data)
