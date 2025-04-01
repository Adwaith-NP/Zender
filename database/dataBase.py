import sqlite3
import os
from pathlib import Path

class DataBase:
    def __init__(self):
        BASE_DIR = Path(__file__).parent.resolve()
        self.database = os.path.join(BASE_DIR, "zender.db") 
        
    def add_box(self,boxId,password,enc):
        try:
            with sqlite3.connect(self.database) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO box (boxName, password, encrypted) VALUES (?, ?, ?)", 
                            (boxId, password, enc))
                conn.commit()
            return True
        except:
            return False
        
    def return_data_in_DB(self):
        try:
            with sqlite3.connect(self.database) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM box")
                rows = cursor.fetchall()
                return rows
        except:
            pass
        
obj = DataBase()
obj.return_data_in_DB()
        
        
