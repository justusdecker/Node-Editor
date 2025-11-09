
from typing import Callable
from src.constants import *
from src.ui.ux_element import UXRenderer, UXWrapper, UIELEMENT_DEFAULT, UIELEMENT_TEXT, UXText, UXRect
from src.events import Events

class UIGroup:
    gid = 0
    def __init__(self, group_name: str):
        self.group_name = group_name
        UIGroup.gid += 1

UI_DEFAULT_GROUP = UIGroup('default')

ANCHORS = {'t': -1, 'c': -.5, 'b': 0, 'l': -1, 'r': 0}

class UIElement: ...
class UIElement:
    """
    The Base Class for UIElements
    """
    __uid = 0
    def __init__(self,
                 app,
                 pos: Vector2,
                 size: Vector2,
                 ux: UXWrapper | None = None,
                 draggable: bool = False,
                 **kwargs):
        
        self.app = app
        if ux is None:
            self.ux = UXWrapper(UIELEMENT_DEFAULT)
        else: 
            self.ux = ux
        self.event: Events = self.app.events
        self.pos = pos
        self.size = size
        self.draggable = draggable
        self.group = kwargs.get('group',UI_DEFAULT_GROUP)
        
        self.layer = kwargs.get('layer',0)
        self.o_layer = kwargs.get('o_layer',0)
        self.visible = kwargs.get('visible', True)
        self.anchor = kwargs.get('anchor', 'cc')
        self.parent = kwargs.get('parent',None)
        
        self.callback_hover = kwargs.get('cb_hover',lambda x: print(x)) #! change ux
        self.callback_unhover = kwargs.get('cb_unhover',lambda x: print(x)) #! change ux
        self.callback_lclick = kwargs.get('cb_lclick',lambda x: print(x)) #! change ux
        self.callback_rclick = kwargs.get('cb_rclick',lambda x: print(x))
        self.callback_dclick = kwargs.get('cb_dclick',lambda x: print(x)) #! change ux
        self.callback_drag = kwargs.get('cb_drag',lambda x: print(x)) #! change ux
        self.callback_wheel = kwargs.get('cb_wheel',lambda x: print(x))
        self.callback_keypress = kwargs.get('cb_keypress',lambda x: print(x))
        
        self.blocked = False
        self.click_offset = Vector2(0,0)
        
        UIElement.__uid += 1
        self.uid = UIElement.__uid
        UIM.add_to_queue(self)
    
    @property
    def rect(self) -> Rect:
        """
        Returns the Rect from this UI Object.
        """
        return Rect(self.pos.x, self.pos.y, self.size.x, self.size.y)
    
    @property
    def hover(self) -> bool:
        x, y = self.abs_offset
        w,h = self.size.x,self.size.y
        g,l = self.event.MOUSE_POS
        return g > x and l > y and g < x + w and l < y + h
    
    @property
    def image(self) -> Surface:
        """
        Returns the current Image for this UIElement.
        Will be a blank 1 by 1 Surface if nothing set!
        """
        if not hasattr(self,'surface'):
            self.surface = Surface((1,1))
        return self.surface
    
    @property
    def anchor_offset(self) -> Vector2:
        """
        Calculates the offset for the anchor: Center, LEFT etc.
        """
        #TODO add offset code here
        x,y = self.anchor
        self.size + Vector2(ANCHORS[x], ANCHORS[y])
        
        return self.size + Vector2(ANCHORS[x], ANCHORS[y])
    
    @property
    def parent_offset(self) -> Vector2:
        """
        Calculates the parent offset to the `regular` position of the `UIElement`
        """
        offset = Vector2(0,0)
        parent = self.parent
        
        while parent is not None:
            offset += parent.pos
            parent = parent.parent
            
        return offset
    
    @property
    def abs_offset(self) -> Vector2:
        """
        The absolute offset: anchor + parents + pos
        """
        return self.anchor_offset + self.parent_offset + self.pos
    
    @property
    def root_parent(self) -> None | UIElement:
        """
        Gets the main / root parent of this object.
        Can only be None if the first upper parent is None.
        
        """
        parent = self.parent
        
        while 1:
            if parent.parent is not None:
                parent = parent.parent
            else:
                break
            
        return parent
    
    def mouse_interaction(self):
        
        # Click only one time, self.last_frame_hold to time
        if self.event.MOUSE_LEFT and self.is_free:
            self.callback_lclick(self)
            self.ux.set_mode(2)
        
        # UI Double Clicked
        if self.event.DOUBLE_CLICK and self.is_free: 
            self.callback_dclick(self)
            self.ux.set_mode(2)
            
        # Right click
        if self.event.MOUSE_RIGHT and self.is_free:
            self.callback_rclick(self)
            
        # A key was pressed while hover
        if self.event.KEYDOWN and self.event.KEYS and self.is_free:
            self.callback_keypress(self)
        
        if self.event.WHEEL and self.is_free:
            self.callback_wheel(self)
        
    def mouse_interaction_ex(self):
        # Dragging
        if self.event.MOUSE_MIDDLE and self.is_free:
            self.is_dragging = True
            self.click_offset = self.pos - self.event.MOUSE_POS
            self.callback_drag(self)
            self.ux.set_mode(2)
        
    def keyboard_interaction(self): # Used for Shortcuts
        ...
    def keyboard_interaction_ex(self): # Used for TextInputSystems
        ...
    
    @property
    def is_free(self) -> bool:
        return self.hover and not self.blocked
    
    def update(self): 
        # self.last_frame_hold to False if not pressed anymore
        # self.last_frame_hold must have a multiframe puffer preventing unwanted drags.
        # So self.last_frame_hold must be >= last_time + 0.2 and after that the self.dragging will be set to true
        
        
        #! If a object is dragged, only draw other update, DO NOT UPDATE!
        
        # Updating position on dragging if enabled
        if self.event.MOUSE_MIDDLE and self.is_dragging:
            self.pos = self.event.MOUSE_POS + self.click_offset
        
        # Resets the ability to use the UIE
        # Currently it is pretty simple and will prevent from pressing Mouse 1 after Mouse 3 etc.
        if not self.event.MOUSE_LEFT \
            and not self.event.MOUSE_RIGHT \
            and not self.event.MOUSE_MIDDLE \
            and not self.event.KEYS \
            and not self.event.DOUBLE_CLICK\
            and not self.event.WHEEL:
            self.is_dragging = False
            self.blocked = False
            self.click_offset = Vector2(0,0)
            UIM.blocked = -1
            return False
        
        self.mouse_interaction()

        if self.draggable:
            self.mouse_interaction_ex()
        
        self.keyboard_interaction()
        
        self.blocked = any([self.event.MOUSE_LEFT,self.event.MOUSE_RIGHT,self.event.MOUSE_MIDDLE,self.event.KEYS,self.event.DOUBLE_CLICK,self.event.WHEEL]) and self.hover
        return self.blocked
    
    def draw(self):
        self.app.window.blit(self.image,self.abs_offset)
        pg.draw.rect(self.app.window, (255,0,0), (self.abs_offset.x, self.abs_offset.y, self.size.x, self.size.y))

        if not self.blocked and UIM.blocked == -1:
            self.ux.set_mode(0)
        self.ux.draw(self.app.window,self.abs_offset)
        
    def destroy(self):
        UIM.remove_from_queue(self)
        del self

