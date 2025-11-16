from src.ui.ui_element import UIElement
from src.ui.ui_textinput import UITextInput
from src.ui.ux_element import UXWrapper, UXText, UXRect
from src.constants import *
class UISpinBox(UIElement): 
    def __init__(self, app, pos,increment_by: float | int,round_by: int, **kwargs):
        kwargs['anchor'] = 'tl'
        self.increment_by = increment_by
        self.round_by = round_by
        super().__init__(app, pos, Vector2(80,16), None, False, **kwargs)
        
        
        ux = [
            [UXRect(-1,Color('#242424' if i < 1 else '#484848'),size=Vector2(16,16)),
                UXText(color=Color('#969696'),text_get_callback=lambda: '<')] for i in range(4)
        ]
        
        
        self.dec_btn = UIElement(
            self.app,
            Vector2(0,0),
            Vector2(16,16),
            UXWrapper(ux),
            parent = self,
            anchor = 'tl',
            cb_lclick = self.dec_num
        )
        
        self.inp = UITextInput(
            self.app,
            Vector2(16,0),
            Vector2(48,16),
            parent = self,
            anchor = 'tl',
            type=2
        )
        
        ux = [
            [UXRect(-1,Color('#242424' if i < 1 else '#484848'),size=Vector2(16,16)),
                UXText(color=Color('#969696'),text_get_callback=lambda: '>')] for i in range(4)
        ]
        self.inc_btn = UIElement(
            self.app,
            Vector2(64,0),
            Vector2(16,16),
            UXWrapper(ux),
            anchor = 'tl',
            parent = self,
            cb_lclick = self.inc_num
        )
    def get_n(self) -> float | int:
        try:
            n = float(self.inp.text)
            return n
        except:
            return 0
    def inc_num(self, x):
        n = self.get_n()
        n += self.increment_by
        n = round(n, self.round_by)
        self.inp.text = str(n)
    
    def dec_num(self, x):
        n = self.get_n()
        n -= self.increment_by
        n = round(n, self.round_by)
        self.inp.text = str(n)