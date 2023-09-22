import pymysql, cx_Oracle, winrm, paramiko, pymssql
import argparse
import importlib
import os


class Base:
    def __init__(self, host, port, user, password):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

    def connect(self):
        raise ValueError

    def run(self, raw_input):
        raise ValueError
    
    def generate_script(self, raw_input, script_name):
        with open(f"{script_name}.py", "w") as f:
            f.write(f"""import main
import argparse

q = '{raw_input}'
type_str = '{self.type}'
host = '{self.host}'
port = {self.port}
user = '{self.user}'
password = '{self.password}'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command runner')
    parser.add_argument('-t', '--type', type=str)
    parser.add_argument('-ho', '--host', type=str)
    parser.add_argument('-po', '--port', type=int)
    parser.add_argument('-u', '--user', type=str)
    parser.add_argument('-pa', '--password', type=str)
    parser.add_argument('-c', '--command', type=str)

    args = parser.parse_args()

    type_str = args.type if args.type else type_str
    host = args.host if args.host else host
    port = args.port if args.port else port
    user = args.user if args.user else user
    password = args.password if args.password else password
    q = args.command if args.command else q

    client_class = getattr(main, type_str)
    client = client_class(host, port, user, password)
    client.connect()
    result = client.run(q)
    print(result)
""")
        print(f"Script generated: {script_name}.py")


class Client(Base):
    pass


class Windows(Client):
    def __init__(self, host, port, user, password):
        super().__init__(host, port, user, password)
        self.type = 'Windows'

    def connect(self):
        self.connection = winrm.Session(f'http://{self.host}:{self.port}/wsman', auth=(f'{self.user}', f'{self.password}'))
        print(f'http://{self.host}:{self.port}/wsman', ({self.user}, {self.password}))

    def run(self, raw_input):
        result = self.connection.run_cmd(raw_input)
        return result.std_out.decode(encoding='cp1252')


class Linux(Client):
    def __init__(self, host, port, user, password):
        super().__init__(host, port, user, password)
        self.type = 'Linux'

    def connect(self):
        self.connection = paramiko.SSHClient()
        self.connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connection.connect(hostname=self.host, port=self.port, username=self.user, password=self.password)

    def run(self, raw_input):
        stdin, stdout, stderr = self.connection.exec_command(raw_input)
        return stdout.read().decode()


class Database(Base):
    def run(self, raw_input):
        self.cursor.execute(raw_input)
        raw_results = self.cursor.fetchall()
        return raw_results


class Mysql(Database):
    def __init__(self, host, port, user, password):
        super().__init__(host, port, user, password)
        self.type = 'Mysql'

    def connect(self):
        connection = pymysql.connect(host=self.host, user=self.user, password=self.password, port=self.port)
        self.cursor = connection.cursor()
    
    def run(self, raw_input):
        raw_results = super().run(raw_input)
        column_names = [desc[0] for desc in self.cursor.description]
        return column_names, raw_results


class Oracle(Database):
    def __init__(self, host, port, user, password, name):
        super().__init__(host, port, user, password)
        self.name = name
        self.type = 'Oracle'

    def connect(self):
        dsn = cx_Oracle.makedsn(self.host, self.port, self.name)
        connection = cx_Oracle.connect(self.user, self.password, dsn=dsn)
        self.cursor = connection.cursor()

    def generate_script(self, raw_input, script_name):
        with open(f"{script_name}.py", "w") as f:
            f.write(f"""import main
import argparse

q = '{raw_input}'
type_str = '{self.type}'
host = '{self.host}'
port = {self.port}
user = '{self.user}'
password = '{self.password}'
name = '{self.name}'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command runner')
    parser.add_argument('-t', '--type', type=str)
    parser.add_argument('-ho', '--host', type=str)
    parser.add_argument('-po', '--port', type=int)
    parser.add_argument('-u', '--user', type=str)
    parser.add_argument('-pa', '--password', type=str)
    parser.add_argument('-c', '--command', type=str)
    parser.add_argument('-n', '--name', type=str)
    
    args = parser.parse_args()

    type_str = args.type if args.type else type_str
    host = args.host if args.host else host
    port = args.port if args.port else port
    user = args.user if args.user else user
    password = args.password if args.password else password
    q = args.command if args.command else q
    name = args.name if args.name else name

    client_class = getattr(main, type_str)
    client = client_class(host, port, user, password, name)
    client.connect()
    result = client.run(q)
    print(result)
""")


