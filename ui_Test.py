from src.app import App
from src.ui.ui_element import UIM, UIElement
from src.constants import *
APP = App()

UIE = UIElement(APP, Vector2(0,0),Vector2(15,15),)


APP.run()