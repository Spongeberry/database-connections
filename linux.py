import paramiko

client = paramiko.SSHClient()

client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

client.connect(hostname='192.168.236.102', port=22, username='oracle', password='oracle')

stdin, stdout, stderr = client.exec_command('ifconfig')

print(stdout.read().decode())
print(stderr.read().decode())
