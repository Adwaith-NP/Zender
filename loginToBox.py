import dearpygui.dearpygui as dpg
from accessFile import AccessFile
import queue
import threading
class LoginToBox:
    def __init__(self):
        self.Queue = queue.Queue()
    def scanForLoginResponse(self):
        while True:
            response = self.Queue.get()
            if response:
                print(response)
    def loginToBox(self):
        userId = dpg.get_value('userId')
        boxId = dpg.get_value('boxId')
        password = dpg.get_value('boxPassword')
        self.zender.requestForLogin(userId,boxId,password,self.Queue)
        
    def goToFileAccess(self):
        if dpg.does_item_exist(self.zender.accessFileWindowName):
            dpg.delete_item(self.zender.accessFileWindowName)
        dpg.hide_item(self.zender.loginToBoxWindowName)
        self.AccessFileObj = AccessFile()
        self.AccessFileObj.accessFileMain(zender=self.zender)
    def backToHome(self):
        dpg.hide_item(self.zender.loginToBoxWindowName)
        dpg.show_item(self.zender.homeWindowName)
        self.zender.resize(self.zender.homeWindowName)
    def loginToBoxMain(self,zender):
        threading.Thread(target=self.scanForLoginResponse,daemon=True).start()
        self.zender = zender
        if not dpg.does_item_exist(zender.loginToBoxWindowName):
            with dpg.window(tag=zender.loginToBoxWindowName, pos=(0, 0), no_title_bar=True, no_resize=True, no_move=True):
                dpg.add_input_text(tag="userId",pos=(80,60),width=390,hint='User Id')
                dpg.add_input_text(tag="boxId",pos=(80,60),width=390,hint='Box Id')
                dpg.add_input_text(tag="boxPassword",pos=(80,60),width=390,hint='Password')
                dpg.add_button(label="Access The Box", tag="accessBoc", pos=(0, 0), width=390, height=60,callback=self.loginToBox)
                dpg.add_image_button(texture_tag="icon_go_back",tag="back_icon", width=50, height=50, frame_padding=0, background_color=(203, 184, 116, 255),callback=self.backToHome)
                
                dpg.bind_item_theme("userId", zender.input_theme)
                dpg.bind_item_font("userId", zender.fontSetUp)
                dpg.bind_item_theme("boxId", zender.input_theme)
                dpg.bind_item_font("boxId", zender.fontSetUp)
                dpg.bind_item_theme("boxPassword", zender.input_theme)
                dpg.bind_item_font("boxPassword", zender.fontSetUp)
                dpg.bind_item_theme("accessBoc",zender.button2)
                dpg.bind_item_font("accessBoc", zender.fontSetUp)
                dpg.bind_theme(zender.WindowTheam)
        zender.resize(zender.loginToBoxWindowName)