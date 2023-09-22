import cx_Oracle

dsn = cx_Oracle.makedsn('192.168.236.101', 1521, 'orcl')

connection = cx_Oracle.connect('drcc', 'okp@admin!123', dsn=dsn)

cursor = connection.cursor()

cursor.execute("SELECT * FROM V$VERSION")

print(cursor.fetchall())