import dearpygui.dearpygui as dpg
from accessFile import AccessFile
class History:
    def goBack(self):
        def goTo(toWhere):
            dpg.hide_item(self.zender.historyWindow)
            dpg.show_item(toWhere)
            self.zender.resize(toWhere)
        if self.zender.fromWhere == "accessFile":
            dpg.delete_item(self.zender.accessFileWindowName)
            dpg.hide_item(self.zender.loginToBoxWindowName)
            self.AccessFileObj = AccessFile()
            self.AccessFileObj.accessFileMain(zender=self.zender)
        elif self.zender.fromWhere == "zender_home":
            goTo(self.zender.fromWhere)
        elif self.zender.fromWhere == "YourBox" or self.zender.fromWhere == "fileBox":
            goTo("YourBox")
    def windowTheam(self):
        with dpg.theme() as window_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (203, 184, 116, 255))
        return window_theme
    def childTheam(self,color):
        with dpg.theme() as child_theme:
            with dpg.theme_component(dpg.mvChildWindow):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg,color)
                dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 15)
        return child_theme
    def addHistoryList(self):
        parent_width = dpg.get_item_width(self.zender.historyWindow)
        with dpg.child_window(tag="historyChildWindow",border=False,width=parent_width) as elderChild:
            dpg.bind_item_theme(elderChild,self.childTheam((203, 184, 116, 255)))
            for _ in range(4):
                dpg.add_child_window(width=300, height=4, border=False)
                with dpg.child_window(width=480,height=60,no_scrollbar=True, no_scroll_with_mouse=True) as child:
                                dpg.bind_item_theme(child,self.childTheam((174, 136, 83, 255)))
                                section_width = 450 // 3
                                with dpg.group(horizontal=True):
                                    with dpg.child_window(width=section_width, height=45, border=True):
                                        dpg.add_spacer(height=1)
                                        dpg.add_text("Audio.txt")

                                    with dpg.child_window(width=section_width, height=45, border=True):
                                        dpg.add_spacer(height=1)
                                        dpg.add_text("10000/10000 MB")

                                    with dpg.child_window(width=section_width, height=45, border=True):
                                        dpg.add_spacer(height=1)
                                        dpg.add_text("50 minuts")
                                        dpg.add_image_button(texture_tag="icon_cross",pos=(section_width-40,10),width=25, height=25, frame_padding=0, background_color=(174, 136, 83, 255))
    def historyManin(self,zender):
        self.zender = zender
        if not dpg.does_item_exist(self.zender.historyWindow):
            with dpg.window(tag=self.zender.historyWindow,pos=(0, 0), no_title_bar=True, no_resize=True, no_move=True):
                with dpg.group(tag='icon_text'):
                    dpg.add_image(texture_tag="icon_history",tag="history_icon", width=50, height=50)
                    dpg.add_text("History",tag="history_text")
                    
                    self.addHistoryList()
                
                dpg.bind_item_font('history_text',self.zender.fontSetUp)
                dpg.bind_item_theme("history_text",self.zender.textColorSetUp((0, 0, 0, 255)))
                dpg.add_image_button(texture_tag="icon_go_back",tag="back_icon_history", width=50, height=50, frame_padding=0, background_color=(203, 184, 116, 255),callback=self.goBack)
            dpg.bind_theme(self.windowTheam())
            zender.resize(zender.historyWindow)