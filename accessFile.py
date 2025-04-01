import dearpygui.dearpygui as dpg

class AccessFile:
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
    def fileInfo(self,sender,app_data,user_data):
        def closeInfoWindow():
            dpg.hide_item('fileInfo')
        def editText(newTxt):
            return f'File name      : {newTxt}'
        if not dpg.does_item_exist('fileInfo'):
            with dpg.child_window(tag="fileInfo",width=350,height=300,border=False,parent=self.zender.accessFileWindowName) as elderChild:
                    dpg.bind_item_theme(elderChild,self.childTheam((157, 104, 75, 255)))
                    with dpg.group(tag='info',pos=(80,30)):
                        dpg.add_image_button(texture_tag="icon_cross",pos=(320,10),width=25, height=25, frame_padding=0, background_color=(157, 104, 75, 255),callback=closeInfoWindow)
                        dpg.add_text(editText(user_data),tag="fileNameInfo",wrap=270)
                        dpg.add_text('File size         : 2GB',tag="fileSizeInfo",wrap=270)
                        dpg.add_text('Upload Date  : 30/12/2024',tag="dateInfo",wrap=270)
                    dpg.add_button(label="Download", tag="download_button", pos=(110, 170), width=140, height=60)
            dpg.bind_item_theme("download_button",self.zender.button2)
            dpg.bind_item_font("download_button", self.zender.fontSetUp)
            dpg.bind_item_font("fileNameInfo", self.zender.fontSetUp)
            dpg.bind_item_font("fileSizeInfo", self.zender.fontSetUp)
            dpg.bind_item_font("dateInfo", self.zender.fontSetUp)
        elif not dpg.is_item_shown('fileInfo'):
            dpg.show_item('fileInfo')
            dpg.set_value('fileNameInfo',editText(user_data))
        self.zender.resize(self.zender.accessFileWindowName,self.groupName,"fileInfo")
    def fetchData(self):
        self.groupName = []
        parent_width = dpg.get_item_width(self.zender.accessFileWindowName)
        if dpg.does_item_exist(self.zender.accessFileWindowName+"child"):
            dpg.delete_item(self.zender.accessFileWindowName+"child")
        files = ["file1.txt", "file2.jpg", "file3.pdf", "file4.mp4", "fifnkfhfjbfhbfhble5.zip", "file6.docx","file1.txt", "file2.jpg", "file3.pdf", "file4.mp4", "file5.zip", "file6.docx"]
        with dpg.child_window(tag=self.zender.accessFileWindowName+"child",parent=self.zender.accessFileWindowName,pos=(10,130),width=parent_width,border=False):
            with dpg.table(tag="table",header_row=False, resizable=False, pos=(100, 90)):
                for _ in range(3):
                    dpg.add_table_column()

                for i in range(0, len(files), 3):
                    with dpg.table_row():
                        for j in range(3):
                            if i + j < len(files):
                                gorupName = f'fileGroup{i+j}'
                                with dpg.group(tag=gorupName) as fileGroup:
                                    self.groupName.append(fileGroup)
                                    dpg.add_image_button(texture_tag="icon_folder", width=100, height=100, frame_padding=0, background_color=(203, 184, 116, 255),callback=self.fileInfo,user_data=files[i + j])
                                    dpg.add_text(files[i + j],tag=f'fileName{i+j}', wrap=100)
                                    dpg.bind_item_font(f'fileName{i+j}',self.zender.fontSetUp)
                                    dpg.bind_item_theme(f'fileName{i+j}', self.zender.textColorSetUp((0, 0, 0, 255))) 
        self.zender.resize(self.zender.accessFileWindowName,self.groupName)
    def accessFileMain(self,zender):
        self.zender = zender
        if not dpg.does_item_exist(self.zender.accessFileWindowName):
            with dpg.window(tag=self.zender.accessFileWindowName,pos=(0, 0), no_title_bar=True, no_resize=True, no_move=True):
                dpg.add_image_button(texture_tag="icon_download",tag="zender_download_accessFile", width=50, height=50, frame_padding=0, background_color=(203, 184, 116, 255),callback=self.goToHistory)
                dpg.add_image_button(texture_tag="icon_go_back",tag="back_icon_access", width=50, height=50, frame_padding=0, background_color=(203, 184, 116, 255),callback=self.backToHome)
                
                
                self.fetchData()
                
            dpg.bind_theme(self.zender.WindowTheam)
        # self.zender.resize(self.zender.accessFileWindowName,self.groupName)
        