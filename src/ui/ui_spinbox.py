from src.ui.ui_element import UIElement
from src.ui.ux_element import UXWrapper, UXText, UXRect
from src.constants import *
class UISpinBox(UIElement): 
    def __init__(self, app, pos, draggable = False, **kwargs):
        # < 255 > btn - textinput(int | float) - btn
        kwargs['anchor'] = 'tl'
        super().__init__(app, pos, Vector2(128,24), None, draggable, **kwargs)
        
        
        ux = [
            [UXRect(-1,Color('#242424' if i < 1 else '#484848'),size=Vector2(8,8)),
                UXText(color=Color('#969696'),text_get_callback=lambda: '<')] for i in range(4)
        ]
        self.dec_btn = UIElement(
            self.app,
            Vector2(4,4),
            Vector2(8,8),
            UXWrapper(ux),
            anchor = 'tl'
        )
        