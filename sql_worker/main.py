import sqlite3


class Cursor:
    def __init__(self):
        # Создаем соединение с нашей базой данных
        # В нашем примере у нас это просто файл базы
        conn = sqlite3.connect('db.sqlite')

        # Создаем курсор - это специальный объект который делает запросы и получает их результаты
        cursor = conn.cursor()

        self.cursor = cursor
        self.conn = conn

        # ТУТ восстанавливаем данные
        tables = {
            'cinemas': (
                'id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL',
                'name VARCHAR (30) NOT NULL',
                'address VARCHAR (255) NOT NULL',
            ),
            'cinemas_halls': (
                'id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL',
                'name VARCHAR (30) NOT NULL',
                'places BLOB NOT NULL',
                'cols INTEGER NOT NULL',
                'cinema_id INTEGER NOT NULL',
            ),
            'auth': (
                'id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL',
                'login VARCHAR (30) NOT NULL',
                'password VARCHAR (30) NOT NULL',
                'is_admin BOOLEAN NOT NULL CHECK (is_admin IN (0, 1))',
            ),
            'films': (
                'id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL',
                'title VARCHAR (30) NOT NULL',
                'halls BLOB NOT NULL',
                'actual_to INTEGER NOT NULL',
            ),
        }
        for table in tables:
            try:
                cursor.execute('SELECT * FROM {}'.format(table))
            except sqlite3.OperationalError as e:
                print(e, end='')
                cursor.execute('CREATE TABLE {} ({})'.format(table, ", ".join(tables[table])))
                print('------------ FIXED!')

        # проверяем юзера
        if len(self.execute('SELECT * FROM auth WHERE login="admin" AND is_admin=1')) == 0:
            self.execute('INSERT INTO auth (login, password, is_admin) VALUES ("admin", "12345qwert", 1)')

    def execute(self, request_string):
        self.cursor.execute(request_string)
        self.conn.commit()
        return self.cursor.fetchall()


class Request:
    def __init__(self, cursor=Cursor()):
        self.user = {'login': 'Anonym', 'password': None}
        self.cursor = cursor

    def auth(self, login='', password=''):
        users = self.cursor.execute('SELECT * FROM auth WHERE login="{}" and password="{}"'.format(login, password))
        if len(users) > 0:
            self.user = {'id': users[0][0], 'login': users[0][1], 'password': users[0][2], 'is_admin': users[0][3]}
            return {'success': 'Вы успешно авторизовались!'}
        else:
            return {'error': 'Пользователь с такими логином и паролем не найден!'}

    def auth_admin(self, login='', password=''):
        users = self.cursor.execute('SELECT * FROM auth WHERE login="{}" and password="{}" and is_admin=1'.format(login, password))
        if len(users) > 0:
            self.user = {'login': users[0][1], 'password': users[0][2], 'is_admin': 1}
            return {'success': 'Вы успешно авторизовались!'}
        else:
            return {'error': 'Пользователь с такими логином и паролем не найден!'}

    def register(self, login='', password=''):
        if len(login) < 4:
            return {'error': 'Логин не может быть короче 4 символов!'}
        if len(password) < 6:
            return {'error': 'Пароль не может быть короче 6 символов!'}
        self.cursor.execute('INSERT INTO auth (login, password) VALUES login="{}" and password="{}" and is_admin=0'.format(login, password))
        user = self.cursor.cursor.fetchall()
        return user

    def unauth(self):
        self.user = {'login': 'Anonym', 'password': None}

    def kill(self):
        self.cursor.cursor.close()


