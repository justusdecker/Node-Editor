from src.ui.utils import *
from src.constants import *
from typing import Any
from src.ui.ui_node import UINM
class NewApp(App): 
    """
    A variant of the Application Class.
    We need to insert the UINodeManager here.
    
    """
    def run(self):
        while self.is_running:
            self.window.fill((25,25,25))
            self.update()
            UIM.update()
            UINM.update()
            self.draw()
            self.event_handler()
            
        self.destroy()
APP = NewApp()

pg.key.set_repeat(500,50)
M = UIMenuBar(APP, Vector2(0,0),Vector2(32,16))
M.set_subs(
    [
        {
            'title': "File",
            'ltext': ["New", "Open", "Save"],
            'lcom': None
        },
        {
            'title': "About",
            'ltext': ["Help", "License"],
            'lcom': None
        }
    ]
)


OFFSET = UIElement(APP, Vector2(0,0),Vector2(1280,720),UXWrapper([[],[],[],[]]))

BG = UIElement(APP, Vector2(0,0),Vector2(1280,720),UXWrapper([[],[],[],[]]))

A = UIElement(APP, Vector2(400,30),Vector2(15,15),draggable=True)
B = UIElement(APP, Vector2(53,350),Vector2(15,15))
C = UIElement(APP, Vector2(130,360),Vector2(15,15),parent=A)
D = UITextInput(APP, Vector2(130,0),Vector2(200,100),parent=A, multiline=True, max_length=64)
E = UIDropDown(APP, Vector2(255,30),Vector2(32,16),draggable=True,title='ABC')

def get_fps():
    return str(int(APP.clock.get_fps()))
FPS_DISPLAY = [
    [UXRect(-1,Color('#484848'),size=Vector2(64,32)),
     UXText(text_get_callback=get_fps)],
    [UXRect(-1,Color('#969696'),size=Vector2(64,32)),
     UXText(text_get_callback=get_fps)],
    [UXRect(-1,Color('#ffffff'),size=Vector2(64,32)),
     UXText(text_get_callback=get_fps)],
    [UXRect(-1,Color('#000000'),size=Vector2(64,32)),
     UXText(text_get_callback=get_fps)]
]

F = UIElement(APP, Vector2(420,360),Vector2(64,32),UXWrapper(FPS_DISPLAY))

CP = UIColorPicker(APP, Vector2(100,0))
SB = UISpinBox(APP,Vector2(250,300),0.2, 2)
SBN = UISideBar(APP)
E.set_subs(['ABC','DEF','GHI'])

NODE_1 = UINode(APP, 
                Vector2(150,150),
                [
                    [False, "test1", str],
                    [False, "test2", Any],
                    [False, "test3", str],
                    [True, "test1", str],
                    [True, "test2", str],
                    [True, "test3", str],
                ]
                )

NODE_2 = UINode(APP, 
                Vector2(150,150),
                [
                    [False, "test1", str],
                    [False, "test2", bool],
                    [False, "test3", int],
                    [True, "test1", int],
                    [True, "test2", float],
                    [True, "test3", str],
                ]
                )

UINM.add_node(NODE_1)
UINM.add_node(NODE_2)

APP.run()