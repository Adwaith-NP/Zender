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
                last_id = cursor.lastrowid
            return last_id
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
                
            with sqlite3.connect(self.database) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM fileCount WHERE file_name = ?",(fileName,))
                result = cursor.fetchone()
                if result:
                    new_count = result[1] + 1
                    cursor.execute('UPDATE fileCount SET count = ? WHERE file_name = ?', (new_count, fileName))
                else:
                    cursor.execute('INSERT INTO fileCount (file_name, count) VALUES (?, ?)', (fileName, 1))
                
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
        except:
            return False
    def deliteFile(self,fileId):
        try:
            with sqlite3.connect(self.database) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM file_info WHERE id = ?",
                            (fileId,))
            return True
        except:
            return False
        
    def getDataOfBox(self,boxId):
        try:
            with sqlite3.connect(self.database) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM box WHERE boxName = ?",(boxId,))
                conn.commit()
                rows = cursor.fetchall()
            if rows:
                return rows[0]
        except KeyError as e:
            return False
        
    def fileCount(self,fileName):
        try:
            with sqlite3.connect(self.database) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT count FROM fileCount WHERE file_name = ?', (fileName,))
                result = cursor.fetchone()
            return result[0]
        except:
            return None
        
    def decrementCount(self,fileName):
        try:
            with sqlite3.connect(self.database) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT count FROM fileCount WHERE file_name = ?', (fileName,))
                result = cursor.fetchone()
                if result is None:
                    return
                newCount = result[0] - 1
                if newCount == 0:
                    cursor.execute('DELETE FROM fileCount WHERE file_name = ?', (fileName,))
                else:
                    cursor.execute('UPDATE fileCount SET count = ? WHERE file_name = ?', (newCount, fileName))
        except:
            return None
        
    
# obj = DataBase()
# print(obj.listAllFileByBoxId(1))

        
        
