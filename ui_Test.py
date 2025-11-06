from src.app import App
from src.ui.ui_element import UIM, UIElement
from src.constants import *
APP = App()

A = UIElement(APP, Vector2(0,0),Vector2(15,15),draggable=True)
B = UIElement(APP, Vector2(53,0),Vector2(15,15))
C = UIElement(APP, Vector2(130,0),Vector2(15,15),parent=A)
APP.run()