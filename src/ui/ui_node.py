from pig_ui import UIElement
from pig_ui import UITextInput
from src.constants import *
from typing import Any
"""
Todo:
+ Background move functionality
+ Type Check before connection
+ Save Data
+ Load Data
* Z-Index on-top if selected(Only nodes)
* Do not render out of frame
* Only draw line to frame-border
* Change line to bezier
"""


class UIKnot(UIElement): ...
class UIKnot(UIElement):
    def __init__(self, app, pos, size, ux = None, draggable = False, **kwargs):
        self.active = False
        self.is_input = kwargs['type']
        self.connected: list[UIKnot] = []
        
        kwargs['cb_rclick'] = self.disconnect_all
        #kwargs['cb_unclick'] = lambda x: print('Unclick')
        super().__init__(app, pos, size, ux, draggable, **kwargs)
    
    def connect(self, obj: UIKnot): 
        if obj not in self.connected:
            self.connected.append(obj)
            
    def disconnect(self, obj: UIKnot):
        if obj in self.connected:
            self.connected.remove(obj)
    def disconnect_all(self, _):
        for knot in self.connected:
            knot.disconnect(self)
            self.disconnect(knot)
    
    def set_state(self, state: int): 
        self.state = state
    
class UINode(UIElement):
    def __init__(self, app, pos,in_out: list[list[bool, str, Any]], **kwargs):
        l = len(in_out)
        header = 16
        id = 8
        row = 32
        space = 4
        h = header + (l * (row + space)) + id
        size = Vector2(144,h)
        
        ux = [
            [UXRect(-1,Color('#242424' if i < 1 else '#484848'),size=size)] for i in range(4)
        ]
        
        super().__init__(app, pos, size, UXWrapper(ux), True, anchor = 'tl', **kwargs)
        self.sub = []
        self.texts = []
        for idx, (is_input, name, type) in enumerate(in_out):
            #+ Knot
            #+ Input
            self.texts.append(name)
            
            p = Vector2(0 if is_input else self.size.x - 8,header + space + (idx * 24))

            ux = [
            [
                UXRect(-1,Color('#1f8fc0' if i < 1 else "#6db8d8"),size=Vector2(8,8)),
                UXText(Vector2(8 if is_input else -70,0),Color('#ffffff'),0,name)
                ] for i in range(4)
            ]
            uie = UIKnot(
                app,
                p,
                Vector2(8,8),
                UXWrapper(ux),
                parent = self,
                anchor = 'tl',
                cb_lclick = self.set_active,
                type = is_input
            )
            self.sub.append(uie)
            
    def set_active(self, x: UIKnot):
        x.active = True
        
class UINodeManager:
    def __init__(self):
        self.nodes: list[UINode] = []
    def add_node(self, node: UINode):
        self.nodes.append(node)
        
    def update(self):
        obj = None
        already_visited_knots = set()
        for node in self.nodes:
            for knot in node.sub:
                knot: UIKnot
                for cn in knot.connected:
                    if cn.uid not in already_visited_knots:
                        pg.draw.line(node.app.window, (255,128,128),knot.abs_offset + Vector2(4,4), cn.abs_offset + Vector2(4, 4), width=3)
                        already_visited_knots.add(cn)
                already_visited_knots.add(knot)
                if not knot.active: continue
                if obj is not None:
                    onode, oknot = obj
                    
                    knot.active, oknot.active = False, False
                    if node == onode:
                        print(f'Connected to same node: {node.uid} -> {onode.uid}')
                        continue
                    if knot.is_input == oknot.is_input:
                        print(f'Connected {"input" if knot.is_input else "output"} -> {"input" if knot.is_input else "output"}')
                        continue
                    if oknot in knot.connected: # Only one check!
                        print(f'Already Connected {knot.uid} -> {oknot.uid}')
                        continue
                    print(f'Connected {knot.uid} -> {oknot.uid}')
                    knot.connect(oknot)
                    oknot.connect(knot)
                else:
                    pg.draw.line(node.app.window, (128,128,128),knot.abs_offset + Vector2(4,4), knot.event.MOUSE_POS, width=3)
                    obj = (node, knot)
                # search for a second


UINM = UINodeManager()