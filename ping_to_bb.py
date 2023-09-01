import subprocess
import psycopg2
from datetime import datetime

import requests
from ping3 import ping

# IP address to ping
ip_address = "169.254.2.2"

# PostgreSQL database connection parameters
db_params = {
    "host": "bot360-purplebox-dev.cqblstrpdwe8.us-east-2.rds.amazonaws.com",
    "database": "bot360",
    "user": "postgres",
    "password": "postgresbot360",
}


# Ping the IP address and record the ping time
def ping_ip(ip):
    try:
        time_taken = ping('169.254.2.2')
        return time_taken
    except subprocess.CalledProcessError:
        return None


# Connect to the PostgreSQL database
def connect_to_db():
    try:
        connection = psycopg2.connect(**db_params)
        return connection
    except psycopg2.Error as e:
        print("Error connecting to the database:", e)
        return None


# Insert ping time into the database
def insert_ping_time(connection, ping_time):
    query = "INSERT INTO public.pingBB (timestamp, time_taken) VALUES (%s, %s);"
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (datetime.now(), ping_time))
        connection.commit()
    except psycopg2.Error as e:
        print("Error inserting data:", e)


# Delete old data if more than 10 records exist
def delete_old_data(connection):
    query = "DELETE FROM public.pingBB WHERE id NOT IN (SELECT id FROM public.pingBB ORDER BY timestamp DESC LIMIT 10);"
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
        connection.commit()
    except psycopg2.Error as e:
        print("Error deleting data:", e)


# def get_pingbb_data(connection):
#     query = "SELECT id, timestamp, time_taken FROM public.pingbb;"
#     with connection.cursor() as cursor:
#         cursor.execute(query)
#         columns = [col[0] for col in cursor.description]
#         results = [
#             dict(zip(columns, row))
#             for row in cursor.fetchall()
#         ]
#     return results


def main():
    ping_time = ping_ip(ip_address)
    if ping_time is not None:
        connection = connect_to_db()
        if connection is not None:
            insert_ping_time(connection, ping_time)
            delete_old_data(connection)
            connection.close()

            # url = "https://purplebox-dev.devopstek-projects.com:3000/event/socket"
            # print(list(PingRecord_count))
            # payload = json.dumps({
            #     "data": list(PingRecord_count),
            #     "room": "pingbb"
            # })
            # headers = {
            #     'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY0YjEzZThjODM0NWVlODMyNDU5ZTE4MiIsImlhdCI6MTY5MjE2MjY5OSwiZXhwIjoxNjkyMjQ5MDk5fQ.JzxY3C7GtBmJgPT4BKTOmQU5CgP1tlTYZNDP6nvoFDY',
            #     'Content-Type': 'application/json'
            # }
            #
            # response = requests.request("POST", url, headers=headers, data=payload)
            #
            # print(response.text)


if __name__ == "__main__":
    main()
