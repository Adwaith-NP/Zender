import dearpygui.dearpygui as dpg


def resizeElement(windowName,self,tagList=[],tag=None,notification=False):
    width = dpg.get_viewport_width()
    height = dpg.get_viewport_height()
    dpg.set_item_width(windowName, width)
    dpg.set_item_height(windowName, height)
   
    if notification:
        dpg.set_item_pos("notification", [(width / 2)-150, (height / 2)-150])
    
    if windowName == self.homeWindowName:
        dpg.set_item_pos("zender_box", [(width / 2) - 60, (height / 2) - 90])
        dpg.set_item_pos("zender_your_box", [(width / 2) - 60, (height / 2) + 20])
        dpg.set_item_pos("zender_download", [width - 100, 10])
        userIdLen = len(dpg.get_value('userIdZender'))
        dpg.set_item_pos("zender_copy", [(userIdLen*10), 33]) #((width//100)*20))
        
    elif windowName == self.loginToBoxWindowName:
        dpg.set_item_pos("userId", [(width / 2) - 200, (height / 2) - 110])
        dpg.set_item_pos("boxId", [(width / 2) - 200, (height / 2) - 65])
        dpg.set_item_pos("boxPassword", [(width / 2) - 200, (height / 2)-20])
        dpg.set_item_pos("accessBoc", [(width / 2) - 200, (height / 2)+25])
    elif windowName == self.accessFileWindowName:
        dpg.set_item_pos("zender_download_accessFile", [width - 100, 10])
        for tagName in tagList:
            dpg.set_item_indent(tagName,(width//100)*10)
        if tag == 'fileInfo':
            dpg.set_item_pos("fileInfo", [(width / 2) - 180, (height / 2)-150])
            
    elif windowName == self.historyWindow:
        dpg.set_item_pos("icon_text", [width//2, 40])
        dpg.set_item_pos("historyChildWindow", [(width / 2) - 230 , (height / 2) - 130])
    
    elif windowName == self.yourBoxWindow:
        dpg.set_item_pos("boxChildWindow", [(width / 2) - 230 , (height / 2) - 120])
        dpg.set_item_pos("zender_download_yourBox", [width - 100, 10])

    elif windowName == self.createBox:
        dpg.set_item_pos("box_icon", [(width / 2)-40, 50])
        dpg.set_item_pos("boxId_create", [(width / 2) - 200, (height / 2) - 65])
        dpg.set_item_pos("boxPassword_create", [(width / 2) - 200, (height / 2)-20])
        dpg.set_item_pos("encryption_checkbox", [(width / 2) - 200, (height / 2)+35])
        dpg.set_item_pos("encText", [(width / 2) - 170, (height / 2)+30])
        dpg.set_item_pos("create_box", [(width / 2) - 200, (height / 2)+75])
        dpg.set_item_pos("infoText", [(width / 2) - 200, (height / 2)+175])
        dpg.set_item_pos("warning", [(width)-400, 20])
        
    elif windowName == self.fileBox:
        dpg.set_item_pos("zender_download_fileBox", [width - 100, 10])
        for tagName in tagList:
            dpg.set_item_indent(tagName,(width//100)*10)
        if tag == 'addNewFileWindow':
            dpg.set_item_pos("addNewFileWindow", [(width / 2) - 275, (height / 2)-200])
        if tag == 'fileInfoWindow':  
            dpg.set_item_pos("fileInfoWindow", [(width / 2) - 275, (height / 2)-200])
            
            
            