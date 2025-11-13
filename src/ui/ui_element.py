from src.constants import *
from src.ui.ux_element import UXRenderer, UXWrapper, UIELEMENT_DEFAULT, UIELEMENT_TEXT, UXText, UXRect
from src.ui.ui_manager import UIM
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
        self.callback_unclick = kwargs.get('cb_unclick',lambda x: print(x))
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
        
        if self.event.MOUSE_LEFT and not self.hover and not self.blocked:
            self.callback_unclick(self)
        
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
