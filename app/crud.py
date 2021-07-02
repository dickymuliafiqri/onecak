from sqlite3 import Error
import sqlite3

db_file = './database/onecak.db'

posts_table = '''CREATE TABLE IF NOT EXISTS posts(
                id integer PRIMARY KEY AUTOINCREMENT,
                post_id integer NOT NULL,
                title text NOT NULL,
                url text NOT NULL,
                src text NOT NULL,
                is_gif integer NOT NULL,
                is_nsfw integer NOT NULL
                );'''

tasks_table = '''CREATE TABLE IF NOT EXISTS tasks(
                id integer PRIMARY KEY AUTOINCREMENT,
                recent_post integer NOT NULL,
                last_scan integer NOT NULL,
                database_length integer NOT NULL
                );'''

post_insert = '''INSERT INTO posts(
        post_id,
        title,
        url,
        src,
        is_gif,
        is_nsfw)
        VALUES(
            ?, ?, ?, ?, ?, ?
        )'''

task_insert = '''INSERT INTO tasks(
        recent_post,
        last_scan,
        database_length)
        VALUES(
            ?, ?, ?
        )'''

posts_update = '''UPDATE posts SET
                post_id = ?,
                title = ?,
                url = ?,
                src = ?,
                is_gif = ?,
                is_nsfw = ?
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

posts_get = '''SELECT json_group_array(json_object('id', post_id,
                                'title', title,
                                'url', url,
                                'src', src,
                                'gif', is_gif,
                                'nsfw', is_nsfw))
                                AS json_result FROM (SELECT * FROM posts WHERE id = ?)'''

tasks_get = '''SELECT json_group_array(json_object('recent_post', recent_post,
                                'last_scan', last_scan,
                                'length', database_length))
                                AS json_result FROM (SELECT * FROM tasks WHERE id = 1)'''

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