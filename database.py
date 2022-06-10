import hashlib
import sqlite3
import datetime
import pandas as pd

def get_time():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

class AccountDB():
    def __init__(self) -> None:
        self.conn = sqlite3.connect('account.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT, password TEXT)')

    def add_account(self, usr, pwd):
        self.cursor.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(usr, hash(pwd)))
        self.conn.commit()
        
    def fetch_account(self, usr, pwd):
        self.cursor.execute('SELECT * FROM userstable WHERE username = ? AND password = ?', (usr, hash(pwd)))
        data = self.cursor.fetchall()
        return data
    
    # admin user only
    def view_all_accounts(self):
        self.cursor.execute('SELECT * FROM userstable ORDER BY username')
        data = self.cursor.fetchall()
        return data

class DashboardDB():
    def __init__(self) -> None:
        self.conn = sqlite3.connect('dashboard.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS dashboard(username TEXT, session_id TEXT, time TEXT, score TEXT)')
        
    def update_record(self, username, session_id, score):
        self.cursor.execute('SELECT * FROM dashboard WHERE username = ? AND session_id = ?', (username, session_id))
        data = self.cursor.fetchall()
        if len(data) == 0:  # insert
            self.cursor.execute('INSERT INTO dashboard(username, session_id, time, score) VALUES (?,?,?,?)', (username, session_id, get_time(), score))
        else:  # update
            self.cursor.execute('UPDATE dashboard SET time = ?, score = ? WHERE username = ? AND session_id = ?', (get_time(), score, username, session_id))
        self.conn.commit()
        
    def fetch_record(self, username):
        self.cursor.execute('SELECT * FROM dashboard WHERE username = ?', (username))
        data = self.cursor.fetchall()
        return data
    
    def fetch_records_for_show(self):
        # ref: https://stackoverflow.com/a/28119350/13874470
        # ref: https://stackoverflow.com/questions/4618624/
        self.cursor.execute(
            '''
            SELECT
                username,
                time,
                score,
                method_name
            FROM dashboard AS a
            WHERE username || '-' || session_id || '-' || time IN (
                SELECT username || '-' || session_id || '-' || time
                FROM dashboard AS b
                WHERE a.username = b.username
                AND b.score IS NOT NULL
                ORDER BY b.score
                LIMIT 1
            )
            ORDER BY score, username
            '''
        )
        data = self.cursor.fetchall()
        return data

    # admin user only
    def view_all_records(self):
        self.cursor.execute('SELECT * FROM dashboard ORDER BY username')
        data = self.cursor.fetchall()
        return data

    def add_column(self, column_name, type):
        self.cursor.execute(f'ALTER TABLE dashboard ADD COLUMN {column_name} {type}')