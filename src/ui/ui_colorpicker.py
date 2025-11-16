from src.ui.ui_element import UIElement
from src.ui.ui_textinput import UITextInput
from src.ui.ux_element import UXElement, UXImage, UXWrapper
from numpy import array, zeros, uint8
from numpy.typing import NDArray
from colorsys import rgb_to_hsv,hsv_to_rgb
from src.constants import *
from pygame.surfarray import make_surface
from pygame.transform import scale
from pygame.mouse import get_pos
from pygame import Color, Surface, SRCALPHA
from math import floor
from src.ui.ux_element import UXRect, UXText

SET_BUTTON = [
    [UXRect(-1,Color('#484848'),size=Vector2(128,16))],
    [UXRect(-1,Color('#969696'),size=Vector2(128,16))],
    [UXRect(-1,Color('#ffffff'),size=Vector2(128,16))],
    [UXRect(-1,Color('#000000'),size=Vector2(128,16))]
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

def color_rect_array(hue: float, size: int = 256) -> NDArray: #! Optimize by doing only pixels needed, not all & convert
    pixel_array = zeros(shape=(256,256,3),dtype=uint8)
    for x in range(256):
        for y in range(256):
            pixel_array[y, x] = convert_hsv_to_rgb(hue,x / 255,(255 - y) / 255)
    return pixel_array

def color_rect(hue: float, size: int = 256) -> Surface: #! Optimize by doing only pixels needed, not all & convert
    return pg.transform.scale(make_surface(color_rect_array(hue, size)),(size, size))

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
class UIColorPickerLine(UIElement):
    def __init__(self, app, pos, size, ux = None, draggable = False, **kwargs):
        
        super().__init__(app, pos, size, ux, draggable, **kwargs)
    
    def draw(self):
        super().draw()
        col = Color(self.parent.ux_color_line.image.get_at(Vector2(self.parent.hue_pos,0)))
        pg.draw.line(
                self.app.window,
                (col.b, col.g, col.r),
                self.abs_offset + Vector2(self.parent.hue_pos,-4),
                self.abs_offset + Vector2(self.parent.hue_pos, 12),
                3
            )
def hex_to_rgb(hex_code):
    hex_code = hex_code[1:]
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))
class UIColorInput(UITextInput):
    def __init__(self, app, pos, size, ux=None, draggable=False, multiline = False, max_length = -1, type = 2, **kwargs):
        
        super().__init__(app, pos, size, ux, draggable, multiline, max_length, type, **kwargs)
    
    def update(self):
        if self.special_keys[pg.K_RETURN].pressed:
            try:
                # 1. HEX zu RGB konvertieren (0-255)
                r, g, b = hex_to_rgb(self.text)
                
                r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
                
                h, s, v = rgb_to_hsv(r_norm, g_norm, b_norm)


                ly = int(h * (127)) 

                x = 127 - int(s * (127))
                
                y = int((v * (127))) 
                self.parent.color_pos = (x,y)
                self.parent.line_pos = ly
                self.parent.ux_color_rect.image = color_rect(h,128)
                
            except ValueError as E:
                print(f'ERROR: {E}')
        return super().update()

class UIColorPicker(UIElement):
    def __init__(self, app, pos, **kwargs):
        ux = [
            [UXRect(-1,color=Color('#363636'),size=Vector2(144,216)),
             UXRect(-1,color=Color('#484848' if i < 1 else '#969696'),size=Vector2(144,16)),
             UXText(color=Color('#969696'),text_get_callback=lambda : "Color")] for i in range(4)
        ]
        kwargs['anchor'] = 'tl'
        super().__init__(app, pos, Vector2(144,216), UXWrapper(ux), True, **kwargs)

        self.ux_color_rect = UXImage(Vector2(0,0),color_rect(0.2, 128),True)
        self.ux_color_line = UXImage(Vector2(0,0),color_line(Vector2(128,8)),True)
        
        self.color = Color(0,0,0)
        self.hue = 0.2
        self.hue_pos = 0
        self.color_pos = Vector2(0,0)
        
        self.color_rect_btn = UIColorPickerRect(
            self.app,
            Vector2(8,24),
            Vector2(128,128),
            UXWrapper([[self.ux_color_rect] for i in range(4)]),
            parent = self,
            anchor='tl',
            cb_lclick = self.get_color #CAlculate the mouse_pos - offset
        )
        self.color_line_btn = UIColorPickerLine(
            self.app,
            Vector2(8,160),
            Vector2(128,8),
            UXWrapper([[self.ux_color_line] for i in range(4)]),
            parent = self,
            anchor='tl',
            cb_lclick = self.get_hue #CAlculate the mouse_pos - offset
        )
        
        self.color_in_out = UIColorInput(
            self.app,
            Vector2(8,176),
            Vector2(128,32),
            max_length=7,
            type=3,
            parent = self,
            anchor = 'tl'
        )
    def get_color_hex(self) -> str:
        c = Color(self.color)
        return f'#{c.r:02x}{c.g:02x}{c.b:02x}'
        
    def get_hue(self, obj):
        self.hue_pos = obj.get_internal_mouse_pos.x
        self.hue = 255 / self.hue_pos
        self.ux_color_rect.image = color_rect(self.hue, 128)
        
        self.color = Color(self.ux_color_rect.image.get_at(self.color_pos))
        c = self.color
        self.color_in_out.text = f'#{c.r:02x}{c.g:02x}{c.b:02x}'
        
    def get_color(self, obj):
        self.color_pos = obj.get_internal_mouse_pos
        self.color = Color(self.ux_color_rect.image.get_at(self.color_pos))
        c = self.color
        self.color_in_out.text = f'#{c.r:02x}{c.g:02x}{c.b:02x}'