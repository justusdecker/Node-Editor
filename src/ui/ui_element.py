
"""
For all the following:
Copy the source code from my pygameEngine & refactor it to match the project requirements
"""

from src.constants import *
from src.events import Events

class UIGroup:
    gid = 0
    def __init__(self, group_name: str):
        self.group_name = group_name
        UIGroup.gid += 1

UI_DEFAULT_GROUP = UIGroup('default')

class Anchor:
    VALID = [
        'tl','tc','tr',
        'cl','cc','cr',
        'lb','cb','rb'
    ]
    def __init__(self):
        pass

class UIElement: ...
class UIElement:
    """
    The Base Class for UIElements
    """
    uid = 0
    def __init__(self,
                 app,
                 pos: Vector2,
                 size: Vector2,
                 **kwargs):
        self.app = app
        self.event: Events = self.app.events
        self.pos = pos
        self.size = size
        
        self.group = kwargs.get('group',UI_DEFAULT_GROUP)
        
        self.layer = kwargs.get('layer',0)
        self.o_layer = kwargs.get('o_layer',0)
        self.visible = kwargs.get('visible', True)
        self.anchor = kwargs.get('anchor', 'cc')
        self.parent = kwargs.get('parent',None)
        
        self.callback_hover = kwargs.get('cb_hover',None)
        self.callback_unhover = kwargs.get('cb_unhover',None)
        self.callback_click = kwargs.get('cb_click',None)
        self.callback_drag = kwargs.get('cb_drag',None)
        
        self.blocked = False
        
        UIElement.uid += 1
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
        g,l = self.event.MOUSE_POS()
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
        return
    
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
    
    def update(self): ...
    
    def draw(self):
        self.app.window.blit(self.image,self.abs_offset)

    def destroy(self):
        UIM.remove_from_queue(self)
        del self
    
class UIManager:
    def __init__(self):
        self.QUEUE = []
    
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
        _q0 = [(o.layer + o.o_layer, o.id) for o in self.QUEUE if not o.o_layer]
        _q1 = [(o.layer + o.o_layer, o.id) for o in self.QUEUE if o.o_layer]
            
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
                if o.id == id:
                    return o
    
    def update(self, groups: list | tuple):
        ids = self.__get_ordered_by_layers()
        
        for id in ids[::-1]:
            object = self.__get_object_by_id(id)
            if not object.visible or \
                not object.group in groups:
                 # Skip unwanted groups & not visible uie's
                pass
            if object.update(): # Object has been interacted with. Break out.
                break
        
        for id in ids:
            object = self.__get_object_by_id(id)
            
            if object.group in groups: # Skip unwanted groups
                continue
            
            object.draw()
            
    @property
    def uids(self) -> list[int]:
        return [o.uid for o in self.QUEUE]   

UIM = UIManager()

    
