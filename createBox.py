import dearpygui.dearpygui as dpg
import threading
from database.dataBase import DataBase
import bcrypt
import asyncio
import time

class CreateBox:
    def __init__(self):
        self.dbObj = DataBase()
    def backToBoxWindow(self):
        dpg.hide_item(self.zender.createBox)
        dpg.show_item(self.zender.yourBoxWindow)
        self.zender.resize(self.zender.yourBoxWindow)
    def hide_text(self, tag):
        time.sleep(3)
        dpg.set_value(tag, "")
    def notofication(self, text):
        dpg.set_value("warning", text)
        thread = threading.Thread(target=self.hide_text, args=("warning",))
        thread.start()
    def createBox(self):
        boxId = ((dpg.get_value('boxId_create')).strip()).lower()
        password = dpg.get_value('boxPassword_create').strip()
        enc = dpg.get_value('encryption_checkbox')
        if len(password) < 6:
            self.notofication("warning : password must be 6 characters at least")
            return
        if not boxId:
            self.notofication("warning : Enter boxID")
            return
        if enc:
            salt = bcrypt.gensalt()
            password = bcrypt.hashpw(password.encode(), salt)
        result = self.dbObj.add_box(boxId,password,enc)
        if not result:
            self.notofication("Error: Box name already exists!")
        else:
            self.add_box(name = boxId,enc = enc ,password = password , boxId = result,new = True)
            self.backToBoxWindow()
    def run_async_task(self, coroutine):
        try:
            loop = asyncio.get_running_loop()  # Get current event loop
        except RuntimeError:
            loop = asyncio.new_event_loop()   # If none exists, create one
            asyncio.set_event_loop(loop)

        loop.create_task(coroutine)
            
    def createBoxMain(self,zender,add_box):
        self.zender = zender
        self.add_box = add_box
        if not dpg.does_item_exist(zender.createBox):
            with dpg.window(tag=zender.createBox, pos=(0, 0), no_title_bar=True, no_resize=True, no_move=True):
                dpg.add_image(texture_tag="icon_box",tag="box_icon", width=80, height=80)
                dpg.add_input_text(tag="boxId_create",pos=(80,60),width=390,hint='Box Id')
                dpg.add_input_text(tag="boxPassword_create",pos=(80,60),width=390,hint='Password')
                dpg.add_button(label="Create Box", tag="create_box", pos=(0, 0), width=390, height=60,callback=self.createBox)
                dpg.add_text('End to end encryption',tag='encText')
                dpg.add_text('',tag='warning',wrap=410)
                dpg.add_checkbox(user_data=None,tag="encryption_checkbox")
                dpg.add_image_button(texture_tag="icon_go_back",tag="back_icon_create", width=50, height=50, frame_padding=0, background_color=(203, 184, 116, 255),callback=self.backToBoxWindow)
                dpg.add_text('info : If encryption is turned ON, you MUST enter the correct password to access the box. Failure to provide the password will result in complete inaccessibility!',tag='infoText',wrap=400)
                
                dpg.bind_item_theme("boxId_create", zender.input_theme)
                dpg.bind_item_font("boxId_create", zender.fontSetUp)
                dpg.bind_item_theme("boxPassword_create", zender.input_theme)
                dpg.bind_item_font("boxPassword_create", zender.fontSetUp)
                dpg.bind_item_theme("create_box",zender.button2)
                dpg.bind_item_font("create_box", zender.fontSetUp)
                dpg.bind_item_font("encText", zender.fontSetUp)
                dpg.bind_item_theme('encText', zender.textColorSetUp((0, 0, 0, 255))) 
                dpg.bind_item_theme('infoText', zender.textColorSetUp((0, 0, 0, 255)))
                dpg.bind_item_theme('warning', zender.textColorSetUp((255, 69, 0, 255)))
                dpg.bind_item_font("warning", zender.fontSetUp)
            dpg.bind_theme(self.zender.WindowTheam)
        zender.resize(zender.createBox)