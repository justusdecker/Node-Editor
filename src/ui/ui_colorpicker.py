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

def color_rect(hue: float) -> Surface:
    pixel_array = zeros(shape=(256,256,3),dtype=uint8)
    for x in range(256):
        for y in range(256):
            pixel_array[y, x] = convert_hsv_to_rgb(hue,x / 255,(255 - y) / 255)

    return make_surface(pixel_array)

def color_line() -> Surface:
    pixel_array = zeros(shape=(256,16,3))
    for x in range(256):
        for y in range(16):
            pixel_array[x, y] = convert_hsv_to_rgb(x/255,1.0,1.0)
    return make_surface(pixel_array)

class UIColorPickerElement(UIElement):
    def __init__(self, app, pos, size, ux = None, draggable = False, **kwargs):
        super().__init__(app, pos, size, ux, draggable, **kwargs)

class UIColorPicker(UIElement):
    def __init__(self, app, pos, size, ux = None, draggable = False, **kwargs):
        kwargs['visible'] = False
        super().__init__(app, pos, size, ux, draggable, **kwargs)

        self.ux_color_rect = UXImage(Vector2(0,0),color_rect(0.2))
        self.ux_color_line = UXImage(Vector2(0,0),color_line())
        
        self.color = None
        self.hue = None
        
        self.color_rect_btn = UIElement( #!Must be a different element with overwritten update rules
            self.app,
            Vector2(8,8),
            Vector2(256,256),
            UXWrapper([[self.ux_color_rect] for i in range(4)]),
            parent = self,
            cb_lclick = lambda x: print('Changed color...') #CAlculate the mouse_pos - offset
        )
        self.color_line_btn = UIElement( #!Must be a different element with overwritten update rules
            self.app,
            Vector2(8,272),
            Vector2(256,16),
            UXWrapper([[self.ux_color_rect] for i in range(4)]),
            parent = self,
            cb_lclick = lambda x: print('Changed color...') #CAlculate the mouse_pos - offset
        )
        
        self.color_in_out = UITextInput(
            self.app,
            Vector2(8,280),
            Vector2(124,32),
            None,
            max_length=7,
            type=3 #! color type Must be added
        )
        
        self.set_color_btn = UIElement( #!Must be a different element with overwritten update rules
            self.app,
            Vector2(140,272),
            Vector2(124,32),
            None, #! TODO
            parent = self,
            cb_lclick = lambda x: print('Changed color...') #CAlculate the mouse_pos - offset
        )
        
        """
    def set_col_by_hex(self,*_):
        if len(self.hex_input.text) == 7:
            rgb = self.hex_input.text
            
            r,g,b = int(rgb[1:3],16),int(rgb[3:5],16),int(rgb[5:7],16)
            self.current_color = r,g,b,255
            r = (r / 255) if r > 0 else 0
            g = (g / 255) if g > 0 else 0
            b = (b / 255) if b > 0 else 0
            self.hue = rgb_to_hsv(r,g,b)[0]
            self.color_rect.set_image(scale(make_surface(color_rect(self.hue)),(163,163)))
            self.rerender_text_inputs()
    def set_col_by_rgb(self,*_):
        if not self.r_input.text or not self.g_input.text or not self.b_input.text: return
        r = int(self.r_input.text)
        r = r if r < 256 else 255
        g = int(self.g_input.text)
        g = g if g < 256 else 255
        b = int(self.b_input.text)
        b = b if b < 256 else 255
        self.current_color = r,g,b,255
        hsv = rgb_to_hsv(r,g,b)
        self.hue = hsv[0]
        self.color_rect.set_image(scale(make_surface(color_rect(self.hue)),(163,163)))
        self.rerender_text_inputs()
    def set_col_by_hsv(self,*_):
        if not self.h_input.text or not self.s_input.text or not self.v_input.text: return
        h, s, v = hsv_to_rgb(float(self.h_input.text),float(self.s_input.text),float(self.v_input.text))
        r = (h if h <= 1 else 1) * 255
        g = (s if s <= 1 else 1) * 255
        b = (v if v <= 1 else 1) * 255
        self.current_color = r,g,b
        self.hue = h
        self.color_rect.set_image(scale(make_surface(color_rect(self.hue)),(163,163)))
        self.rerender_text_inputs()
    def rerender_text_inputs(self):
        r,g,b,a = tuple(self.current_color)
        h, s, v = rgb_to_hsv((r / 255) if r > 0 else 0 , (g / 255) if g > 0 else 0, (b / 255) if b > 0 else 0)

        self.h_input.overwrite_text(f'{h:.2f}'[:3])
        self.s_input.overwrite_text(f'{s:.2f}'[:3])
        self.v_input.overwrite_text(f'{v:.2f}'[:3])
        self.r_input.overwrite_text(str(int(r)))
        self.g_input.overwrite_text(str(int(g)))
        self.b_input.overwrite_text(str(int(b)))
    def update(self):
        
        if self.color_rect.is_pressed:
            x1 , y1 = get_pos()
            x2, y2 = self.color_rect.get_abs_position()
            x, y = x1 - x2, y1 - y2
            
            if x >= 0 and y >= 0 and x < self.color_rect.dest[0] and y < self.color_rect.dest[1]:
                
                self.current_color = self.color_rect.get_image().get_at((x,y))
                self.last_pos = x,y
                self.rerender_text_inputs()
        if self.color_line.is_pressed:
            x1 , y1 = get_pos()
            x2, y2 = self.color_line.get_abs_position()
            x, y = x1 - x2, y1 - y2
            
            if x >= 0 and y >= 0 and x < self.color_line.dest[0] and y < self.color_line.dest[1]:
                p = (x / self.color_line.dest[0]) if x > 0 else 0
                self.hue = p
                self.color_rect.set_image(scale(make_surface(color_rect(self.hue)),(163,163)))
                self.current_color = self.color_rect.get_image().get_at(self.last_pos)
                self.rerender_text_inputs()   

        if self.color_rect.is_pressed or self.color_line.is_pressed:
            
            surf = Surface(self.color_preview.dest,SRCALPHA)
            surf.fill(self.current_color)
            self.color_preview.set_image(surf)
        else:
            surf = Surface(self.color_preview.dest,SRCALPHA)
            self.color_preview.set_image(surf)
        return super().update()
        """