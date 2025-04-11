import dearpygui.dearpygui as dpg
from tkinter import filedialog
import multiprocessing
import threading
import os
from urllib.parse import urlparse
import shutil
from database.dataBase import DataBase
from datetime import date
from pathlib import Path
import bcrypt
import time

class FileBox:
    def __init__(self,zender,boxId,encrypt,password,boxName):
        self.db = DataBase()
        self.zender = zender
        self.password = password
        self.boxName = boxName
        self.fileNotInSelection = True
        self.childWindowNotShown = True
        self.boxId = boxId
        self.encrypt = encrypt
        self.fileCount = 1
        self.filePath = None
        if encrypt:
            self.fileDir = os.path.join(self.zender.BASE_DIR,"files/encrypted")
            self.realPassword = None
        else:
            self.fileDir = os.path.join(self.zender.BASE_DIR,"files/non_encrypted")
            
    def moveToDownloadThread(self,fileName):
        home_dir = Path.home()
        downloads_dir = home_dir / 'Downloads'
        file_path = os.path.join(self.fileDir,fileName)
        self.zender.loadingWindow(self.zender.fileBox,"Moving to Dwonload Directory",[self.groupName,"fileInfoWindow"],nameSpace="UN01")
        shutil.copy(file_path,downloads_dir)
        self.zender.stopSpinning = True
        self.clossFileInfoWindow()
    
    def moveToDownload(self,sender,app_data,fileName):
        if self.encrypt:
            pass
        else:
            self.zender.stopSpinning = False
            thread = threading.Thread(target=self.moveToDownloadThread,args=(fileName,))
            thread.start()
    
    def copyFile(self,filePath,dirPath,fileName,filesize,fileId):
        shutil.copy(filePath,dirPath)
        self.zender.stopSpinning = True
        self.clossAddNewFileWindow()
        today = date.today()
        self.addItemsInTeble(fileName,filesize,today,fileId)
        self.zender.resize(self.zender.fileBox,self.groupName)
    
    def goToHistory(self):
        if self.childWindowNotShown and self.zender.stopSpinning:
            self.zender.fromWhere = self.zender.fileBox
            if dpg.does_item_exist(self.zender.historyWindow):
                dpg.hide_item(self.zender.fileBox)
                dpg.show_item(self.zender.historyWindow)
                self.zender.resize(self.zender.historyWindow)
            else:
                self.zender.history.historyManin(zender=self.zender)
    
    def removeFile(self,sender, app_data,fileName):
        filePath = os.path.join(self.fileDir,fileName[0])
        if os.path.exists(filePath):
            os.remove(filePath)
            dpg.delete_item(fileName[1])
            self.groupName.remove(fileName[1])
            self.db.deliteFile(fileName[2])
            self.clossFileInfoWindow()
    
    def isFileInDb(self,fileName):
        fileList = self.db.listAllFileByBoxId(self.boxId)
        for tup in fileList:
            if tup[1] == fileName:
                return True
        return False
    
    def addNonEncryptedFile(self):
        if self.filePath:
            filePath = os.path.join(self.filePath)
            parsed = urlparse(filePath)
            
            fileName = os.path.basename(parsed.path)
            size_bytes = os.path.getsize(filePath)
            if size_bytes/(1024 * 1024) > 1:
                filesize = "{:.2f} MB".format(size_bytes / (1024 * 1024))
            else:
                filesize = "{:.2f} KB".format(size_bytes / (1024))
            
            copyPath = os.path.join(self.zender.BASE_DIR,"files/non_encrypted")
            filePathInCopyPath = os.path.join(copyPath,fileName)
            
            if not os.path.exists(filePathInCopyPath):
                result = self.db.addFileToBox(fileName,filesize,self.boxId)
                if result:
                    self.zender.stopSpinning = False
                    self.zender.loadingWindow(self.zender.fileBox,"Coping pleas wait",[self.groupName,"addNewFileWindow"])
                    thread = threading.Thread(target=self.copyFile,args=(filePath,copyPath,fileName,filesize,result))
                    thread.start()
            else:
                if not self.isFileInDb(fileName):
                    result = self.db.addFileToBox(fileName,filesize,self.boxId)
                    self.clossAddNewFileWindow()
                    today = date.today()
                    self.addItemsInTeble(fileName,filesize,today,result)
                    self.zender.resize(self.zender.fileBox,self.groupName)
                
    def backToYourBox(self):
        if self.childWindowNotShown and self.zender.stopSpinning:
            dpg.hide_item(self.zender.fileBox)
            dpg.show_item(self.zender.yourBoxWindow)
            self.zender.resize(self.zender.yourBoxWindow)
    def open_file_dialog(self,queue):
        file_path = filedialog.askopenfilename()
        queue.put(file_path)
    def select_file(self):
        if self.fileNotInSelection:
            self.fileNotInSelection = False
            queue = multiprocessing.Queue()
            process = multiprocessing.Process(target=self.open_file_dialog,args=(queue,))
            process.start()
            process.join() 
            result = queue.get()
            if result:
                dpg.set_value("filePathText",result)
                self.filePath = result
            self.fileNotInSelection = True
    def select_file_thread(self):
        thread = threading.Thread(target=self.select_file)
        thread.start()
    def clossAddNewFileWindow(self):
            if self.fileNotInSelection and self.zender.stopSpinning:
                self.filePath = False
                self.childWindowNotShown = True
                dpg.delete_item("addNewFileWindow")
                self.zender.resize(self.zender.fileBox,self.groupName)
    def addNewFile(self):
        if not self.encrypt or (self.realPassword and self.encrypt):
            if not dpg.does_item_exist('addNewFileWindow') and self.childWindowNotShown:
                self.childWindowNotShown = False
                with dpg.child_window(tag="addNewFileWindow",width=550,height=400,border=False,parent=self.zender.fileBox) as elderChild:
                    dpg.bind_item_theme(elderChild,self.zender.childTheam((157, 104, 75, 255)))
                    dpg.add_image_button(texture_tag="icon_cross",pos=(480,10),width=50, height=50, frame_padding=0, background_color=(157, 104, 75, 255),callback=self.clossAddNewFileWindow)
                    text = dpg.add_text("Add File",pos=(265,50))
                    dpg.bind_item_font(text,self.zender.fontSetUp)
                    dpg.bind_item_theme(text, self.zender.textColorSetUp((0, 0, 0, 255))) 
                    with dpg.child_window(width=365,height=50,pos=(30,150)) as filePath:
                        dpg.bind_item_theme(filePath,self.zender.childTheam((117, 117, 117, 255)))
                        dpg.add_text("File Path",pos=(5,15),tag="filePathText")
                    button = dpg.add_button(label="browse",width=100,height=50,pos=(400,150),tag="browseButton",callback=self.select_file_thread)
                    dpg.bind_item_theme(button, self.zender.button2)
                    dpg.bind_item_font(button, self.zender.fontSetUp)
                    if self.encrypt:
                        callBackFunction = None
                    else:
                        callBackFunction = self.addNonEncryptedFile
                    add_button = dpg.add_button(label="Add File",width=470,height=50,pos=(30,220),callback=callBackFunction)
                    dpg.bind_item_theme(add_button, self.zender.button2)
                    dpg.bind_item_font(add_button, self.zender.fontSetUp)
                    info_text = dpg.add_text("info : The selected file has been saved to the directory \"files\"",pos=(50,300))
                    dpg.bind_item_font(info_text, self.zender.fontSetUp)
                    dpg.bind_item_theme(info_text, self.zender.textColorSetUp((0, 0, 0, 255)))
                self.zender.resize(self.zender.fileBox,self.groupName,"addNewFileWindow")
    def clossFileInfoWindow(self):
        if self.fileNotInSelection:
                self.childWindowNotShown = True
                dpg.delete_item("fileInfoWindow")
                self.zender.resize(self.zender.fileBox,self.groupName)
    def fileInfo(self,sender, app_data, user_data,fileId):
        if not self.encrypt or (self.realPassword and self.encrypt):
            if not dpg.does_item_exist('fileInfoWindow') and self.childWindowNotShown:
                self.childWindowNotShown = False
                with dpg.child_window(tag="fileInfoWindow",width=550,height=400,border=False,parent=self.zender.fileBox) as elderChild:
                    dpg.bind_item_theme(elderChild,self.zender.childTheam((157, 104, 75, 255)))
                    dpg.add_image_button(texture_tag="icon_cross",pos=(480,10),width=50, height=50, frame_padding=0, background_color=(157, 104, 75, 255),callback=self.clossFileInfoWindow)
                    text = dpg.add_text("File Info",pos=(265,50))
                    dpg.bind_item_font(text,self.zender.fontSetUp)
                    dpg.bind_item_theme(text, self.zender.textColorSetUp((0, 0, 0, 255))) 
                    with dpg.group(pos=(50,150)) as group:
                        dpg.add_text("File name")
                        with dpg.child_window(width=350,height=40,pos=(150,143)) as fileNameWindow:
                            dpg.bind_item_theme(fileNameWindow,self.zender.childTheam((0, 0, 0, 255)))
                            text = dpg.add_text(user_data[0],pos=(5,8))
                            dpg.bind_item_font(text,self.zender.fontSetUp)
                            dpg.bind_item_theme(text, self.zender.textColorSetUp((255, 255, 255, 255))) 
                        dpg.add_text("File size",pos=(50,210))
                        with dpg.child_window(width=350,height=40,pos=(150,200)) as fileNameWindow:
                            dpg.bind_item_theme(fileNameWindow,self.zender.childTheam((0, 0, 0, 255)))
                            text = dpg.add_text(user_data[1],pos=(5,8))
                            dpg.bind_item_font(text,self.zender.fontSetUp)
                            dpg.bind_item_theme(text, self.zender.textColorSetUp((255, 255, 255, 255))) 
                        dpg.add_text(f"Upload date",pos=(50,267))
                        with dpg.child_window(width=350,height=40,pos=(150,257)) as fileNameWindow:
                            dpg.bind_item_theme(fileNameWindow,self.zender.childTheam((0, 0, 0, 255)))
                            text = dpg.add_text(user_data[2],pos=(5,8))
                            dpg.bind_item_font(text,self.zender.fontSetUp)
                            dpg.bind_item_theme(text, self.zender.textColorSetUp((255, 255, 255, 255))) 
                        dpg.bind_item_font(group,self.zender.fontSetUp)
                        dpg.bind_item_theme(group, self.zender.textColorSetUp((0, 0, 0, 255))) 
                    button = dpg.add_button(label="remove",width=100,height=50,pos=(160,330),callback=self.removeFile,user_data = (user_data[0],user_data[3],fileId))
                    button2 = dpg.add_button(label="Download",width=100,height=50,pos=(300,330),callback=self.moveToDownload,user_data=user_data[0])
                    dpg.bind_item_theme(button, self.zender.button2)
                    dpg.bind_item_font(button,self.zender.fontSetUp)
                    dpg.bind_item_theme(button2, self.zender.buttonTheam((78, 93, 108, 255)))
                    dpg.bind_item_font(button2,self.zender.fontSetUp)
                self.zender.resize(self.zender.fileBox,self.groupName,"fileInfoWindow")
    def addItemsInTeble(self,name,size,date,fileId):
        if self.fileCount > 2:
            self.fileCount = 0

            with dpg.table_row(parent="tableInFileBox") as table:
                self.tableInstance = table
        with dpg.group(parent=self.tableInstance) as fileGroup:
                                label = name.lower()
                                if len(label) > 15:
                                    label = label[:15] + "..."
                                self.groupName.append(fileGroup)
                                dpg.add_image_button(texture_tag="icon_folder", width=100, height=100, frame_padding=0, background_color=(203, 184, 116, 255),callback=self.fileInfo,user_data=(name,size,date,fileGroup,fileId))
                                text = dpg.add_text(label, wrap=100)
                                dpg.bind_item_font(text,self.zender.fontSetUp)
                                dpg.bind_item_theme(text, self.zender.textColorSetUp((0, 0, 0, 255))) 
                        
        self.fileCount = self.fileCount + 1
    def fetchData(self):
        self.groupName = []
        parent_width = dpg.get_item_width(self.zender.fileBox)
        if dpg.does_item_exist(self.zender.fileBox+"child"):
            dpg.delete_item(self.zender.fileBox+"child")
        with dpg.child_window(tag=self.zender.fileBox+"child",parent=self.zender.fileBox,pos=(10,130),width=parent_width,border=False):
            with dpg.table(tag="tableInFileBox",header_row=False, resizable=False, pos=(100, 90)):
                for _ in range(3):
                    dpg.add_table_column()
                with dpg.table_row(parent="tableInFileBox") as table:
                    self.tableInstance = table
                    with dpg.group() as fileGroup:
                                    self.groupName.append(fileGroup)
                                    dpg.add_image_button(texture_tag="icon_add-file", width=100, height=100, frame_padding=0, background_color=(203, 184, 116, 255),callback=self.addNewFile)

                filesInDb = self.db.listAllFileByBoxId(self.boxId)
                for file in filesInDb:
                    filePath = os.path.join(self.fileDir,file[1])
                    if os.path.exists(filePath):
                        self.addItemsInTeble(file[1],file[2],file[3][:10],file[0])
                        
        self.zender.resize(self.zender.fileBox,self.groupName)
    def hide_text(self, tag):
        time.sleep(3)
        dpg.set_value(tag, "")
    def notofication(self, text):
        dpg.set_value("warningInfo", text)
        thread = threading.Thread(target=self.hide_text, args=("warningInfo",))
        thread.start()
    def verifyPassword(self):
        password = dpg.get_value("passwordEnc")
        if password:
            if bcrypt.checkpw(password.encode(), self.password):
                self.realPassword = password
                dpg.delete_item('passwordRequest')
            else:
                self.notofication("Incorrect Password Try Again")
    def passwordRequest(self):
        if not dpg.does_item_exist('passwordRequest'):
            with dpg.child_window(tag="passwordRequest",width=550,height=400,border=False,parent=self.zender.fileBox) as elderChild:
                dpg.bind_item_theme(elderChild,self.zender.childTheam((157, 104, 75, 255)))
                
                text = dpg.add_text("To access the box enter the password",pos=(140,50))
                dpg.bind_item_font(text,self.zender.fontSetUp)
                dpg.bind_item_theme(text, self.zender.textColorSetUp((0, 0, 0, 255))) 
                
                dpg.add_input_text(tag="passwordEnc",pos=(50,180),width=450,hint='Password')
                dpg.bind_item_theme("passwordEnc", self.zender.input_theme)
                dpg.bind_item_font("passwordEnc", self.zender.fontSetUp)
                
                button = dpg.add_button(label="Download",width=450,height=50,pos=(50,240),callback=self.verifyPassword)
                dpg.bind_item_theme(button, self.zender.buttonTheam((78, 93, 108, 255)))
                dpg.bind_item_font(button,self.zender.fontSetUp)
                
        self.zender.resize(self.zender.fileBox,self.groupName,"passwordRequest")
    def fileBoxMain(self):
        if not dpg.does_item_exist(self.zender.fileBox):
            with dpg.window(tag=self.zender.fileBox,pos=(0, 0), no_title_bar=True, no_resize=True, no_move=True):
                text = dpg.add_text(self.boxName,tag="boxName")
                dpg.add_image_button(texture_tag="icon_download",tag="zender_download_fileBox", width=50, height=50, frame_padding=0, background_color=(203, 184, 116, 255),callback=self.goToHistory)
                dpg.add_image_button(texture_tag="icon_go_back",tag="back_icon_fileBox", width=50, height=50, frame_padding=0, background_color=(203, 184, 116, 255),callback=self.backToYourBox)
                dpg.bind_item_font(text,self.zender.large_font_max)
                dpg.bind_item_theme(text, self.zender.textColorSetUp((0, 0, 0, 255))) 
                testWarning = dpg.add_text('',tag='warningInfo',wrap=410)
                dpg.bind_item_font(testWarning,self.zender.fontSetUp)
                dpg.bind_item_theme(testWarning, self.zender.textColorSetUp((255, 69, 0, 255))) 
                self.fetchData()
                if self.encrypt:
                    self.passwordRequest()
                dpg.bind_theme(self.zender.WindowTheam)
                