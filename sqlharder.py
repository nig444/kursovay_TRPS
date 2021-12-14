import sqlite3
class SQLighter:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
    def get_user_id_from_id(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT user_id FROM `users` WHERE `id` = ?", (user_id,)).fetchone()[0]
    def get_user_info(self, user_id):
        """Получаем информацио о пользователе"""
        with self.connection:
            return self.cursor.execute("SELECT * FROM `users` WHERE `user_id` = ?", (user_id,)).fetchone()
    def get_user_state(self, user_id):
        """Получаем состояние о пользователе"""
        with self.connection:
            return self.cursor.execute("SELECT state FROM `users` WHERE `user_id` = ?", (user_id,)).fetchone()[0]
    def user_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `users` WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def add_user(self, user_id, state=0):
        """Добавляем нового пользователя"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `users` (`user_id`, `state`) VALUES(?,?)", (user_id,state))
    def add_progress(self, user_id, state=0):
        """Добавляем нового пользователя"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `progress` (`user_id`, `state`) VALUES(?,?)", (user_id,state))
    
    def update_user_key(self, user_id, key, value):
        """Обновляем данные пользователя"""
        with self.connection:
            if(key=='FIO'):
                return self.cursor.execute("UPDATE `users` SET `FIO` = ? WHERE `user_id` = ?", (value,user_id,))
            if(key=='username'):
                return self.cursor.execute("UPDATE `users` SET `username` = ? WHERE `user_id` = ?", (value,user_id,))
            if(key=='password'):
                return self.cursor.execute("UPDATE `users` SET `password` = ? WHERE `user_id` = ?", (value,user_id,))
            
    def update_user_state(self, user_id, value):
        """Обновляем состояния пользователя"""
        with self.connection:
            return self.cursor.execute("UPDATE `users` SET `state` = ? WHERE `user_id` = ?", (value,user_id))
    def get_data(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            return self.cursor.execute('SELECT mark FROM `progress` WHERE `user_id` = ?', (user_id,)).fetchone()[0]
    def get_all_mark(self):
        with self.connection:
            return self.cursor.execute('SELECT * FROM `progress`').fetchall()
    def set_state_mark(self,user_id):
        with self.connection:
            return self.cursor.execute("UPDATE `progress` SET `state` = 0 WHERE `user_id` = ?", (user_id,))
    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()
        
class SQLharder:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def get_users_info(self):
        """Получаем информацио о пользователе"""
        with self.connection:
            return self.cursor.execute("SELECT id,username,password FROM `users`").fetchall()
    def update_data(self, user_id, value):
        """Обновление данных об успеваемости"""
        with self.connection:
            return self.cursor.execute("UPDATE `progress` SET `mark` = ? , `state` = 1 WHERE `user_id` = ?", (value,user_id))
    def get_data(self, user_id):
        """Получение данных об успеваемости"""
        with self.connection:
            return self.cursor.execute('SELECT mark FROM `progress` WHERE `user_id` = ?', (user_id,)).fetchone()[0]

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()