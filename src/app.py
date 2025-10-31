from src.constants import *

class Events:
    def __init__(self):
        self.WHEEL = False
        self.MOUSE_LEFT = False
        self.MOUSE_MIDDLE = False
        self.MOUSE_RIGHT = False
        self.MOUSE_4 = False
        self.MOUSE_5 = False
        self.QUIT = False
        self.MOUSE_RELATIVE = Vector2(0,0)
        self.MOUSE_POS = pg.mouse.get_pos()
        self.KEYDOWN = False
        self.KEYS = set()
        self.DOUBLE_CLICK = False
        self.last_click = 0
        self.keys_to_control = [
            pg.K_a, # Add a new Node
            pg.K_s, # Saves the configuration
            pg.K_l, # Loads the configuration
        ]
        
    def __set_mouse_btn(self, event_btn: int, i: bool):
        match event_btn:
            case 1: self.MOUSE_LEFT = i
            case 2: self.MOUSE_MIDDLE = i
            case 3: self.MOUSE_RIGHT = i
            case 4: self.MOUSE_4 = i
            case 5: self.MOUSE_5 = i
            
    def recv_events(self) -> None:
        self.WHEEL = 0 # Resets the Wheel, because pygame will not do this
        self.DOUBLE_CLICK = False
        self.MOUSE_POS = pg.mouse.get_pos()
        for event in pg.event.get():
            match event.type:
                case pg.MOUSEBUTTONDOWN | pg.MOUSEBUTTONUP:
                    i = event.type == pg.MOUSEBUTTONDOWN
                    self.__set_mouse_btn(event.button,i)
                    if time() - self.last_click <= 0.5 and i: # using the windows-default double-click speed
                        self.DOUBLE_CLICK = True
                        self.last_click = 0
                    if event.button == 1 and i:
                        self.last_click = time()
                case pg.MOUSEWHEEL:
                    self.WHEEL = event.y
                case pg.KEYDOWN:
                    self.KEYS.add(event.key)
                case pg.KEYUP:
                    self.KEYS.remove(event.key)
                case pg.QUIT:
                    self.QUIT = True
                
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