import pymssql

server = '192.168.236.31'
port = 1433
user = 'sa'
password = 'Hzmc321#'
database = 'master'

conn = pymssql.connect(server=server, port=port, user=user, password=password, database=database)

cursor = conn.cursor()

cursor.execute("SELECT @@VERSION")

print(cursor.fetchall())

cursor.close()
conn.close()
