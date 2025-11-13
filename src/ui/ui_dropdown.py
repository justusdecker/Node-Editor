from src.constants import *
from src.ui.ux_element import UXWrapper, UXText, UXRect
from src.ui.ui_element import UIElement

class UIDropDown(UIElement):
    def __init__(self, app, pos, size, ux = None, draggable = False, **kwargs):
        ux=UXWrapper(
            ux = [
                [UXRect(-1,Color(col),size=size),
                 UXText(text_get_callback='')] for col in ('#484848', '#969696', '#ffffff', '#000000')
            ]
        )
        super().__init__(app, pos, size, ux, draggable, **kwargs)
        self.sub = []
        kwargs.get('ltext')
        kwargs.get('lcom')
        #self.set_subs()
    @property
    def text(self) -> str:
        return "test"
    def set_subs(self, ltext: list[str], lcom: list[Callable] | None = None):
        self.texts = []
        if lcom is None:
            lcom = [lambda *x: None for i in ltext]
        for i, (t, c) in enumerate(zip(ltext, lcom)):
            self.texts.append(t)
            ux = [
                [UXRect(-1,Color(col),size=self.size),
                 UXText(text_get_callback=t)] for col in ('#484848', '#969696', '#ffffff', '#000000')
            ]
            
            uie = UIElement(
                self.app, 
                self.abs_offset + Vector2(0,(i+1) * self.size.y),
                self.size,draggable=False,
                ux=UXWrapper(ux), 
                parent=self,
                anchor="tl",
                cb_lclick=c,
                cb_dclick=lambda x: None
                )
            
            self.sub.append(uie)