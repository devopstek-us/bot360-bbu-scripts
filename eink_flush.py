import paramiko

host = "169.254.93.82"
port = 22
username = "vrizn"
password = 'raspberry'

# Path to the remote Python script
remote_flush_script_path = 'Music/bot360-eink/examples/epd_2in7_test_flush.py'

remote_run_script_path = 'Music/bot360-eink/examples/epd_2in7_test.py'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# Workaround for no authentication:
# https://github.com/paramiko/paramiko/issues/890#issuecomment-906893725
try:
    client.connect(host, port=port, username=username, password=password, look_for_keys=False)

    # Execute remote Python script
    stdin, stdout, stderr = client.exec_command(f"python3 {remote_flush_script_path}")

    output = stdout.read().decode()
    error = stderr.read().decode()

    print("Remote script output:")
    print(output)
    print("Remote script error:")
    print(error)

    # Close SSH connection
    client.close()
except paramiko.SSHException as e:
    if not password:
        client.get_transport().auth_none(username)
    else:
        raise e
    print(e)

# Now we can interact with the client as usual
stdin, stdout, stderr = client.exec_command("ls /")
lines = stdout.readlines()
print(lines)
