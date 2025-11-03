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
        self.offset = offset
        self.size = size
        self.width = width
        
    def draw(self, surf: Surface):
        pg.draw.rect(surf, 
                     self.color, 
                     (self.offset.x,self.offset.y, self.size.x,self.y),
                     self.width,
                     border_radius=-1,
                     *self.border_radius.options
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
                 path: str,
                 alpha: bool):
        self.pos = pos
        self.image = pg.image.load(path)
        self.alpha = alpha
    def draw(self, surf):
        surf.blit(self.image, self.pos)

class UXText(UXElement): ...

class UXRenderer:
    def __init__(self,
                 ui,
                 ux: list[UXElement]):
        self.ui = ui
        self.ux = ux
        self.draw()
    def draw(self):
        self.image = pg.Surface(self.ui.size)
        for element in self.ux:
            element.draw()