from src.modules import *

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

FONT_NAME = 'Consolas'
FONT_SIZE_BASE = 13
FONT_MIN_SIZE_DRAW = 10
SAVE_FILE = "nodes_save.json"
CULL_PADDING = 50 

WHITE = Color('#ffffff')
BLACK = Color('#000000')
GRAY = Color('#969696')
NODE_COLOR = Color('#3C3C3C')
NODE_HEADER_COLOR = Color('#505050')
PANEL_COLOR = Color('#282828')
DATA_TYPES = {
    "str":      Color('#FFA500'),    
    "int":      Color('#0096C8'),    
    "float":    Color('#00C8C8'),    
    "bool":     Color('#ff0000'),      
    "list":     Color('#9600C8'),    
    "any":      Color('#646464'),  
}
DEFAULT_SOCKET_COLOR = Color('#C86400')

NORM_FONT = pg.font.SysFont('Consolas',FONT_SIZE_BASE)