from src.ui.ui_element import UIElement
from src.ui.ui_dropdown import UIDropDown
from src.constants import *
from src.ui.ux_element import UXWrapper, UXText, UXRect
from src.ui.ui_manager import UIM
class UIMenuBar(UIElement):
    def __init__(self, app, pos, size, ux = None, draggable = False, **kwargs):
        kwargs['visible'] = False
        kwargs['anchor'] = 'tl'
        super().__init__(app, pos, size, ux, draggable, **kwargs)
        self.sub = []
    def set_subs(self, subs: list[dict]):
        """
        Format:
            {
                'title': "title",
                'ltext': [],
                'lcom': []
            }
        """
        
        for i, dd in enumerate(subs):
            uidd = UIDropDown(
                self.app, 
                Vector2(i*self.size.x, 0),
                self.size,
                parent=self,
                anchor= 'tl',
                title = dd['title'],
                draggable=True,
                )
            
            uidd.set_subs(dd['ltext'], dd['lcom'])
            self.sub.append(uidd)