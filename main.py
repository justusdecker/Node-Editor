from src.app import App
from src.ui.utils import *
from src.constants import *
APP = App()
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
A = UIElement(APP, Vector2(400,30),Vector2(15,15),draggable=True)
B = UIElement(APP, Vector2(53,350),Vector2(15,15))
C = UIElement(APP, Vector2(130,360),Vector2(15,15),parent=A)
D = UITextInput(APP, Vector2(130,0),Vector2(200,100),parent=A, multiline=True, max_length=64)
E = UIDropDown(APP, Vector2(255,30),Vector2(32,16),draggable=True,title='ABC')
CP = UIColorPicker(APP, Vector2(100,0))
SB = UISpinBox(APP,Vector2(250,300),0.2, 2)
SBN = UISideBar(APP)
E.set_subs(['ABC','DEF','GHI'])

NODE_1 = UINode(APP, 
                Vector2(150,150),
                [
                    [False, "test1", str],
                    [False, "test2", str],
                    [False, "test3", str],
                    [True, "test1", str],
                    [True, "test2", str],
                    [True, "test3", str],
                ]
                )

APP.run()