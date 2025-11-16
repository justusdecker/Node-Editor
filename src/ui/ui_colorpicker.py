from src.ui.ui_element import UIElement
from src.ui.ui_textinput import UITextInput
from src.ui.ux_element import UXElement, UXImage, UXWrapper
from numpy import array, zeros, uint8
from colorsys import rgb_to_hsv,hsv_to_rgb
from src.constants import *
from pygame.surfarray import make_surface
from pygame.transform import scale
from pygame.mouse import get_pos
from pygame import Color, Surface, SRCALPHA
from math import floor
from src.ui.ux_element import UXRect

HEAD_DEFAULT = [
    [UXRect(-1,Color('#484848'),size=Vector2(272,15))],
    [UXRect(-1,Color('#969696'),size=Vector2(272,15))],
    [UXRect(-1,Color('#ffffff'),size=Vector2(272,15))],
    [UXRect(-1,Color('#000000'),size=Vector2(272,15))]
]


def convert_hsv_to_rgb(H: float, S: float, V: float) -> tuple[int, int, int]:
    if S == 0.0:
        val = int(V * 255)
        return (val, val, val)
    i = floor(H * 6)
    f = H * 6 - i
    x = V * (1 - S)
    y = V * (1 - f * S)
    z = V * (1 - (1 - f) * S)
    match i % 6:
        case 0: r, g, b = V, z, x
        case 1: r, g, b = y, V, x
        case 2: r, g, b = x, V, z
        case 3: r, g, b = x, y, V
        case 4: r, g, b = z, x, V
        case 5: r, g, b = V, x, y
        case _: r, g, b = 0, 0, 0 # H >= 1.0
    
    return (int(r * 255), int(g * 255), int(b * 255))

def color_rect(hue: float, size: int = 256) -> Surface: #! Optimize by doing only pixels needed, not all & convert
    pixel_array = zeros(shape=(256,256,3),dtype=uint8)
    for x in range(256):
        for y in range(256):
            pixel_array[y, x] = convert_hsv_to_rgb(hue,x / 255,(255 - y) / 255)

    return pg.transform.scale(make_surface(pixel_array),(size, size))

def color_line(size: Vector2 = Vector2(256, 16)) -> Surface: #! Optimize by doing only pixels needed, not all & convert
    pixel_array = zeros(shape=(256,16,3))
    for x in range(256):
        for y in range(16):
            pixel_array[x, y] = convert_hsv_to_rgb(x/255,1.0,1.0)
    return pg.transform.scale(make_surface(pixel_array),size)

class UIColorPickerRect(UIElement):
    def __init__(self, app, pos, size, ux = None, draggable = False, **kwargs):
        
        super().__init__(app, pos, size, ux, draggable, **kwargs)
    
    def draw(self):
        super().draw()
        pg.draw.circle(
                self.app.window,
                (self.parent.color.b, self.parent.color.g, self.parent.color.r),
                self.abs_offset + self.parent.color_pos,
                15,
                1
            )



class UIColorPicker(UIElement):
    #! color type Must be added: #245245
    #! btn ux missing
    #! Add custom draw code for color selection & hue selection
    def __init__(self, app, pos, size, ux = None, draggable = False, **kwargs):
        kwargs['visible'] = False
        kwargs['anchor'] = 'tl'
        super().__init__(app, pos, size, ux, draggable, **kwargs)

        self.ux_color_rect = UXImage(Vector2(0,0),color_rect(0.2, 128),True)
        self.ux_color_line = UXImage(Vector2(0,0),color_line(Vector2(128,8)),True)
        
        self.color = Color(0,0,0)
        self.hue = None
        self.hue_pos = 0
        self.color_pos = Vector2(0,0)
        
        self.color_rect_btn = UIColorPickerRect(
            self.app,
            Vector2(8,8),
            Vector2(128,128),
            UXWrapper([[self.ux_color_rect] for i in range(4)]),
            parent = self,
            anchor='tl',
            cb_lclick = self.get_color #CAlculate the mouse_pos - offset
        )
        self.color_line_btn = UIElement(
            self.app,
            Vector2(8,272),
            Vector2(128,8),
            UXWrapper([[self.ux_color_line] for i in range(4)]),
            parent = self,
            anchor='tl',
            cb_lclick = self.get_hue #CAlculate the mouse_pos - offset
        )
        
        self.color_in_out = UITextInput(
            self.app,
            Vector2(8,280),
            Vector2(124,32),
            None,
            max_length=7,
            type=3
        )
        
        self.set_color_btn = UIElement(
            self.app,
            Vector2(140,272),
            Vector2(124,32),
            None, #! TODO
            parent = self,
            cb_lclick = lambda x: print('Changed color...') #CAlculate the mouse_pos - offset
        )
     
    def get_hue(self, obj):
        self.hue_pos = obj.get_internal_mouse_pos.x
        self.hue = 255 / self.hue_pos
        self.ux_color_rect.image = color_rect(self.hue, 128)
    def get_color(self, obj):
        self.color_pos = obj.get_internal_mouse_pos
        self.color = self.ux_color_rect.image.get_at(self.color_pos)
        print(self.ux_color_rect.image.get_at(self.color_pos))