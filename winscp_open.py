import subprocess

def connect_to_sftp_with_script(script_path):
    winscp_executable = r"C:\Program Files (x86)\WinSCP\WinSCP.exe"  # Modify this path to match your installation path

    try:
        process = subprocess.Popen([winscp_executable, f'/script={script_path}'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        print("STDOUT:", stdout.decode())
        print("STDERR:", stderr.decode())
    except Exception as e:
        print("An error occurred while connecting to SFTP:", e)

if __name__ == "__main__":
    script_path = "sftp_script.txt"
    connect_to_sftp_with_script(script_path)
