from src.constants import *
from src.ui.ux_element import UXWrapper, UXText
from src.ui.ui_element import UIElement

class SpecialKeyStates:
    IDLE = 0
    WAITING_FOR_DELAY = 1
    REPEATING = 2
    
class SpecialKey:
    DELAY = 0
    REPEAT = 0
    def __init__(self, delay_ms: int, repeat_ms: int):
        self.REPEAT_MS = repeat_ms
        self.DELAY_MS = delay_ms
        self.last_press_time = 0.0
        self.last_repeat_time = 0.0
        self.state = SpecialKeyStates.IDLE
        self.pressed = False
    def reset(self):
        self.state = SpecialKeyStates.IDLE
    def update(self):
        self.pressed = False
        if self.state == SpecialKeyStates.IDLE: 
            self.state = SpecialKeyStates.WAITING_FOR_DELAY
            self.pressed = True
            self.last_press_time = time()
            self.last_repeat_time = time()
            
        elif self.state == SpecialKeyStates.WAITING_FOR_DELAY: 
            time_since = (time() - self.last_press_time) * 1000
            if time_since >= self.DELAY_MS:
                self.state = SpecialKeyStates.REPEATING
                self.last_repeat_time = time()
                
        elif self.state == SpecialKeyStates.REPEATING: 
            time_since = (time() - self.last_repeat_time) * 1000
            if time_since >= self.REPEAT_MS:
                self.pressed = True
                self.last_repeat_time = time()

class UITextInput(UIElement):
    #! Add blocking: out of bounds write
    #! Add Row/Columns
    # 
    """
    A Default TextInput
    """
    TRANSLATION_TABLE = {getattr(pg,f'K_{l}'): (l, u) for l,u in zip('0123456789abcdefghijklmnopqrstuvwxyz','=!"§$%&/()ABCDEFGHIJKLMNOPQRSTUVWXYZ')}
    TRANSLATION_TABLE[pg.K_SPACE] = (' ', ' ')
    TRANSLATION_TABLE[pg.K_RETURN] = ('', '\n')
    TRANSLATION_TABLE[pg.K_PERIOD] = ('.', ':')
    def __init__(self, app, pos, size, ux = None, draggable = False, multiline: bool = False, max_length: int = -1, type: int = 2, **kwargs):
        """
        Type 0: takes all(str)
        Type 1: takes only(int)
        Type 2: takes int & float
        """
        # click outside or returning will set is_editing to false
        """
        To reset the is_editing variable we need to inject this into UIM
        from there it will check the id & outside_clicks so it can reset
        
        in UIM:
            if self.is_editing: break # will break because the other elements should be not interacted with!
            if object.is_editing:
                if not object.hover and object.event.MOUSE_LEFT:
                    object.is_editing = False
        """
        
        # We need UXFont
        # The font can have its own anchors left, center, right
        kwargs['cb_lclick'] = self.set_edit
        kwargs['cb_unclick'] = self.reset
        if ux is None:
            
            UIELEMENT_TEXT = [
            [UXText(color=Color('#484848'),text_get_callback=self.get_text)],
            [UXText(color=Color('#969696'),text_get_callback=self.get_text)],
            [UXText(color=Color('#ffffff'),text_get_callback=self.get_text)],
            [UXText(color=Color('#000000'),text_get_callback=self.get_text)]
        ]
            ux = UXWrapper(UIELEMENT_TEXT)
        super().__init__(app, pos, size, ux, draggable, **kwargs)
        
        self.text = 'abc'
        self.is_editing = False
        self.pressed_keys = set()
        self.multiline = multiline
        self.max_length = max_length
        self.type = type
        self.special_keys: dict[str, SpecialKey] = {}
        
        self.set_special_key_state(pg.K_RETURN)
        self.set_special_key_state(pg.K_BACKSPACE)
        
    def get_text(self) -> str:
        return self.text
    def set_edit(self,*_):
        self.is_editing = True
    @property
    def delete(self) -> bool:
        return pg.K_BACKSPACE in self.event.KEYS
    @property
    def _return(self) -> bool:
        return pg.K_RETURN in self.event.KEYS
    @property
    def shift(self) -> bool:
        return pg.K_LSHIFT in self.event.KEYS or pg.K_RSHIFT in self.event.KEYS
    def set_used_keys(self):
        for key in self.event.KEYS:
            self.pressed_keys.add(key)
    
    def type_check(self, text: str) -> str:
        match self.type:
            case 1: 
                if text.isdecimal(): return text
                return ''
            case 2:
                try:
                    float(self.text + text)
                    return text
                except:
                    return ''
            case _: return text
    
    def set_special_key_state(self, key: int): 
        if key not in self.special_keys:
            self.special_keys[key] = SpecialKey(500,50)
    def update_special_key_state(self, key: int):
        if key in self.event.KEYS:
            self.special_keys[key].update()
            
        else:
            self.special_keys[key].reset()

    def get_special_key_state(self, key: int):
        return self.special_keys[key].pressed
    def reset(self,*_):
        self.is_editing = False
    def keyboard_interaction(self):
        if not self.is_editing: return
        self.update_special_key_state(pg.K_RETURN)
        self.update_special_key_state(pg.K_BACKSPACE)
        
        if self.get_special_key_state(pg.K_BACKSPACE):
            self.text = self.text[:-1] if self.text else ''
            return
        
        text = self.event.TEXTINPUT
        if self.max_length != -1 and len(self.text) + len(text) > self.max_length: 
            return
        
        if text:
            self.text += text
        if self.get_special_key_state(pg.K_RETURN):
            self.text += '\n'
