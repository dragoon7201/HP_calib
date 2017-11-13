import paramiko
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.load_system_host_keys()
host = "opi1504-103.clsi.ca"
usrname = "magmap"
password = "w1gg13"

ssh.connect(hostname=host, username=usrname, password=password)
stdin, stdout, stderror = ssh.exec_command('pwd')
print(stdout)