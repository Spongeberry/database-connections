from flask import Flask, request, jsonify, render_template
import pymysql, cx_Oracle, winrm, paramiko, pymssql


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
        print(f"Script generated: {script_name}.py")


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
        print(f"Script generated: {script_name}.py")


app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/run_command', methods=['POST'])
def run_command():
    try:
        data = request.form if request.form else request.json
        cmd_type = data.get('type')
        host = data.get('host')
        port = int(data.get('port'))
        user = data.get('user')
        password = data.get('password')
        name = data.get('name', '')  # Default to empty string if not provided
        command = data.get('command')
        file = data.get('file')

        object = None
        if cmd_type == 'mysql':
            object = Mysql(host, port, user, password)
        elif cmd_type == 'oracle':
            object = Oracle(host, port, user, password, name)
        elif cmd_type == 'sqlserver':
            object = Sqlserver(host, port, user, password, name)
        elif cmd_type == 'windows':
            object = Windows(host, port, user, password)
        elif cmd_type == 'linux':
            object = Linux(host, port, user, password)

        if not object:
            return jsonify({'error': 'Invalid type'}), 400

        object.connect()
        result = object.run(command)

        if file:
            object.generate_script(command, file)

        return jsonify({'result': result})

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)

