import dearpygui.dearpygui as dpg
import threading
import queue
import time
class AccessFile:
    def __init__(self,fils,publicKey,userId,BoxId,Password,token):
        self.userId = userId
        self.BoxId = BoxId
        self.password = Password
        self.publicKey = publicKey
        self.files = fils
        self.token = token
        self.childWindowNotShown = True
        self.fileCount = 0
        self.queue = queue.Queue()
    def hide_text(self):
        time.sleep(3)
        dpg.set_value("accesswarning", "")
    def notofication(self, text):
        dpg.set_value("accesswarning", text)
        thread = threading.Thread(target=self.hide_text)
        thread.start()
    def goToHistory(self):
        self.zender.fromWhere = self.zender.accessFileWindowName
        if dpg.does_item_exist(self.zender.historyWindow):
            dpg.hide_item(self.zender.accessFileWindowName)
            dpg.show_item(self.zender.historyWindow)
            self.zender.resize(self.zender.historyWindow)
        else:
            self.zender.history.historyManin(zender=self.zender)
    def backToHome(self):
        dpg.hide_item(self.zender.accessFileWindowName)
        dpg.show_item(self.zender.homeWindowName)
        self.zender.resize(self.zender.homeWindowName)
    def childTheam(self,color):
        with dpg.theme() as child_theme:
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg,color)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 15)
        return child_theme
    
    def clossFileInfoWindow(self):
            self.childWindowNotShown = True
            dpg.delete_item("fileInfo")
            self.zender.resize(self.zender.accessFileWindowName,self.groupName)
            
    def scanForNotofiacation(self):
        while True:
            response = self.queue.get()
            if response:
                if response['status'] == 200:
                    self.notofication('download started visit history')
                if response['status'] == 404:
                    self.notofication('some error are occured log again')
            
    def download(self,sender, app_data, user_data):
        self.zender.fileRequest(self.userId,self.token,user_data[0],self.queue,user_data[1],self.password)
        
    def fileInfo(self,sender, app_data, user_data):
        ## demo : [120, 'WhatsApp Image 2025-04-21 at 22.15.28.jpeg', '144.46 KB', '2025-04-21 17:30:18', 13]
        if not dpg.does_item_exist('fileInfo') and self.childWindowNotShown:
            self.childWindowNotShown = False
            with dpg.child_window(tag="fileInfo",width=550,height=400,border=False,parent=self.zender.accessFileWindowName) as elderChild:
                dpg.bind_item_theme(elderChild,self.zender.childTheam((157, 104, 75, 255)))
                dpg.add_image_button(texture_tag="icon_cross",pos=(480,10),width=50, height=50, frame_padding=0, background_color=(157, 104, 75, 255),callback=self.clossFileInfoWindow)
                text = dpg.add_text("File Info",pos=(265,50))
                dpg.bind_item_font(text,self.zender.fontSetUp)
                dpg.bind_item_theme(text, self.zender.textColorSetUp((0, 0, 0, 255))) 
                with dpg.group(pos=(50,150)) as group:
                    dpg.add_text("File name")
                    with dpg.child_window(width=350,height=40,pos=(150,143)) as fileNameWindow:
                        dpg.bind_item_theme(fileNameWindow,self.zender.childTheam((0, 0, 0, 255)))
                        text = dpg.add_text(user_data[1],pos=(5,8))
                        dpg.bind_item_font(text,self.zender.fontSetUp)
                        dpg.bind_item_theme(text, self.zender.textColorSetUp((255, 255, 255, 255))) 
                    dpg.add_text("File size",pos=(50,210))
                    with dpg.child_window(width=350,height=40,pos=(150,200)) as fileNameWindow:
                        dpg.bind_item_theme(fileNameWindow,self.zender.childTheam((0, 0, 0, 255)))
                        text = dpg.add_text(user_data[2],pos=(5,8))
                        dpg.bind_item_font(text,self.zender.fontSetUp)
                        dpg.bind_item_theme(text, self.zender.textColorSetUp((255, 255, 255, 255))) 
                    dpg.add_text(f"Upload date",pos=(50,267))
                    with dpg.child_window(width=350,height=40,pos=(150,257)) as fileNameWindow:
                        dpg.bind_item_theme(fileNameWindow,self.zender.childTheam((0, 0, 0, 255)))
                        text = dpg.add_text(user_data[3],pos=(5,8))
                        dpg.bind_item_font(text,self.zender.fontSetUp)
                        dpg.bind_item_theme(text, self.zender.textColorSetUp((255, 255, 255, 255))) 
                    dpg.bind_item_font(group,self.zender.fontSetUp)
                    dpg.bind_item_theme(group, self.zender.textColorSetUp((0, 0, 0, 255))) 
                button = dpg.add_button(label="Download",width=300,height=50,pos=(125,330),callback=self.download,user_data=(user_data[0],user_data[1]))
                dpg.bind_item_theme(button, self.zender.buttonTheam((78, 93, 108, 255)))
                dpg.bind_item_font(button,self.zender.fontSetUp)
            self.zender.resize(self.zender.accessFileWindowName,self.groupName,"fileInfo")
 

    def addItemsInTeble(self,data):
        if self.fileCount > 2:
            self.fileCount = 0

            with dpg.table_row(parent=self.table) as table:
                self.tableInstance = table
        with dpg.group(parent=self.tableInstance) as fileGroup:
                                label = data[1].lower()
                                if len(label) > 15:
                                    label = label[:15] + "..."
                                dpg.add_image_button(texture_tag="icon_folder", width=100, height=100, frame_padding=0, background_color=(203, 184, 116, 255),callback=self.fileInfo,user_data=data)
                                text = dpg.add_text(label, wrap=100)
                                dpg.bind_item_font(text,self.zender.fontSetUp)
                                dpg.bind_item_theme(text, self.zender.textColorSetUp((0, 0, 0, 255))) 
        self.groupName.append(fileGroup)
        self.fileCount = self.fileCount + 1
    
    def fetchData(self):
        self.groupName = []
        parent_width = dpg.get_item_width(self.zender.accessFileWindowName)
        with dpg.child_window(parent=self.zender.accessFileWindowName,pos=(10,130),width=parent_width,border=False):
            with dpg.table(header_row=False, resizable=False, pos=(100, 90)) as table:
                self.table = table
                for _ in range(3):
                    dpg.add_table_column()
                with dpg.table_row(parent=self.table) as table:
                    self.tableInstance = table
                for file in self.files:
                    self.addItemsInTeble(file)
        self.zender.resize(self.zender.accessFileWindowName,self.groupName)
        
            
        
    def accessFileMain(self,zender):
        threading.Thread(target=self.scanForNotofiacation,daemon=True).start()
        self.zender = zender
        if not dpg.does_item_exist(self.zender.accessFileWindowName):
            with dpg.window(tag=self.zender.accessFileWindowName,pos=(0, 0), no_title_bar=True, no_resize=True, no_move=True):
                dpg.add_image_button(texture_tag="icon_download",tag="zender_download_accessFile", width=50, height=50, frame_padding=0, background_color=(203, 184, 116, 255),callback=self.goToHistory)
                dpg.add_image_button(texture_tag="icon_go_back",tag="back_icon_access", width=50, height=50, frame_padding=0, background_color=(203, 184, 116, 255),callback=self.backToHome)
                dpg.add_text("",pos=(70,20),tag='accesswarning')
                dpg.bind_theme(self.zender.WindowTheam)
                dpg.bind_item_theme('accesswarning', zender.textColorSetUp((255, 69, 0, 255)))
                dpg.bind_item_font("accesswarning", zender.large_font_max)
        self.zender.resize(self.zender.accessFileWindowName)
        self.fetchData()
    
        