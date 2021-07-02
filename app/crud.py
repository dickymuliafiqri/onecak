from sqlite3 import Error
import sqlite3

db_file = './database/onecak.db'

posts_table = '''CREATE TABLE IF NOT EXISTS posts(
                id integer PRIMARY KEY AUTOINCREMENT,
                json_value text NOT NULL
                );'''

tasks_table = '''CREATE TABLE IF NOT EXISTS tasks(
                id integer PRIMARY KEY AUTOINCREMENT,
                recent_post integer NOT NULL,
                last_scan integer NOT NULL,
                database_length integer NOT NULL
                );'''

post_insert = '''INSERT INTO posts(
        json_value)
        VALUES(
            ?
        )'''

task_insert = '''INSERT INTO tasks(
        recent_post,
        last_scan,
        database_length)
        VALUES(
            ?, ?, ?
        )'''

posts_update = '''UPDATE posts SET
                json_value = ?
                WHERE id = ?
                '''

tasks_update = '''UPDATE tasks SET
                recent_post = ?,
                last_scan = ?,
                database_length = ?
                WHERE id = ?
                '''

post_delete = '''DELETE FROM posts WHERE id = ?'''

task_delete = '''DELETE FROM tasks WHERE id = ?'''

posts_length = '''SELECT COUNT(*) FROM posts'''

tasks_length = '''SELECT COUNT(*) FROM tasks'''

class OnecakDB():
    def __init__(self):
        self.conn = None
        self.retry_connect = 0
        while True:
            try: 
                self.conn = sqlite3.connect(db_file)
                if self.conn: 
                    print(sqlite3.version)
                    print('Connected to ', db_file)
                    break
            except Error as err:
                print('Failed connect to ', db_file, '\nError: ', err)
                self.retry_connect += 1
            if self.retry_connect >= 3:
                print('Failed to connect, aborting process...')
                break
            print('Retry to connect ({})'.format(self.retry_connect))
        if self.conn is None: raise 'Error while try to connect to Database'
    
    def run_command(self, command, value=None):
        c = None
        result = None
        try:
            c = self.conn.cursor()
            if value is None: c.execute(command)
            else: c.execute(command, value)
            result = c.fetchone()
        except Error as err:
            raise err
        self.conn.commit()
        if result is not None:
            return result[0]
        return result