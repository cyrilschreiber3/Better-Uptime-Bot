import os
import sqlite3
import mysql.connector
from dotenv import load_dotenv

load_dotenv()
DB_TYPE = os.getenv('DB_TYPE')
DB_FILE = os.getenv('DB_FILE')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASS')
DB_NAME = os.getenv('DB_NAME')

def db_connect():
    if DB_TYPE == "sqlite":
        db = sqlite3.connect(DB_FILE)
        cursor = db.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS resolutions 
            (id INTEGER, monitor VARCHAR(45), checkedURL VARCHAR(45), cause VARCHAR(100), startDate VARCHAR(45), endDate VARCHAR(45), length VARCHAR(45), link VARCHAR(150), message_id BIGINT, PRIMARY KEY (id))''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS alerts
            (id INTEGER, nature VARCHAR(20), monitor VARCHAR(45), checkedURL VARCHAR(45), cause VARCHAR(100), startDate VARCHAR(45), link VARCHAR(150), resolved_id INTEGER, message_id BIGINT, PRIMARY KEY (id AUTOINCREMENT), FOREIGN KEY ("resolved_id") REFERENCES resolutions(id))''')
    
    elif DB_TYPE == "mysql":
        db = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            passwd=DB_PASS,
            database=DB_NAME
        )
        cursor = db.cursor()

        cursor.execute('''CREATE TABLE IF NOT EXISTS resolutions 
            (id INTEGER, monitor VARCHAR(45), checkedURL VARCHAR(45), cause VARCHAR(100), startDate VARCHAR(45), endDate VARCHAR(45), length VARCHAR(45), link VARCHAR(150), message_id BIGINT, PRIMARY KEY (id))''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS alerts
            (id INTEGER NOT NULL AUTO_INCREMENT, nature VARCHAR(20), monitor VARCHAR(45), checkedURL VARCHAR(45), cause VARCHAR(100), startDate VARCHAR(45), link VARCHAR(150), resolved_id INTEGER, message_id BIGINT, PRIMARY KEY (id), FOREIGN KEY (resolved_id) REFERENCES resolutions(id))''')
    
    return db