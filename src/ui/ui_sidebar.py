from src.ui.ui_element import UIElement
from src.ui.ui_textinput import UITextInput
from src.ui.ux_element import UXWrapper, UXText, UXRect
from src.constants import *

class UISideBar(UIElement):
    def __init__(self, app):
        size = Vector2(SCREEN_WIDTH // 4, SCREEN_HEIGHT)
        
        ux = [
            [UXRect(-1,Color('#242424' if i < 1 else '#484848'),size=size)] for i in range(4)
        ]
        
        super().__init__(app, Vector2(0,0), size, UXWrapper(ux), False,anchor = 'tl')
        # A SideBar are currently only leftbound
        # Two buttons are needed:
        #   * The first is the close buttom this is placed next to the bar (BarSize.x, 0)
        #   * The second is at 0,0
        #
        #? Only one will be drawn & update at a time.
        
        ux = [
            [UXRect(-1,Color('#242424' if i < 1 else '#484848'),size=Vector2(16,16)),
                UXText(color=Color('#969696'),text_get_callback=lambda: '<')] for i in range(4)
        ]
        
        
        self.in_btn = UIElement(
            self.app,
            Vector2(size.x,0),
            Vector2(16,16),
            UXWrapper(ux),
            parent = self,
            anchor = 'tl',
            cb_lclick = self.roll_in
        )
        
        ux = [
            [UXRect(-1,Color('#242424' if i < 1 else '#484848'),size=Vector2(16,16)),
                UXText(color=Color('#969696'),text_get_callback=lambda: '>')] for i in range(4)
        ]
        
        self.out_btn = UIElement(
            self.app,
            Vector2(0,0),
            Vector2(16,16),
            UXWrapper(ux),
            parent = self,
            anchor = 'tl',
            cb_lclick = self.roll_out
        )
        
    def roll_in(self, x):
        self.visible = False
        self.in_btn.visible = False
        self.out_btn.visible = True
        
    def roll_out(self, x):
        self.visible = True
        self.in_btn.visible = True
        self.out_btn.visible = False