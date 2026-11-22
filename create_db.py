import sqlite3

conn = sqlite3.connect('my_database.db')
cursor = conn.cursor()

# создаем таблицы
cursor.executescript('''
DROP TABLE IF EXISTS userPhones;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS phones;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE phones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    number TEXT NOT NULL
);

CREATE TABLE userPhones (
    user_id INTEGER,
    phone_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (phone_id) REFERENCES phones(id)
);
''')

# Добавляем данные
cursor.executescript('''
-- Создаем 3-х пользователей (user1, user2, user3)
INSERT INTO users (name) VALUES ('Александр'); -- id=1
INSERT INTO users (name) VALUES ('Владимир');  -- id=2 (у него не будет телефонов)
INSERT INTO users (name) VALUES ('Кирилл');    -- id=3

-- Создаем 4 телефона (phone1, phone2, phone3, phone4)
INSERT INTO phones (number) VALUES ('+7-900-111-11-11'); -- phone1 (id=1)
INSERT INTO phones (number) VALUES ('+7-900-222-22-22'); -- phone2 (id=2)
INSERT INTO phones (number) VALUES ('+7-900-333-33-33'); -- phone3 (id=3)
INSERT INTO phones (number) VALUES ('+7-900-444-44-44'); -- phone4 (id=4)

-- Связываем user1 с phone1, phone2, phone3
INSERT INTO userPhones (user_id, phone_id) VALUES (1, 1);
INSERT INTO userPhones (user_id, phone_id) VALUES (1, 2);
INSERT INTO userPhones (user_id, phone_id) VALUES (1, 3);

-- Связываем user3 с phone1 и phone4
INSERT INTO userPhones (user_id, phone_id) VALUES (3, 1);
INSERT INTO userPhones (user_id, phone_id) VALUES (3, 4);
''')

conn.commit()
conn.close()