class Sqlserver(Database):
    def __init__(self, host, port, user, password, name):
        super().__init__(host, port, user, password)
        self.name = name
        self.type = 'Sqlserver'

    def connect(self):
        connection = pymssql.connect(server=self.host, port=self.port, user=self.user, password=self.password, database=self.name)
        self.cursor = connection.cursor()

    def generate_script(self, raw_input, script_name):
        with open(f"{script_name}.py", "w") as f:
            f.write(f"""import main
import argparse

q = '{raw_input}'
type_str = '{self.type}'
host = '{self.host}'
port = {self.port}
user = '{self.user}'
password = '{self.password}'
name = '{self.name}'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command runner')
    parser.add_argument('-t', '--type', type=str)
    parser.add_argument('-ho', '--host', type=str)
    parser.add_argument('-po', '--port', type=int)
    parser.add_argument('-u', '--user', type=str)
    parser.add_argument('-pa', '--password', type=str)
    parser.add_argument('-c', '--command', type=str)
    parser.add_argument('-n', '--name', type=str)
    
    args = parser.parse_args()

    type_str = args.type if args.type else type_str
    host = args.host if args.host else host
    port = args.port if args.port else port
    user = args.user if args.user else user
    password = args.password if args.password else password
    q = args.command if args.command else q
    name = args.name if args.name else name

    client_class = getattr(main, type_str)
    client = client_class(host, port, user, password, name)
    client.connect()
    result = client.run(q)
    print(result)
""")


def handle_client(input_type):
    raw_input = input("Enter your CMD command: ")
    try:
        if input_type == 'W':
            client = Windows('192.168.236.104', 5985, 'administrator', 'Hzmc321#')
        elif input_type == 'L':
            client = Linux('192.168.236.102', 22, 'oracle', 'oracle')
        else:
            exit("wrong input, exiting")
        client.connect()
        result = client.run(raw_input)
        print(result)

        confirmation = input("Is this what you expected? (Y/N): ")
        if confirmation.lower() == 'y':
            script_name = input("Enter a name for the generated script: ")
            client.generate_script(raw_input, script_name)

    except Exception as e:
        print(f"An error occurred: {e}")

def handle_database(input_type):
    raw_input = input("Enter your SQL command: ")
    try:
        if input_type == 'M':
            db = Mysql('192.168.236.151', 3306, 'drcc', 'okp@admin!123')
        elif input_type == 'O':
            db = Oracle('192.168.236.101', 1521, 'drcc', 'okp@admin!123', 'orcl')
        elif input_type == 'S':
            db = Sqlserver('192.168.236.31', 1433, 'sa', 'Hzmc321#', 'master')
        db.connect()
        result = db.run(raw_input)
        print(result)

        confirmation = input("Is this what you expected? (Y/N): ")
        if confirmation.lower() == 'y':
            script_name = input("Enter a name for the generated script: ")
            db.generate_script(raw_input, script_name)

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    while True:
        distinguisher = input("Client/Database? (C/D)").upper()

        if distinguisher == "C":
            while True:
                input_type = input("Windows/Linux (W/L)").upper()
                if input_type == "W" or input_type == "L":
                    handle_client(input_type)
                    exit()
                else:
                    print("wrong platform, please enter a valid character")
                    continue
        elif distinguisher == "D":
            while True:
                input_type = input("mySQL/Oracle/Sqlserver (M/O/S)").upper()
                if input_type == "M" or input_type == "O" or input_type == "S":
                    handle_database(input_type)
                    exit()
                else:
                    print("wrong platform, please enter a valid character")
                    continue
        else:
            print("Wrong input, please try again")
            continue

