from src.constants import *
from src.ui.ux_element import UXWrapper, UXText, UXRect
from src.ui.ui_element import UIElement
from src.ui.ui_manager import UIM
class UIDropDown(UIElement):
    def __init__(self, app, pos, size, ux = None, draggable = False, **kwargs):
        kwargs['cb_lclick'] = self.toggle_dd
        kwargs['anchor'] = "tl"
        ux=UXWrapper(
            ux = [
                [UXRect(-1,Color(col),size=size),
                 UXText(text_get_callback=kwargs.get('title', ''))] for col in ('#484848', '#969696', '#ffffff', '#000000')
            ]
        )
        super().__init__(app, pos, size, ux, draggable, **kwargs)
        self.sub = []
        kwargs.get('ltext')
        kwargs.get('lcom')
    @property
    def text(self) -> str:
        return "test"
    def toggle_dd(self,*_):
        for uie in self.sub:
            uie.visible = not uie.visible
    def sub_callbacks(self,obj):
        i = self.sub.index(obj)
        self.sub_cbs[i](obj)
        for uie in self.sub:
            uie.visible = not uie.visible
    def set_subs(self, ltext: list[str], lcom: list[Callable] | None = None):
        for uie in self.sub:
            uie: UIElement
            uie.destroy()
        
        self.texts = []
        if lcom is None:
            lcom = [lambda *x: None for i in ltext]
        print(ltext, lcom)
        self.sub_cbs = lcom
        for i, (t, c) in enumerate(zip(ltext, lcom)):
            print(t,)
            self.texts.append(t)
            ux = [
                [UXRect(-1,Color(col),size=self.size),
                 UXText(text_get_callback=t)] for col in ('#484848', '#969696', '#ffffff', '#000000')
            ]
            
            uie = UIElement(
                self.app, 
                Vector2(0,(i+1) * self.size.y),
                self.size,
                draggable=False,
                ux=UXWrapper(ux), 
                parent=self,
                anchor="tl",
                cb_lclick=self.sub_callbacks,
                cb_dclick=lambda x: None,
                visible=False
                )
            print(self.abs_offset + Vector2(0,(i+1) * self.size.y), uie.abs_offset)
            self.sub.append(uie)