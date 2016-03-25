import kivy
from random import Random
kivy.require('1.9.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty,StringProperty
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.core.audio import Sound, SoundLoader
from time import clock
import ast
import re
from kivy.storage.jsonstore import JsonStore
from kivy.core.window import Window
import copy


Rows_For_First_Level = 3
Max_Level = 15

'''
class BButton(Button):
    def __init__(self,box,**kwargs):
        super(BButton,self).__init__(**kwargs)
        self.box = box
        self.isMarking = False

    def on_press(self):
        self.press()

    def press(self):
        if self.box.root.gameover:
            return
        
        self.isMarking = self.box.root.status_bar.toggle_mark.state=='down'

        if self.isMarking:
            if self.image.opacity == 1:
                self.MarkNormal()
            else:
                self.MarkB()
        else:
            self.box.Clear()

    def MarkB(self):
        self.image.opacity = 1
        self.box.state=1
        
        if self.box.root.mute == False:
            self.box.root.sounds['state'].play()
        
        if self.box.root.gameover == False:
            self.box.root.bfound += 1

    def MarkNormal(self):
        self.image.opacity = 0
        self.box.state=0
        
        if self.box.root.mute == False:
            self.box.root.sounds['state'].play()
            
        if self.box.root.gameover == False:
            self.box.root.bfound -= 1

class BLabel(Label):
    pass
'''
class BBox():
    BNumber = NumericProperty(0)
    def __init__(self,root,**kwargs):
        self.isBomb = False
        self.BNumber = 0
        self.root = root
        self.isClear = False
        self.row = 0
        self.col = 0
        self.state=0 # 0 means normal, 1 means marked as bomb, -1 means cleared already
        self.pos = (0,0)
        self.size = (0,0)
        

    def Clear(self,isShowAll=False):
        '''
        triggered when user click the button and think it's empty or has a number
        '''
        if self.isBomb and self.state==0:
            '''
            A Bomb, game over
            '''
            if isShowAll == False:
                self.root.GameOver()
                self.Explode()
                #self.bbutton.image.source='gameoverflag.png'
        else:
            self.MarkNumberOrEmpty()
            
        self.root.CheckSucceed()


    def Explode(self):
        '''
        Animation needed
        '''  
        if self.root.mute == False:
            self.root.sounds['bomb'].play()
            
        self.root.ShowAll()
    
    def MarkNumberOrEmpty(self):
        '''
        Not only mark itself as empty, also mark all around boxes if they are empty
        '''
        if self.state == 1:
            return
        
        if self.BNumber == 0 and self.isClear == False:
            self.isClear = True

            self.root.Clear(self.row - 1,self.col - 1)
            self.root.Clear(self.row - 1,self.col)
            self.root.Clear(self.row - 1,self.col + 1)
            self.root.Clear(self.row,self.col - 1)
            self.root.Clear(self.row,self.col + 1)
            self.root.Clear(self.row + 1,self.col - 1)
            self.root.Clear(self.row + 1,self.col)
            self.root.Clear(self.row + 1,self.col + 1)
                    
        elif self.BNumber > 0 and self.isClear == False:
            self.isClear = True
            
        self.state = -1
        
        if self.root.mute == False:
            self.root.sounds['state'].play()
       
    
class PlayArea(Widget):
    pass

class FindBWidget(BoxLayout):
    level=NumericProperty(1)
    bfound = NumericProperty(0)
    bnumber = NumericProperty(0)
    
    def __init__(self,**kwargs):
        super(FindBWidget,self).__init__(**kwargs)
        self.BBoxList=[]
        self.store = JsonStore("findb.json")
        self.gridSize_height = 0
        self.gridSize_width = 0
        self.bnumber = 0
        self.badded = 0
        self.bfound = 0
        self.mute=True
        self.gameover = False
        self.custimize = False
        self.custimize_height = 0
        self.custimize_width = 0
        self.custimize_brate = 0.2
        
        self.sounds = {'bomb':SoundLoader.load('bomb.wav'),
                       'state':SoundLoader.load('state.wav'),
                       'upgrade':SoundLoader.load('upgrade.mp3')}
        
        self.start_clock = clock()
        self.config = None
                
    def on_bfound(self,instance,value):
        self.status_bar.label_left_bomb.text = '{}'.format(self.bnumber - self.bfound)
        self.CheckSucceed()

    def on_bnumber(self,instance,value):
        self.status_bar.label_left_bomb.text = '{}'.format(self.bnumber - self.bfound)

    def Restart(self):
        self.custimize,self.custimize_height,self.custimize_width,self.custimize_brate = self.get_customize_info()
        self.level,self.levels_info = self.get_level_info()
        self.mute = self.get_mute_info()
        
        self.BBoxList = []
                
        if self.custimize == True:
            self.status_bar.label_level.text = 'L:C'
            self.gridSize_height = self.custimize_height
            self.gridSize_width = self.custimize_width
            
            if self.gridSize_height < 5:
                self.gridSize_height = 5
            if self.gridSize_width < 5:
                self.gridSize_width = 5
            if self.gridSize_height > 50:
                self.gridSize_height = 50
            if self.gridSize_width > 50:
                self.gridSize_width = 50
        else:
            self.status_bar.label_level.text = 'L:{}'.format(self.level)
            self.gridSize_width = self.level + Rows_For_First_Level
            self.gridSize_height = self.level + Rows_For_First_Level            
        
        self.bnumber = 0
        self.badded = 0
        self.bfound = 0
        self.start_clock = clock()
        self.gameover = False
        self.play_area.clear_widgets()
        self.play_area.cols = self.gridSize_width
        self.play_area.rows = self.gridSize_height
        
        '''
        for i in range(0,self.gridSize_height):
            for j in range(0,self.gridSize_width):
                b = BBox(root=self)
                b.row=i
                b.col=j
                self.BBoxList.append(b)
                self.play_area.add_widget(b)
        '''
        self._calculate_bombs()
        
        self.status_bar.toggle_mark.disable = False
        self.status_bar.toggle_mark.state = "normal"
        self.status_bar.button_reset.image.source='smile.png'

    def _calculate_bombs(self):
        if self.custimize:
            self.brate = self.custimize_brate/100.0
            if self.brate < 0.05:
                self.brate = 0.05
            if self.brate > 0.8:
                self.brate = 0.8
        elif self.level < 6:
            self.brate = 0.11
        elif self.level < 11:
            self.brate = 0.13
        elif self.level < 20:
            self.brate = 0.15
        elif self.level < 30:
            self.brate = 0.18
        else:
            self.brate = 0.2
            
        self.bnumber = int(self.brate * self.gridSize_width * self.gridSize_height)
        
        self.badded = 0
        while True:
            if self._add_bomb():
                self.badded += 1
                
            if self.badded >= self.bnumber:
                break

    def _add_bomb(self):
        if len(self.BBoxList) <=0:
            return
        
        i = Random().randint(0,len(self.BBoxList) - 1)
        
        if self.BBoxList[i].isBomb:
            return False
        else:
            self.BBoxList[i].isBomb = True
            #set bomb number of the around boxes
            row = self.BBoxList[i].row
            col = self.BBoxList[i].col            

            self._add_bomb_number(row - 1,col - 1)
            self._add_bomb_number(row - 1,col)
            self._add_bomb_number(row - 1,col + 1)                
            self._add_bomb_number(row,col - 1)
            self._add_bomb_number(row,col + 1)
            self._add_bomb_number(row + 1,col - 1)
            self._add_bomb_number(row + 1,col)
            self._add_bomb_number(row + 1,col + 1)
                    
        return True
    def _add_bomb_number(self,row,col):
        if row < 0 or row >= self.gridSize_width or col < 0 or col >= self.gridSize_height:
            return
        
        index = row*self.gridSize_width + col
        if index < 0 or index >= len(self.BBoxList):
            return
        
        self.BBoxList[index].BNumber += 1
    
        
    def Clear(self,row,col):
        if row < 0 or row >= self.gridSize_width or col < 0 or col >= self.gridSize_height:
            return
        
        index = row*self.gridSize_width + col
        if index < 0 or index >= len(self.BBoxList):
            return
        
        self.BBoxList[index].MarkNumberOrEmpty()
    
    def ShowAll(self):
        self.status_bar.toggle_mark.state='normal'
        for i in range(0,len(self.BBoxList)):
            if self.BBoxList[i].isBomb:
               self.BBoxList[i].bbutton.MarkB()
            else:
                self.BBoxList[i].Clear()

    def CheckSucceed(self):
        if self.bfound > 0 and self.bfound == self.bnumber:
            for i in range(0,len(self.BBoxList)):
                if self.BBoxList[i].state == 0:
                    return False

            #upgrade level  
            if self.mute == False:
                self.sounds['upgrade'].play()
            
            
            if self.custimize == False:
                duration = round((clock() - self.start_clock),2)                
            
                if self.levels_info.has_key(self.level) and self.levels_info[self.level] > 0:
                    if self.levels_info[self.level] > duration:
                        self.levels_info[self.level] = duration
                else:
                    self.levels_info[self.level] = duration
                    
                if self.level < Max_Level:
                    self.level += 1
                    
                self.store_user_data(self.level,self.levels_info)

            self.Restart()
            
            return True
        else:
            return False
        
    def get_level_info(self):
        if self.store.exists("UserData") == False:
            self.store.put("UserData",CurrentLevel=1,Levels={})
        
        return self.store.get("UserData")["CurrentLevel"],self.store.get("UserData")["Levels"]
    def get_mute_info(self):
        return self.config.get('Sounds','Mute') == '1'
    
    def get_customize_info(self):
       return self.config.get('Customization','Enable') == '1',self.config.getint('Customization','C_Height'),self.config.getint('Customization','C_Width'),self.config.getint('Customization','Rate')

    def store_user_data(self,currentLevel,levels):
        self.store.put("UserData",CurrentLevel=currentLevel,Levels=levels)
        
    def GameOver(self):
        self.status_bar.toggle_mark.disable = True
        self.status_bar.button_reset.image.source='gameover.png'
        self.gameover = True
    
class MinesApp(App): 
    use_kivy_settings = False
    clearcolor = (0.2, 0.2, 0.2, 1)
    title = 'Find Bombs'
    def build(self):        
        findb = FindBWidget()
        findb.config = self.config
        findb.Restart() 
        return findb
    
    def on_pause(self):
        return True
    
    def on_resume(self):
        pass
        
    
    def build_config(self, config):
        try:
            config.get('Sounds','Mute')
        except:
            config.setdefaults('Sounds',{
                                              'Mute':True
                                              }
                              )
            
        try:
            config.get('Customization','Rate')
        except:
            config.setdefaults('Customization',{
                                                'Enable':False,
                                              'C_Height':10,
                                              'C_Width':10,
                                              'Rate':20,
                                              'FullScreen':False
                                              }
                              )

    def build_settings(self, settings):
        jsondata = """[
                        {"type":"title",
                        "title":"Sounds"
                        },
                        { "type": "bool",
                        "title": "Mute",
                        "desc": "Play without sound",
                        "section": "Sounds",
                        "key": "Mute"},
                        
                        {"type":"title",
                        "title":"Customize Boxes"
                        },
                        { "type": "bool",
                        "title": "Customize",
                        "desc": "Play your own customization",
                        "section": "Customization",
                        "key": "Enable"},
                        
                        { "type": "numeric",
                        "title": "Height",
                        "desc": "How many box you want as height",
                        "section": "Customization",
                        "key": "C_Height" },
                        
                        { "type": "numeric",
                        "title": "Width",
                        "desc": "How many box you want as width",
                        "section": "Customization",
                        "key": "C_Width" },
                        
                        { "type": "numeric",
                        "title": "Rate of Bomb",
                        "desc": "How many bomb you will have in percentage",
                        "section": "Customization",
                        "key": "Rate" },
                        
                        
                        {"type":"title",
                        "title":"Full Screen"
                        },
                        { "type": "bool",
                        "title": "Full Screen",
                        "section": "Customization",
                        "key": "FullScreen"}
                    ]"""
        settings.add_json_panel('Find Bomb',self.config,data=jsondata)
            
    def on_config_change(self, config, section, key, value):
        if config is self.config:
            token = (section, key)
            if token == ('Sounds', 'Mute'):
                self.root.mute = (value == '1')
            elif token == ('Customization','Enable'):
                self.root.customize = (value == '1')
            elif token == ('Customization','C_Height'):
                self.root.customize_height = value
            elif token == ('Customization','C_Width'):
                self.root.customize_width = value
            elif token == ('Customization','Rate'):
                self.root.customize_rate = value
            elif token == ('Customization','FullScreen'):
                Window.toggle_fullscreen()
                
if __name__ == '__main__':
    mines = MinesApp()
    mines.run()
