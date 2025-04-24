import dearpygui.dearpygui as dpg
from accessFile import AccessFile
import queue
import threading
import time
class LoginToBox:
    def __init__(self):
        self.Queue = queue.Queue()
        self.click = True
        
    def hide_text(self):
        time.sleep(3)
        dpg.set_value("loginwarning", "")
    def notofication(self, text):
        dpg.set_value("loginwarning", text)
        thread = threading.Thread(target=self.hide_text)
        thread.start()
        
    def scanForLoginResponse(self):
        while True:
            response = self.Queue.get()
            if response:
                if response['status'] == 500:
                    self.notofication('Network erorr')
                elif response['status'] == 404:
                    self.notofication('The given data is not valid')
                elif response['status'] == 200:
                    files = response['replay']
                    publicKey = response['publicKey']
                    userId = self.info[0]
                    boxId = self.info[1]
                    password = self.info[2]
                    self.goToFileAccess(
                        files=files,
                        publicKey=publicKey,
                        userId=userId,
                        boxId=boxId,
                        password=password)
                self.click = True
    def loginToBox(self):
        if self.click:
            self.click = False
            userId = (dpg.get_value('userId')).strip()
            boxId = (dpg.get_value('boxId')).strip()
            password = (dpg.get_value('boxPassword')).strip()
            if '' in [userId,boxId,password]:
                self.notofication('The given data is not valid')
                self.click = True
                return
            self.info = (userId,boxId,password)
            self.zender.requestForLogin(userId,boxId,password,self.Queue)
        
    def goToFileAccess(self,files,publicKey,userId,boxId,password):
        if dpg.does_item_exist(self.zender.accessFileWindowName):
            dpg.delete_item(self.zender.accessFileWindowName)
        dpg.hide_item(self.zender.loginToBoxWindowName)
        self.AccessFileObj = AccessFile(
            fils=files,
            publicKey=publicKey,
            userId=userId,
            BoxId=boxId,
            Password=password)
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
                dpg.add_text('',tag="loginwarning")
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
                
                dpg.bind_item_theme('loginwarning', zender.textColorSetUp((255, 69, 0, 255)))
                dpg.bind_item_font("loginwarning", zender.large_font_max)
                dpg.bind_theme(zender.WindowTheam)
        zender.resize(zender.loginToBoxWindowName)