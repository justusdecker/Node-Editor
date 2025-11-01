from src.ui.ui_element import UIElement
from src.constants import *

from pygame import Surface, Rect, SRCALPHA

TEXT_COLOR = Color('#dddddd')
DEFAULT_BG_COLOR = Color('#363636')
PRESSED_BG_COLOR = Color('#484848')




from src.src_py.ui.ui_calculation import get_center
from pygame.draw import rect as rect_draw
class UXButton(UXElement):
    def __init__(self,
                 **options) -> None:
        if not 'tcg' in options: options['tcg'] = (TEXT_COLOR,HIGHLIGHT_TEXT_COLOR,PRESSED_TEXT_COLOR)
        if not 'bcg' in options: options['bcg'] = (DEFAULT_BACKGROUND_COLOR,)
        super().__init__(**options)
        self.draw()
    def getAllImages(self):
        return self.normal_image,self.hovered_image,self.pressed_image 
    def draw(self):
        "Use this in case you want to redraw the button."
        g = [
                [[0,self.background_color_group.get(0),Vector4(0,0,*self.size)],[1,self.text_color_group.get(0),'center']],
                [[0,self.background_color_group.get(1),Vector4(0,0,*self.size)],[1,self.text_color_group.get(1),'center']],
                [[0,self.background_color_group.get(2),Vector4(0,0,*self.size)],[1,self.text_color_group.get(2),'center']]
        ]
        self.normal_image , self.hovered_image , self.pressed_image = self.gen(
            g,3
        )
        
class UIButton(UIElement):
    def __init__(self, app, pos, size, **kwargs):
        super().__init__(app, pos, size, **kwargs)
        #+ SetImage
        #+ UXElement
    
class UIButton(UIElement):
    """
    .. cb_on_hover:: set the callback for on_hover
    .. cb_on_press:: set the callback for on_press
    .. cb_on_un_hover:: set the callback for on_un_hover
    .. cb_on_release:: set the callback for on_release
    """
    def __init__(self,
                 vector:Vector4,
                 **kwargs) -> None:
        
        UIC.add_element('uiButton')
        self.UX = UXButton(**kwargs.get('ux', {}))
        
        super().__init__(vector,**kwargs)
        self.set_image(self.UX.normal_image)
        self.cb_on_hover = kwargs.get('cb_on_hover',self.noCallback)
        self.cb_on_press = kwargs.get('cb_on_press',self.noCallback)
        self.cb_on_un_hover = kwargs.get('cb_on_un_hover',self.noCallback)
        self.cb_on_release = kwargs.get('cb_on_release',self.noCallback)
        
    def noCallback(self,*btn):
        pass
    def update(self):
        #Change Texture on the fly
        if self.this_frame_hovered:
            self.set_image(self.UX.hovered_image)
            self.cb_on_hover(self)
        if self.this_frame_pressed:
            self.set_image(self.UX.pressed_image)
            self.cb_on_press(self)
        if self.this_frame_un_pressed:
            self.set_image(self.UX.normal_image)
            self.cb_on_release(self)
        if self.this_frame_un_hovered:
            self.set_image(self.UX.normal_image)
            self.cb_on_un_hover(self)
        super().update()