from src.constants import *
from src.events import Events
class App:
    def __init__(self):
        self.is_running = True
        self.window = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pg.display.set_caption("PyNodle")
        self.clock = pg.time.Clock()
        self.events = Events()
        
    def run(self):
        while self.is_running:
            self.window.fill((25,25,25))
            self.update()
            self.draw()
            self.event_handler()
        self.destroy()
    
    def update(self):
        self.clock.tick(60)
    def draw(self):
        if self.events.MOUSE_LEFT:
            pg.draw.circle(self.window,(128,128,0),self.events.MOUSE_POS,8,3)
        if self.events.DOUBLE_CLICK:
            pg.draw.circle(self.window,(0,128,128),self.events.MOUSE_POS,16,3)
        pg.display.update()
        
    def event_handler(self):
        self.events.recv_events()
        if self.events.QUIT:
            self.is_running = False
    def destroy(self):
        self.is_running