from src.constants import *
from src.ui.ux_element import UXWrapper, UXText, UXRect
class UIElement: ...

class UIDropDown:
    def __init__(self,
                 app,
                 pos: Vector2,
                 **kwargs):
        self.app = app
        self.head = UIElement(app, Vector2(0,0),Vector2(32,16),draggable=True)
        self.sub = []
        
    def get_text(self,id: int):
        return self.texts[id]
    def set_subs(self, ltext: list[str], lcom: list[Callable] | None = None):
        self.texts = []
        if lcom is None:
            lcom = [lambda *x: None for i in ltext]
        for i, (t, c) in enumerate(zip(ltext, lcom)):
            self.texts.append(t)
            ux = [
                [UXRect(-1,Color(col),size=Vector2(32,16)),
                 UXText(text_get_callback=t)] for col in ('#484848', '#969696', '#ffffff', '#000000')#! Has no effect on rendering
            ]
            print(t, c(),i )
            UIElement(self.app, Vector2(0,(i+1) * 16),Vector2(32,16),draggable=False,ux=UXWrapper(ux), parent=self.head)