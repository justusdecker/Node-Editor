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
        self.QUEUE.remove(object)
    
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
    
    @staticmethod
    def get_skip_unwanted_groups(object, groups) -> bool:
        """
        Skip unwanted groups & not visible uie's
        """
        return not object.visible or (groups and not object.group in groups)
    
    @staticmethod
    def get_blocked_state(object,blocked) -> bool:
        return blocked != -1 and blocked != object.uid
    
    @staticmethod
    def get_dead_uie(object, blocked) -> bool:
        """
        We encountered a softlock after:
            Pressing a button that makes itself invisbile
        This is a fix/workaround for this
        """
        return not object.visible and object.uid == blocked
    
    @staticmethod
    def get_key_reset(object) -> bool:
        return hasattr(object, 'pressed_keys') and object.pressed_keys and not object.event.KEYS
    
    def update(self, groups: list | tuple | None = None):
        ids = self.__get_ordered_by_layers()
        ids = ids[0] + ids[1]
        
        for id in ids[::-1]:
            object = self.__get_object_by_id(id)
            
            if UIManager.get_dead_uie(object, self.blocked):
                self.blocked = -1
                break
            
            if UIManager.get_skip_unwanted_groups(object,groups):
                continue
            
            if UIManager.get_blocked_state(object, self.blocked): 
                if hasattr(object,'reset'):
                    object.reset()
                continue # other UIE has higher priority because it is actually running(drag&drop)
            
            if UIManager.get_key_reset(object):
                object.pressed_keys = set()
                
            if object.update(): # Object has been interacted with. Break out.
                self.blocked = object.uid
            
            self.draw(ids, groups)
        
    def draw(self, ids, groups):
        for id in ids:
            object = self.__get_object_by_id(id)
            if not object.visible or \
                (groups and not object.group in groups):
                # Skip unwanted groups & not visible uie's
                continue
            if groups and object.group in groups: # Skip unwanted groups
                continue
            
            object.draw()
    @property
    def uids(self) -> list[int]:
        return [o.uid for o in self.QUEUE]   

UIM = UIManager()