class TextInput(UIElement):
    #! Add blocking: out of bounds write
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
    
    def keyboard_interaction(self):
        if not self.shift and self._return and not pg.K_RETURN in self.pressed_keys:  # Add and for spam
            self.set_used_keys()
            return
        if self.delete and not pg.K_BACKSPACE in self.pressed_keys : # Add and for spam
            self.text = self.text[:-1] if self.text else ''
            self.set_used_keys()
            return
        text = [self.TRANSLATION_TABLE.get(key,('',''))[self.shift] for key in self.event.KEYS if key not in self.pressed_keys]
        if not self.multiline:
            text = text.replace('\n','')
        self.set_used_keys()
        if self.max_length != -1 and len(self.text) + len(text) > self.max_length: 
            
            return
        if text:
            self.text += self.type_check(''.join(text))
        
        print(text)

class UISpinBox(UIElement): ...
class UIColorPicker(UIElement): ...
class UIDropDown:
    def __init__(self,
                 app,
                 pos: Vector2,
                 **kwargs):
        self.app = app
        self.head = UIElement(app, Vector2(0,0),Vector2(32,16),draggable=True)
        self.sub = []
        
    def get_text(self,id: int):
        return self.texts[id]
    def set_subs(self, ltext: list[str], lcom: list[Callable] | None = None):
        self.texts = []
        if lcom is None:
            lcom = [lambda *x: None for i in ltext]
        for i, (t, c) in enumerate(zip(ltext, lcom)):
            self.texts.append(t)
            cb = lambda: t
            ux = [
                [UXRect(-1,Color(col),size=Vector2(32,16)),
                 UXText(text_get_callback=cb)] for col in ('#484848', '#969696', '#ffffff', '#000000')#! Has no effect on rendering
            ]
            print(t, c(), cb(),i )
            UIElement(self.app, Vector2(0,(i+1) * 16),Vector2(32,16),draggable=False,ux=UXWrapper(ux), parent=self.head)
            
        
