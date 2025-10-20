import sqlite3
import json
from datetime import datetime

class Database:
    def __init__(self, db_name='bot_data.db'):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            credits INTEGER DEFAULT 0,
            is_banned INTEGER DEFAULT 0,
            joined_date TEXT,
            last_used TEXT
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS sudo_users (
            user_id INTEGER PRIMARY KEY,
            added_by INTEGER,
            added_date TEXT
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS api_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_name TEXT UNIQUE,
            api_url TEXT,
            api_key TEXT,
            is_active INTEGER DEFAULT 1,
            added_date TEXT
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_id TEXT UNIQUE,
            channel_name TEXT,
            is_active INTEGER DEFAULT 1,
            added_date TEXT
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount INTEGER,
            transaction_type TEXT,
            description TEXT,
            transaction_date TEXT
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )''')
        
        cursor.execute("SELECT COUNT(*) FROM api_config")
        if cursor.fetchone()[0] == 0:
            default_apis = [
                ('lookup_1', 'PLACEHOLDER_URL_1', 'PLACEHOLDER_KEY_1'),
                ('lookup_2', 'PLACEHOLDER_URL_2', 'PLACEHOLDER_KEY_2'),
                ('lookup_3', 'PLACEHOLDER_URL_3', 'PLACEHOLDER_KEY_3')
            ]
            for api_name, api_url, api_key in default_apis:
                cursor.execute('''INSERT INTO api_config (api_name, api_url, api_key, added_date) 
                                  VALUES (?, ?, ?, ?)''', 
                               (api_name, api_url, api_key, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def add_user(self, user_id, username, first_name):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''INSERT OR IGNORE INTO users (user_id, username, first_name, joined_date, last_used) 
                              VALUES (?, ?, ?, ?, ?)''',
                           (user_id, username, first_name, datetime.now().isoformat(), datetime.now().isoformat()))
            conn.commit()
        finally:
            conn.close()
    
    def update_last_used(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET last_used = ? WHERE user_id = ?', 
                           (datetime.now().isoformat(), user_id))
            conn.commit()
        finally:
            conn.close()
    
    def get_user(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            return cursor.fetchone()
        finally:
            conn.close()
    
    def get_credits(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT credits FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        finally:
            conn.close()
    
    def add_credits(self, user_id, amount, description=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET credits = credits + ? WHERE user_id = ?', (amount, user_id))
            cursor.execute('''INSERT INTO transactions (user_id, amount, transaction_type, description, transaction_date)
                              VALUES (?, ?, ?, ?, ?)''',
                           (user_id, amount, 'credit', description, datetime.now().isoformat()))
            conn.commit()
        finally:
            conn.close()
    
    def deduct_credits(self, user_id, amount, description=""):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET credits = credits - ? WHERE user_id = ?', (amount, user_id))
            cursor.execute('''INSERT INTO transactions (user_id, amount, transaction_type, description, transaction_date)
                              VALUES (?, ?, ?, ?, ?)''',
                           (user_id, amount, 'debit', description, datetime.now().isoformat()))
            conn.commit()
        finally:
            conn.close()
    
    def is_sudo(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT user_id FROM sudo_users WHERE user_id = ?', (user_id,))
            return cursor.fetchone() is not None
        finally:
            conn.close()
    
    def add_sudo(self, user_id, added_by):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''INSERT OR IGNORE INTO sudo_users (user_id, added_by, added_date) 
                              VALUES (?, ?, ?)''',
                           (user_id, added_by, datetime.now().isoformat()))
            conn.commit()
        finally:
            conn.close()
    
    def remove_sudo(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM sudo_users WHERE user_id = ?', (user_id,))
            conn.commit()
        finally:
            conn.close()
    
    def get_all_sudo(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT user_id FROM sudo_users')
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_api_config(self, api_name):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT api_url, api_key FROM api_config WHERE api_name = ? AND is_active = 1', (api_name,))
            result = cursor.fetchone()
            return {'url': result[0], 'key': result[1]} if result else None
        finally:
            conn.close()
    
    def update_api_config(self, api_name, api_url, api_key):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''UPDATE api_config SET api_url = ?, api_key = ?, added_date = ? 
                              WHERE api_name = ?''',
                           (api_url, api_key, datetime.now().isoformat(), api_name))
            conn.commit()
        finally:
            conn.close()
    
    def get_all_apis(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT api_name, api_url, is_active FROM api_config')
            return cursor.fetchall()
        finally:
            conn.close()
    
    def add_channel(self, channel_id, channel_name):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''INSERT OR IGNORE INTO channels (channel_id, channel_name, added_date) 
                              VALUES (?, ?, ?)''',
                           (channel_id, channel_name, datetime.now().isoformat()))
            conn.commit()
        finally:
            conn.close()
    
    def remove_channel(self, channel_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM channels WHERE channel_id = ?', (channel_id,))
            conn.commit()
        finally:
            conn.close()
    
    def get_all_channels(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT channel_id, channel_name FROM channels WHERE is_active = 1')
            return cursor.fetchall()
        finally:
            conn.close()
    
    def get_total_users(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT COUNT(*) FROM users')
            return cursor.fetchone()[0]
        finally:
            conn.close()
    
    def get_all_user_ids(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT user_id FROM users WHERE is_banned = 0')
            return [row[0] for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def ban_user(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET is_banned = 1 WHERE user_id = ?', (user_id,))
            conn.commit()
        finally:
            conn.close()
    
    def unban_user(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('UPDATE users SET is_banned = 0 WHERE user_id = ?', (user_id,))
            conn.commit()
        finally:
            conn.close()
    
    def is_banned(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT is_banned FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            return result[0] == 1 if result else False
        finally:
            conn.close()
