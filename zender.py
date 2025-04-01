import dearpygui.dearpygui as dpg #dependecy
from pathlib import Path
import os
from rezise import resizeElement
from history import History
from yourBox import YourBox
import pyperclip #dependecy
import asyncio


class ZenderGui:
    def __init__(self):
        self.BASE_DIR = Path(__file__).resolve().parent
        
        self.homeWindowName = "zender_home"
        self.loginToBoxWindowName = "loginToBox"
        self.accessFileWindowName = "accessFile"
        self.historyWindow = "history"
        self.yourBoxWindow = "YourBox"
        self.createBox = "createBox"
        self.fromWhere = None
        self.history = History()
        self.userId = 'DemoUser000001'
    async def hide_text(self, tag):
        await asyncio.sleep(2)
        dpg.set_value(tag, "")
    def resize(self,name,tagList=[],tag=None):
        resizeElement(name,self,tagList,tag)
        dpg.set_viewport_resize_callback(lambda: resizeElement(name,self,tagList,tag))
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
        if dpg.does_item_exist(self.historyWindow):
            dpg.hide_item(self.homeWindowName)
            dpg.show_item(self.historyWindow)
            self.resize(self.historyWindow)
        else:
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
    def setUpFont(self,size):
        with dpg.font_registry():
            large_font = dpg.add_font(os.path.join(self.BASE_DIR,"Arial.ttf"), size)
        return large_font
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
    def main_home(self):
        self.windowTheam()
        self.iconSetUp()
        self.inputDecine()
        self.fontSetUp = self.setUpFont(18)
        self.button1 = self.buttonTheam((157, 104, 75, 255))
        self.button2 = self.buttonTheam((108, 93, 78, 255))
    
        if not dpg.does_item_exist(self.homeWindowName):
            with dpg.window(tag=self.homeWindowName, label="Send your file", pos=(0, 0), no_title_bar=True, no_resize=True, no_move=True):
                dpg.add_text(f'User Id : {self.userId}',pos=(30,30),tag="userIdZender")
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