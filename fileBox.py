import dearpygui.dearpygui as dpg
from tkinter import filedialog
import multiprocessing
import threading

class FileBox:
    def __init__(self,zender):
        self.zender = zender
        self.fileNotInSelection = True
    def childTheam(self,color):
        with dpg.theme() as child_theme:
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg,color)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 15)
        return child_theme
    def open_file_dialog(self,queue):
        file_path = filedialog.askopenfilename()
        queue.put(file_path)
    def select_file(self):
        self.fileNotInSelection = False
        queue = multiprocessing.Queue()
        process = multiprocessing.Process(target=self.open_file_dialog,args=(queue,))
        process.start()
        process.join() 
        result = queue.get()
        if result:
            dpg.set_value("filePathText",result)
        self.fileNotInSelection = True
    def select_file_thread(self):
        thread = threading.Thread(target=self.select_file)
        thread.start()
    def clossAddNewFileWindow(self):
            if self.fileNotInSelection:
                dpg.delete_item("addNewFileWindow")
                self.zender.resize(self.zender.fileBox,self.groupName)
    def addNewFile(self):
        if not dpg.does_item_exist('addNewFileWindow'):
            with dpg.child_window(tag="addNewFileWindow",width=550,height=400,border=False,parent=self.zender.fileBox) as elderChild:
                dpg.bind_item_theme(elderChild,self.childTheam((157, 104, 75, 255)))
                dpg.add_image_button(texture_tag="icon_cross",pos=(480,10),width=50, height=50, frame_padding=0, background_color=(157, 104, 75, 255),callback=self.clossAddNewFileWindow)
                text = dpg.add_text("Add File",pos=(265,50))
                dpg.bind_item_font(text,self.zender.fontSetUp)
                dpg.bind_item_theme(text, self.zender.textColorSetUp((0, 0, 0, 255))) 
                with dpg.child_window(width=365,height=50,pos=(30,150)) as filePath:
                    dpg.bind_item_theme(filePath,self.childTheam((117, 117, 117, 255)))
                    dpg.add_text("File Path",pos=(5,15),tag="filePathText")
                button = dpg.add_button(label="browse",width=100,height=50,pos=(400,150),tag="browseButton",callback=self.select_file_thread)
                dpg.bind_item_theme(button, self.zender.button2)
                dpg.bind_item_font(button, self.zender.fontSetUp)
                add_button = dpg.add_button(label="Add File",width=470,height=50,pos=(30,220))
                dpg.bind_item_theme(add_button, self.zender.button2)
                dpg.bind_item_font(add_button, self.zender.fontSetUp)
                info_text = dpg.add_text("info : The added file path is only saved in the database. If the file is deleted from the given location, it is highlighted in the interface and becomes inaccessible",pos=(30,300),wrap=470)
                dpg.bind_item_font(info_text, self.zender.fontSetUp)
                dpg.bind_item_theme(info_text, self.zender.textColorSetUp((0, 0, 0, 255)))
            self.zender.resize(self.zender.fileBox,self.groupName,"addNewFileWindow")
    def fetchData(self):
        self.groupName = []
        parent_width = dpg.get_item_width(self.zender.fileBox)
        if dpg.does_item_exist(self.zender.fileBox+"child"):
            dpg.delete_item(self.zender.fileBox+"child")
        files = [None, "file2.jpg", "file3.pdf", "file4.mp4", "file6.docx","file1.txt", "file2.jpg", "file3.pdf", "file4.mp4", "file5.zip", "file6.docx"]
        with dpg.child_window(tag=self.zender.fileBox+"child",parent=self.zender.accessFileWindowName,pos=(10,130),width=parent_width,border=False):
            with dpg.table(tag="tableInFileBox",header_row=False, resizable=False, pos=(100, 90)):
                for _ in range(3):
                    dpg.add_table_column()

                for i in range(0, len(files), 3):
                    with dpg.table_row():
                        for j in range(3):
                            if i == 0 and j == 0:
                                with dpg.group() as fileGroup:
                                    self.groupName.append(fileGroup)
                                    dpg.add_image_button(texture_tag="icon_add-file", width=100, height=100, frame_padding=0, background_color=(203, 184, 116, 255),callback=self.addNewFile)
                                    continue
                            if i + j < len(files):
                                with dpg.group() as fileGroup:
                                    self.groupName.append(fileGroup)
                                    dpg.add_image_button(texture_tag="icon_folder", width=100, height=100, frame_padding=0, background_color=(203, 184, 116, 255),user_data=files[i + j])
                                    text = dpg.add_text(files[i + j], wrap=100)
                                    dpg.bind_item_font(text,self.zender.fontSetUp)
                                    dpg.bind_item_theme(text, self.zender.textColorSetUp((0, 0, 0, 255))) 
        self.zender.resize(self.zender.fileBox,self.groupName)
    def fileBoxMain(self):
        if not dpg.does_item_exist(self.zender.fileBox):
            with dpg.window(tag=self.zender.fileBox,pos=(0, 0), no_title_bar=True, no_resize=True, no_move=True):
                dpg.add_image_button(texture_tag="icon_download",tag="zender_download_fileBox", width=50, height=50, frame_padding=0, background_color=(203, 184, 116, 255))
                dpg.add_image_button(texture_tag="icon_go_back",tag="back_icon_fileBox", width=50, height=50, frame_padding=0, background_color=(203, 184, 116, 255))
                self.fetchData()
                
                dpg.bind_theme(self.zender.WindowTheam)