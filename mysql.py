import pymysql

connection = pymysql.connect(host='192.168.236.151', user='drcc', password='okp@admin!123', port = 3306)

cursor = connection.cursor()

cursor.execute("USE mysql")

cursor.execute("SHOW TABLES")
print(cursor.fetchall() , '\n')

cursor.execute("SHOW COLUMNS FROM user")
print(cursor.fetchall() , '\n')

cursor.execute("select host,user from mysql.user;")
print(cursor.fetchall())

# Your SQL query execution
cursor.execute("SELECT host, user FROM mysql.user;")

print(cursor.description)

# Fetching column names
column_names = [desc[0] for desc in cursor.description]

# Fetching all rows
rows = cursor.fetchall()

# Printing column names
print("Column Names:", column_names)

# Printing rows
print("Rows:", rows)


#so I want to achieve this, I don't know if it is achievable within mysql, I want to get the column names of the requested data at the very front
#so for example my input is select host, user from mysql.user, I want to get the column name host and user,if I do have as statement within my sql query, get the correct column name

