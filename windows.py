import winrm

session = winrm.Session('http://192.168.236.104:5985/wsman', auth=('administrator', 'Hzmc321#'))

cmd = 'ipconfig'

result = session.run_cmd(cmd)

print(result.std_out.decode(encoding='cp1252'))