import dearpygui.dearpygui as dpg #dependecy
from pathlib import Path
import os
from rezise import resizeElement
from history import History
import pyperclip #dependecy
from PIL import Image #imported pip install pillow
import time
from accessRelayServer.dataTransfer import RequestHandling,Request
import threading
import time
import json
import requests
import random
import string
from cryptographyFiles.publicAndPrivatKey import createNewKey

class DownloadInfoThread:
    def __init__(self,fileName,fileSize):
        self.fileName = fileName
        self.fileZise = fileSize
        self.speed = None
        self.totalDownlaod = None
        self.startDownloading = True
        self.completed = False

class DownloadQueue:
    def __init__(self):
        self.threaMemory = []
    def setUpDownloadInfoThread(self,fileName,fileSize):
        instance = DownloadInfoThread(fileName=fileName,fileSize=fileSize)
        self.threaMemory.append(instance)
        return instance
        


class ZenderGui:
    def __init__(self):
        self.BASE_DIR = Path(__file__).resolve().parent
        self.homeWindowName = "zender_home"
        self.loginToBoxWindowName = "loginToBox"
        self.accessFileWindowName = "accessFile"
        self.historyWindow = "history"
        self.yourBoxWindow = "YourBox"
        self.createBox = "createBox"
        self.fileBox = "fileBox"
        self.fromWhere = None
        self.history = History()
        self.userId = 'Connect to network and restart'
        self.stopSpinning = True
        self.parentWindow = self.homeWindowName
        self.IP = '192.168.190.49:8080'#'orange-doodle-r4gv66rwqvjv35jwj-8000.app.github.dev'
        
        downloadQueue = DownloadQueue()
        self.downloadQ = downloadQueue
        
        self.createNewKey()
        
    def createNewKey(self):
        publicKey = os.path.join(self.BASE_DIR,'accessRelayServer/public_key.pem')
        privateKey = os.path.join(self.BASE_DIR,'accessRelayServer/private_key.pem')
        createNewKey(privateKey,publicKey)
    def generate_secret_key(self,length=10):
        characters = string.ascii_letters + string.digits + string.punctuation
        secret_key = ''.join(random.choice(characters) for _ in range(length))
        return secret_key
    def accountSetUp(self):
        jsonFile = os.path.join(self.BASE_DIR,'account.json')
        with open(jsonFile,'r') as file:
            jsonData = json.load(file)
        if 'status' in jsonData and not jsonData['status']:
            try:
                response = requests.get(f'http://{self.IP}/userId/',timeout=5)
            except:
                return
            if response:
                data = response.json()  # 👈 This parses the JSON
                newUser = data['newUserId']
                SECRET_KEY = self.generate_secret_key()
                jsonData['status'] = True
                jsonData['userId'] = newUser
                jsonData['SECRET_KEY'] = SECRET_KEY
                with open(jsonFile, "w") as file:
                    json.dump(jsonData, file)
                self.userId = newUser
        else:
            self.userId = jsonData['userId']
        print(4)
        
            
            
    def connectToRelayServer(self):
        url = f"ws://{self.IP}/ws/relay/{self.userId}/"
        self.connection = RequestHandling(self.userId,url,self.BASE_DIR,self.IP)
        self.connection.startScaningThread()
        
    def requestForLogin(self,senderId,boxId,password,Queue):
        request = Request(self.userId,self.BASE_DIR,Queue,self.IP)
        request.loginRequestThread(senderId,boxId,password)
        
    def fileRequest(self,userId,token,fileId,Queue,fileName,password,downloadQ):
        request = Request(self.userId,self.BASE_DIR,Queue,self.IP)
        request.fileRequestThread(userId,token,fileId,fileName,password,downloadQ)
        
    def noNetwork(self):
        #OnlineOrOffline
        onlineTxstSetUp = False
        offLineTextSetUp = False
        while True:
            time.sleep(4)
            connection = self.connection.relayConnection
            if not connection:
                self.connectToRelayServer()
                if not offLineTextSetUp:
                    dpg.set_value('OnlineOrOffline','Offline')
                    dpg.bind_item_theme('OnlineOrOffline', self.textColorSetUp((255, 0, 0, 255))) 
                    offLineTextSetUp = True
                    onlineTxstSetUp = False
            elif not onlineTxstSetUp:
                dpg.set_value('OnlineOrOffline','Online')
                dpg.bind_item_theme('OnlineOrOffline', self.textColorSetUp((100, 250, 100, 200))) 
                onlineTxstSetUp = True
                offLineTextSetUp = False
            
    def childTheam(self,color):
        with dpg.theme() as child_theme:
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg,color)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 15)
        return child_theme
    
    def loadingWindow(self, parentWindow, text , extra = None,nameSpace = "LD"):
        path = os.path.join(self.BASE_DIR, "icon/loading.png")
        original_image = Image.open(path).convert("RGBA")
        width, height = original_image.size
        rotation = 0
        
        icon_tag = "loading_icon"+nameSpace
        notofocation_tag = "notification"+nameSpace
        loading_tag = "loading"+nameSpace


        def loadImage(rotation_angle):
            rotated = original_image.rotate(rotation_angle, expand=False).convert("RGBA")
            img_data = rotated.tobytes()
            if dpg.does_item_exist(icon_tag):
                dpg.delete_item(icon_tag)
            with dpg.texture_registry():
                dpg.add_static_texture(width, height, img_data, tag=icon_tag)

        def spin_loader():
            nonlocal rotation
            if self.stopSpinning:
                dpg.delete_item(notofocation_tag)
                return  # Exit if window was closed
        
            if dpg.does_item_exist(loading_tag):
                dpg.delete_item(loading_tag)
            loadImage(rotation)
                
            dpg.add_image(icon_tag, tag=loading_tag, width=80, height=80, pos=(120, 110),parent=notofocation_tag)
            rotation = (rotation + 10) % 360
            time.sleep(0.05)
            dpg.set_frame_callback(dpg.get_frame_count() + 1, spin_loader)  # schedule next frame

        with dpg.child_window(width=300, height=300, border=False, parent=parentWindow, tag=notofocation_tag) as elderChild:
            dpg.bind_item_theme(elderChild, self.childTheam((78, 93, 108, 255)))
            text_width, _ = dpg.get_text_size(text)
            center_x = (300 - text_width) / 2
            text_item = dpg.add_text(text, pos=(center_x, 10),tag="loadingText"+nameSpace)
            dpg.bind_item_font(text_item, self.fontSetUp)
            dpg.bind_item_theme(text_item, self.textColorSetUp((0, 0, 0, 255)))
            self.resize(self.fileBox,extra[0], extra[1], notification = [nameSpace])
        spin_loader()
        
    def resize(self,name,tagList=[],tag=None,notification=False):
        resizeElement(name,self,tagList,tag,notification)
        dpg.set_viewport_resize_callback(lambda: resizeElement(name,self,tagList,tag,notification))
    def inputDecine(self):
        with dpg.theme() as input_theme:
            self.input_theme = input_theme
            with dpg.theme_component(dpg.mvInputText):
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (50, 50, 50, 255))  # Dark background
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255, 255))  # White text
                dpg.add_theme_color(dpg.mvThemeCol_Border, (200, 200, 200, 255))  # Border color
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)  # Rounded corners
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 5)  # Padding inside box
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 10)
    def copyText(self):
        pyperclip.copy(self.userId)
    def textColorSetUp(self,color):
        with dpg.theme() as black_text_theme:
            with dpg.theme_component(dpg.mvText):
                dpg.add_theme_color(dpg.mvThemeCol_Text, color)
        return black_text_theme
    def moveHistoryBox(self):
        self.fromWhere = self.homeWindowName
        self.history.historyManin(zender=self)
    def moveToBox(self):
        from loginToBox import LoginToBox
        if dpg.does_item_exist(self.loginToBoxWindowName):
            dpg.hide_item(self.homeWindowName)
            dpg.show_item(self.loginToBoxWindowName)
            self.resize(self.loginToBoxWindowName)
        else:
            dpg.hide_item(self.homeWindowName)
            obj = LoginToBox()
            obj.loginToBoxMain(zender=self)
    def moveToYourBox(self):
        from yourBox import YourBox
        if dpg.does_item_exist(self.yourBoxWindow):
            dpg.hide_item(self.homeWindowName)
            dpg.show_item(self.yourBoxWindow)
            self.resize(self.yourBoxWindow)
        else:
            dpg.hide_item(self.homeWindowName)
            obj = YourBox()
            obj.yourBoxMain(zender=self)
    def setUpFont(self):
        with dpg.font_registry():
            self.fontSetUp = dpg.add_font(os.path.join(self.BASE_DIR,"Arial.ttf"), 18)
            self.large_font_max = dpg.add_font(os.path.join(self.BASE_DIR,"Arial.ttf"), 28)
    def windowTheam(self):
        with dpg.theme() as window_theme:
            self.WindowTheam = window_theme
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (203, 184, 116, 255))
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (203, 184, 116, 255))
    def buttonTheam(self,color):
        with dpg.theme() as name:
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, color)  # Background color
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, color[:3]+(color[-1]-80,))  # Hover color
                    dpg.add_theme_color(dpg.mvThemeCol_Text,(0,0,0,255))
                    dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)  # Rounded corners
                    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 10)  # Padding
        return name
    def iconSetUp(self):
        with dpg.texture_registry():
            width, height, channels, data = dpg.load_image(os.path.join(self.BASE_DIR,"icon/download.png"))
            dpg.add_static_texture(width, height, data, tag="icon_download")
            width, height, channels, data = dpg.load_image(os.path.join(self.BASE_DIR,"icon/back-arrow.png"))
            dpg.add_static_texture(width, height, data, tag="icon_go_back")
            width, height, channels, data = dpg.load_image(os.path.join(self.BASE_DIR,"icon/folder.png"))
            dpg.add_static_texture(width, height, data, tag="icon_folder")
            width, height, channels, data = dpg.load_image(os.path.join(self.BASE_DIR,"icon/history.png"))
            dpg.add_static_texture(width, height, data, tag="icon_history")
            width, height, channels, data = dpg.load_image(os.path.join(self.BASE_DIR,"icon/cross.png"))
            dpg.add_static_texture(width, height, data, tag="icon_cross")
            width, height, channels, data = dpg.load_image(os.path.join(self.BASE_DIR,"icon/copy.png"))
            dpg.add_static_texture(width, height, data, tag="icon_copy")
            width, height, channels, data = dpg.load_image(os.path.join(self.BASE_DIR,"icon/padlock.png"))
            dpg.add_static_texture(width, height, data, tag="icon_lock")
            width, height, channels, data = dpg.load_image(os.path.join(self.BASE_DIR,"icon/unlock.png"))
            dpg.add_static_texture(width, height, data, tag="icon_unlock")
            width, height, channels, data = dpg.load_image(os.path.join(self.BASE_DIR,"icon/Addfolde.png"))
            dpg.add_static_texture(width, height, data, tag="icon_Addfolde")
            width, height, channels, data = dpg.load_image(os.path.join(self.BASE_DIR,"icon/box.png"))
            dpg.add_static_texture(width, height, data, tag="icon_box")
            width, height, channels, data = dpg.load_image(os.path.join(self.BASE_DIR,"icon/add-post.png"))
            dpg.add_static_texture(width, height, data, tag="icon_add-file")
    
    def main_home(self):
        self.windowTheam()
        self.iconSetUp()
        self.inputDecine()
        self.setUpFont()
        threading.Thread(target=self.accountSetUp).start()
        self.connectToRelayServer()
        threading.Thread(target=self.noNetwork, daemon=True).start()
        self.button1 = self.buttonTheam((157, 104, 75, 255))
        self.button2 = self.buttonTheam((108, 93, 78, 255))
        if not dpg.does_item_exist(self.homeWindowName):
            with dpg.window(tag=self.homeWindowName, label="Send your file", pos=(0, 0), no_title_bar=True, no_resize=True, no_move=True):
                dpg.add_text(f'User Id : {self.userId}',pos=(30,30),tag="userIdZender")
                dpg.add_text('Status : ',pos=(30,60),tag='status')
                dpg.add_text('Connecting...',tag='OnlineOrOffline',pos=(100,60))
                dpg.add_button(label="Access Box", tag="zender_box", pos=(0, 0), width=140, height=60,callback = self.moveToBox)
                dpg.add_button(label="Your Box", tag="zender_your_box", pos=(0, 0), width=140, height=60,callback=self.moveToYourBox)
                dpg.add_image_button(texture_tag="icon_download",tag="zender_download", width=50, height=50, frame_padding=0, background_color=(203, 184, 116, 255),callback=self.moveHistoryBox)
                dpg.add_image_button(texture_tag="icon_copy",tag="zender_copy", width=20, height=20, frame_padding=0, background_color=(203, 184, 116, 255),callback=self.copyText)

                
                dpg.bind_item_theme("zender_box",self.button1)
                dpg.bind_item_font("zender_box", self.fontSetUp)
                dpg.bind_item_theme("zender_your_box",self.button2)
                dpg.bind_item_font("zender_your_box", self.fontSetUp)
                dpg.bind_item_font("userIdZender", self.fontSetUp)
                dpg.bind_item_theme('userIdZender', self.textColorSetUp((0, 0, 0, 255))) 
                dpg.bind_item_font("status", self.fontSetUp)
                dpg.bind_item_theme('status', self.textColorSetUp((0, 0, 0, 255))) 
                dpg.bind_item_font("OnlineOrOffline", self.fontSetUp)
                dpg.bind_item_theme('OnlineOrOffline', self.textColorSetUp((0, 0, 0, 255))) 
                dpg.add_text("info", tag="info_txt_zender", show=False)
                dpg.bind_theme(self.WindowTheam)
        self.resize(self.homeWindowName)
    def run(self):
        
        dpg.create_context()
        dpg.create_viewport(title='ZENDER', width=850, height=600)
        dpg.setup_dearpygui()
        self.main_home()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
        
if __name__ == "__main__":
    zender = ZenderGui()
    zender.run()