class UIMenuBar(UIElement): ...
class UIMenuItem(UIElement): ...

class UIManager:
    def __init__(self):
        self.QUEUE = []
        self.blocked = -1
    
    def add_to_queue(self,object):
        """
        This adds a ``UIElement`` to the render queue.
        """
        self.QUEUE.append(object)
        
    def remove_from_queue(self, object):
        """
        Removes the given ``UIElement`` from the QUEUE.
        """
        i = self.QUEUE.index(object)
        self.QUEUE.remove(i)
    
    def stick_on_top(self,object):
        """
        Takes the selected Object, if its exists in QUEUE and
        remove it from its old layer and re:adds it on the end of the set 
        """
        if object.uid in self.uids:
            i = self.QUEUE.index(object)
            self.QUEUE.remove(i)
            self.QUEUE.append(i)
    
    def __get_ordered_by_layers(self) -> tuple[list[int], list[int]]:
        """
        HUD LAYER = 1
        BG LAYER = 2
        """
        _q0 = [(o.layer + o.o_layer, o.uid) for o in self.QUEUE if not o.o_layer]
        _q1 = [(o.layer + o.o_layer, o.uid) for o in self.QUEUE if o.o_layer]
            
        _s0 = sorted(
            _q0,
            key = lambda x: x[0]
        )
        _s1 = sorted(
            _q1,
            key = lambda x: x[0]
        )
        
        return [i[1] for i in _s0], [i[1] for i in _s1]
    
    def __get_object_by_id(self, id: int):
        if id in self.uids:
            for o in self.QUEUE:
                if o.uid == id:
                    return o
        assert id not in self.uids
    
    def update(self, groups: list | tuple | None = None):
        ids = self.__get_ordered_by_layers()
        ids = ids[0] + ids[1]
        
        for id in ids[::-1]:
            object = self.__get_object_by_id(id)
            if not object.visible or \
                (groups and not object.group in groups):
                # Skip unwanted groups & not visible uie's
                pass
            if self.blocked != -1 and self.blocked != object.uid: 
                continue # other UIE has higher priority because it is actually running(drag&drop)
            if hasattr(object, 'pressed_keys') and object.pressed_keys and not object.event.KEYS:
                object.pressed_keys = set()
            if object.update(): # Object has been interacted with. Break out.
                self.blocked = object.uid
        
        for id in ids:
            object = self.__get_object_by_id(id)
            
            if groups and object.group in groups: # Skip unwanted groups
                continue
            
            object.draw()
            
    @property
    def uids(self) -> list[int]:
        return [o.uid for o in self.QUEUE]   

UIM = UIManager()

