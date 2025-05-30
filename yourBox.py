import dearpygui.dearpygui as dpg
from createBox import CreateBox
from database.dataBase import DataBase
from fileBox import FileBox

class YourBox:
    def __init__(self):
        self.count = 0
        self.boxData = {}
        self.boxInstance = {}
    def toBox(self,data):
        if dpg.does_item_exist(self.zender.fileBox):
            dpg.delete_item(self.zender.fileBox)
        obj = FileBox(boxId=data[0],boxName=data[1],encrypt=data[2],password=data[3],zender=self.zender)
        obj.fileBoxMain()
    def createBox(self):
        dpg.hide_item(self.zender.yourBoxWindow)
        if not dpg.does_item_exist(self.zender.createBox):
            obj = CreateBox()
            obj.createBoxMain(zender=self.zender,add_box=self.createGroup)
        else:
            dpg.show_item(self.zender.createBox)
            dpg.set_value('boxId_create','')
            dpg.set_value('boxPassword_create','')
            dpg.set_value('encryption_checkbox',False)
        self.zender.resize(self.zender.createBox)
    def moveHistoryBox(self):
        self.zender.fromWhere = self.zender.yourBoxWindow
        self.zender.history.historyManin(zender=self.zender)
    def backToHome(self):
        dpg.hide_item(self.zender.yourBoxWindow)
        dpg.show_item(self.zender.homeWindowName)
        self.zender.resize(self.zender.homeWindowName)
    def childTheam(self,color):
        with dpg.theme() as child_theme:
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg,color)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 15)
        return child_theme
    def createGroup(self,name,enc,boxId,password,new = False):
        self.count = self.count + 1
        self.boxData[self.count] = [boxId,name,enc,password]
        dpg.add_child_window(width=300, height=4, border=False,parent="boxChildWindow")
        with dpg.child_window(tag=f"childBoxSelection{self.count}",width=480,height=60,no_scrollbar=True, no_scroll_with_mouse=True,parent="boxChildWindow") as child:
            dpg.bind_item_theme(child,self.childTheam((174, 136, 83, 255)))
            section_width = 450 // 3
            with dpg.group(horizontal=True):
                with dpg.child_window(width=section_width*2, height=45, border=True,tag=f"childBoxSelection{self.count}ch1"):
                    dpg.add_spacer(height=1)
                    text_id = dpg.add_text(name)
                    dpg.bind_item_theme(text_id, self.zender.textColorSetUp((0, 0, 0, 255))) 
                    dpg.bind_item_font(text_id, self.zender.fontSetUp)
                
                if enc:
                    with dpg.child_window(width=section_width, height=45, border=True,tag=f"childBoxSelection{self.count}ch2"):
                        dpg.add_spacer(height=1)
                        dpg.add_image(texture_tag="icon_lock", width=25, height=25,pos=(65,10))
                else:
                    with dpg.child_window(width=section_width, height=45, border=True,tag=f"childBoxSelection{self.count}ch2"):
                        dpg.add_spacer(height=1)
                        dpg.add_image(texture_tag="icon_unlock", width=25, height=25,pos=(65,10))
            if new:
                with dpg.handler_registry():
                    dpg.add_mouse_click_handler(callback=self.savedFunction(f"childBoxSelection{self.count}",self.count))
                 
    def listBox(self):
        db = DataBase()
        box = db.return_data_in_DB()
        for data in box:
            self.createGroup(name = data[1],enc = data[3],boxId = data[0],password=data[2])
    def yourBoxMain(self,zender):
        self.zender = zender
        if not dpg.does_item_exist(self.zender.yourBoxWindow):
            with dpg.window(tag=self.zender.yourBoxWindow,pos=(0, 0), no_title_bar=True, no_resize=True, no_move=True):
                
                dpg.add_image_button(texture_tag="icon_download",tag="zender_download_yourBox", width=50, height=50, frame_padding=0, background_color=(203, 184, 116, 255),callback=self.moveHistoryBox)
                dpg.add_image_button(texture_tag="icon_go_back",tag="back_icon_yourBox", width=50, height=50, frame_padding=0, background_color=(203, 184, 116, 255),callback=self.backToHome)
                
                parent_width = dpg.get_item_width(self.zender.yourBoxWindow)
                with dpg.child_window(tag="boxChildWindow",border=False,width=parent_width) as elderChild:
                    dpg.bind_item_theme(elderChild,self.childTheam((203, 184, 116, 255)))
                    with dpg.child_window(width=480,height=60,no_scrollbar=True, no_scroll_with_mouse=True,tag="ChildChildWindow") as oldChild:
                                        dpg.bind_item_theme(oldChild,self.childTheam((174, 136, 83, 255)))
                                        dpg.add_image_button(texture_tag="icon_Addfolde",pos=(215,5),width=50, height=50, frame_padding=0, background_color=(174, 136, 83, 255),callback=self.createGroup)
                    self.listBox()
            dpg.bind_theme(self.zender.WindowTheam)
        zender.resize(zender.yourBoxWindow)
        def make_window_click_callback(tag,count):
            if tag == "ChildChildWindow":
                def callback(sender, app_data):
                    if dpg.is_item_hovered(tag):
                        self.createBox()
                return callback
            else:
                def callback(sender, app_data):
                        if dpg.is_item_hovered(tag) or dpg.is_item_hovered(tag+"ch1") or dpg.is_item_hovered(tag+"ch2"):
                            self.toBox(self.boxData[count])
                return callback
        self.savedFunction = make_window_click_callback

        with dpg.handler_registry():
            dpg.add_mouse_click_handler(callback=make_window_click_callback("ChildChildWindow",None))
            for count in range(1,self.count+1):
                dpg.add_mouse_click_handler(callback=make_window_click_callback(f"childBoxSelection{count}",count))