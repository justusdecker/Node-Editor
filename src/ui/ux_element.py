from src.constants import *
from pygame import Surface, SRCALPHA
from pygame.draw import rect as rect_draw

"""
+ Add UXText
. Test the UX Elements
+ Add the UX to UI
"""



class UXParameterError(Exception):
    """"""

class UX4Param:
    def __init__(self,*options):
        options = list(options)
        l = 4 - len(options)
        if l < 0:
            raise Exception('TooManyParameters')
        if l > 0:
            options += [0 for i in range(l)]
        
        self.options = options

class UXElement:
    def draw(self): ...

class UXRect(UXElement):
    def __init__(self,
                 border_radius: int | UX4Param = -1,
                 color: Color = Color('#252525'),
                 offset: Vector2 = Vector2(0,0),
                 size: Vector2 = Vector2(1,1),
                 width: int = 0):
        self.border_radius = border_radius
        if isinstance(self.border_radius, int):
            self.border_radius = UX4Param(*[self.border_radius]*4)
        self.color = color
        self.pos = offset
        self.size = size
        self.width = width
        
    def draw(self, surf: Surface, offset: Vector2):
        pg.draw.rect(surf, 
                     self.color, 
                     (offset.x + self.pos.x,offset.y + self.pos.y, self.size.x,self.size.y),
                     self.width,
                     border_radius=-1,
                     #*self.border_radius.options
                     )

class UXCircle(UXElement): 
    def __init__(self,
                 color: Color,
                 center: Vector2,
                 radius: float,
                 width: int,
                 drawing_points: UX4Param):
        self.color = color
        self.center = center
        self.radius = radius
        self.width = width
        self.drawing_points = drawing_points
        
    def draw(self, surf):
        pg.draw.circle(
            surf,
            self.color,
            self.center,
            self.radius,
            self.width,
            *self.drawing_points.options
        )

class UXLine(UXElement):
    def __init__(self,
                 color: Color,
                 start: Vector2,
                 end: Vector2,
                 width: int):
        self.color = color
        self.start = start
        self.end = end
        self.width = width
    def draw(self, surf):
        pg.draw.line(
            surf,
            self.color,
            self.start,
            self.end,
            self.width
        )

class UXPolygon(UXElement):
    def __init__(self,
                 color: Color,
                 points: list[Vector2],
                 width: int):
        self.color = color
        self.points = points
        self.width = width
    def draw(self, surf):
        pg.draw.polygon(
            surf,
            self.color,
            self.points,
            self.width
        )

class UXImage(UXElement):
    def __init__(self,
                 pos: Vector2,
                 path: str | Surface,
                 alpha: bool):
        self.pos = pos
        if isinstance(path, str):
            self.image = pg.image.load(path)
        elif isinstance(path, Surface):
            self.image = path
            
        self.alpha = alpha
    def update(self, surf: Surface):
        self.image = surf
    def draw(self, surf):
        surf.blit(self.image, self.pos)

FONT = pg.font.SysFont('Consolas',13)

class UXText(UXElement):
    # + Add a snap point for x, so the text will not go outside the element!
    def __init__(self, pos: Vector2 = Vector2(0,0), color: Color = Color('#dddddd'), anchor = 0,text_get_callback: Callable | str = lambda: ""):
        self.anchor = anchor
        self.pos = pos
        self.text_get_callback = text_get_callback
        self.color = color
        super().__init__()
    @property
    def anchor_offset(self) -> Vector2:
        return [0,0.5,1][self.anchor]
    def draw(self, surf: Surface, offset: Vector2):
        text = self.text_get_callback() if not isinstance(self.text_get_callback, str) else self.text_get_callback
        rendered = FONT.render(text, True, self.color)
        size = Vector2(*rendered.get_size())
        surf.blit(rendered, self.pos + offset - (size * self.anchor_offset))
        
        

UIELEMENT_DEFAULT = [
    [UXRect(-1,Color('#484848'),size=Vector2(15,15))],
    [UXRect(-1,Color('#969696'),size=Vector2(15,15))],
    [UXRect(-1,Color('#ffffff'),size=Vector2(15,15))],
    [UXRect(-1,Color('#000000'),size=Vector2(15,15))]
]


UIELEMENT_TEXT = [
    [UXText(color=Color('#484848'))],
    [UXText(color=Color('#969696'))],
    [UXText(color=Color('#ffffff'))],
    [UXText(color=Color('#000000'))]
]

class UXRenderer:
    def __init__(self,
                 ui,
                 ux: list[list[UXElement]]):
        self.ui = ui
        self.ux = ux
        self.draw()
    def draw(self, surf: Surface, offset: Vector2):
        for element in self.ux:
            
            element.draw(surf, offset)
            
class UXWrapper:
    def __init__(self, ux: list[list[UXRenderer]]):
        
        self.ux = ux
        self.set_mode(0)
    
    def draw(self,surf: Surface, offset: Vector2):
        for ux in self.ux[self.selected]:
            ux.draw(surf, offset)
        
    def set_mode(self,type: int):
        """
        (0) normal
        (1) hover
        (2) click
        (3) disabled
        """
        self.selected = type
        
        
