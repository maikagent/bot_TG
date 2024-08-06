import sqlite3
from datetime import datetime

DB_PATH = 'requests.db'

def init_db():
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            phone TEXT,
            company TEXT,
            email TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            vehicle_number TEXT,
            vehicle_brand TEXT,
            is_guest TEXT,
            request_date DATE,
            submission_date TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    connection.commit()
    connection.close()

def add_user(user_id, name, phone, company, email):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO users (user_id, name, phone, company, email)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, name, phone, company, email))
    connection.commit()
    connection.close()

def add_request(user_id, vehicle_number, vehicle_brand, is_guest, request_date):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO requests (user_id, vehicle_number, vehicle_brand, is_guest, request_date, submission_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, vehicle_number, vehicle_brand, is_guest, request_date, datetime.now()))
    connection.commit()
    connection.close()

def get_user(user_id):
    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()
    cursor.execute('''
        SELECT name, phone, company, email
        FROM users
        WHERE user_id = ?
    ''', (user_id,))
    row = cursor.fetchone()
    connection.close()
    if row:
        return {
            'name': row[0],
            'phone': row[1],
            'company': row[2],
            'email': row[3]
        }
    return None

def is_user_registered(user_id):
    return get_user(user_id) is not None
