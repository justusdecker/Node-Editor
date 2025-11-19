from pig_ui import UIElement
from pig_ui import UITextInput
from src.constants import *
from typing import Any
"""
A Node will be bu
"""

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
            uie = UIElement(
                app,
                p,
                Vector2(8,8),
                UXWrapper(ux),
                parent = self,
                anchor = 'tl'
            )
            self.sub.append(uie)
            ...