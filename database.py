import sqlite3

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('incidents.db', check_same_thread=False)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                attack_type TEXT,
                confidence REAL,
                anomaly_score REAL,
                risk_score INTEGER,
                severity TEXT,
                report TEXT,
                timestamp TEXT
            )
        ''')
        self.conn.commit()

    def insert_incident(self, attack_type, confidence, anomaly_score, risk_score, severity, report, timestamp):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO incidents (attack_type, confidence, anomaly_score, risk_score, severity, report, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (attack_type, confidence, anomaly_score, risk_score, severity, report, timestamp))
        self.conn.commit()

    def fetch_incidents(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM incidents')
        return cursor.fetchall()
    
    def fetch_incidents_by_types(self, attack_type):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM incidents WHERE attack_type = ?', (attack_type,))
        return cursor.fetchall()
    

    
