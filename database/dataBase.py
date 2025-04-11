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
    
    def addFileToBox(self,fileName,fileSize,BoxId):
        try:
            with sqlite3.connect(self.database) as conn:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO file_info (file_url, file_size, box_id) VALUES (?, ?, ?)",
                            (fileName, fileSize, BoxId))
                inserted_id = cursor.lastrowid
                conn.commit()
            return inserted_id
        except:
            return False
    def listAllFileByBoxId(self,boxId):
        try:
            with sqlite3.connect(self.database) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM file_info WHERE box_id = ?",
                            (boxId,))
                rows = cursor.fetchall()
            return rows
        except KeyError as e:
            return False
    def deliteFile(self,fileId):
        try:
            with sqlite3.connect(self.database) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM file_info WHERE id = ?",
                            (fileId,))
                conn.commit()
            return True
        except:
            return False
obj = DataBase()
print(obj.listAllFileByBoxId(1))

        
        
