from src.constants import *
from src.ui.bezier import draw_beziere
"""
Better Node Editor:

* New system for setting up knot poses [all outputs, all inputs] not smelted together
+ String Input
+ Multiline String Input
+ Color Input
+ DropDown Input
+ New Vector2 & Vector3 Types


Node:
Each Node will have its own blit surface so the offsets are irrelevant

Each Node needs content
"""

SCREEN = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption("StoryBuilder")
CLOCK = pg.time.Clock()

DEFAULT_NODES = [
    {
        'name': 'Integer',
        'inputs': [],
        'outputs': [('number','int')]
    },
    {
        'name': 'Float',
        'inputs': [],
        'outputs': [('number','float')]
    },
    {
        'name': 'Float To Integer',
        'inputs': [('in','float')],
        'outputs': [('out','int')]
    },
    {
        'name': 'Entity Position',
        'inputs': [],
        'outputs': [('x','int'), ('y','int')]
    },
    {
        'name': 'Move To Position',
        'inputs': [('Entity ID','int'),
                   ('x','int'),
                   ('y','int')],
        'outputs': [('Next','any')]
    },
    {
        'name': 'Player',
        'inputs': [],
        'outputs': [('Entity ID','int')]
    },
    {
        'name': 'Start Node',
        'inputs': [('Name','str')],
        'outputs': [('Name','str')]
    }
]

class TextInput:
    """TextInput in the Header of a Node"""
    def __init__(self, rect, initial_text, font):
        self.rect = rect
        self.text = initial_text
        self.active = False
        self.font = font
        self.base_font_size = font.size("A")[1]
        
    def set_rect(self, rect):
        self.rect = rect

    def handle_event(self, event):
        if event.type == pg.KEYDOWN and self.active:
            if event.key == pg.K_RETURN or event.key == pg.K_KP_ENTER:
                self.active = False
            elif event.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
        
        elif event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False

    def draw(self, surface):
        if self.font.get_height() < FONT_MIN_SIZE_DRAW:
            return

        color = WHITE if self.active else GRAY
        pg.draw.rect(surface, color, self.rect, 2)
        
        text_surface = self.font.render(self.text, True, WHITE)
        surface.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        
        if self.active:
            cursor_pos = self.rect.x + 5 + text_surface.get_width()
            pg.draw.line(surface, WHITE, (cursor_pos, self.rect.y + 5), (cursor_pos, self.rect.y + self.rect.height - 5), 2)


class NodePreset:
    """Base class for Node Presets"""
    def __init__(self, name, inputs, outputs):
        self.name = name
        self.inputs = inputs
        self.outputs = outputs

    def create_node(self, x, y):
        """Returns a Node-Instance."""
        return Node(self.name, x, y, self.inputs, self.outputs)
    
class NodeFactory:
    """Configs and provides NodePresets."""
    def __init__(self):
        self.presets = [NodePreset(**nio) for nio in DEFAULT_NODES]
    
    def get_preset_names(self):
        return [p.name for p in self.presets]
        
    def get_preset_by_name(self, name):
        return next((p for p in self.presets if p.name == name), None)

class UIPanel:
    """Panel for creating knots"""
    def __init__(self, factory, rect, editor):
        self.factory = factory
        self.rect = rect
        self.editor = editor
        self.button_height = 30
        self.buttons = []
        self._setup_buttons()
        pg.font.init()
        self.ui_font = pg.font.SysFont('Consolas',FONT_SIZE_BASE)

    def _setup_buttons(self):
        y_offset = self.rect.top + 35
        for name in self.factory.get_preset_names():
            button_rect = pg.Rect(self.rect.left + 5, y_offset, self.rect.width - 10, self.button_height)
            self.buttons.append((name, button_rect))
            y_offset += self.button_height + 5

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            for name, rect in self.buttons:
                if rect.collidepoint(event.pos):
                    new_x = (SCREEN_WIDTH // 2) - self.editor.offset_x
                    new_y = (SCREEN_HEIGHT // 2) - self.editor.offset_y
                    preset = self.factory.get_preset_by_name(name)
                    if preset:
                        self.editor.nodes.append(preset.create_node(new_x / self.editor.scale, new_y / self.editor.scale))
                        print(f"Node '{name}' über UI erstellt.")

    def draw(self, surface):
        pg.draw.rect(surface, PANEL_COLOR, self.rect)
        
        title = self.ui_font.render("Knoten erstellen (A)", True, WHITE)
        surface.blit(title, (self.rect.left + 5, self.rect.top + 5))
        pg.draw.line(surface, GRAY, (self.rect.left, self.rect.top + 30), (self.rect.right, self.rect.top + 30), 1)

        for name, rect in self.buttons:
            pg.draw.rect(surface, NODE_HEADER_COLOR, rect)
            text = self.ui_font.render(name, True, WHITE)
            text_rect = text.get_rect(center=rect.center)
            surface.blit(text, text_rect)
            
class Socket:
    """Represents the Input- or Output-Connection on the knot."""
    def __init__(self, name, node, is_input, index, data_type="any"):
        self.name = name
        self.node = node
        self.is_input = is_input
        self.index = index
        self.radius = 6
        self.data_type = data_type.lower() 
    def get_color(self) -> Color:
        return DATA_TYPES.get(self.data_type,WHITE)
    def get_pos(self, editor_offset, scale):
        """Calculates the drawing position of the sockets with offset & scaling."""
        
        if self.is_input:
            x_base = self.node.x
        else:
            x_base = self.node.x + self.node.width
        header_height = 25
        y_base = self.node.y + header_height + (self.index + 0.5) * 20
        
        x = (x_base * scale) + editor_offset[0]
        y = (y_base * scale) + editor_offset[1]
        
        return (int(x), int(y))

    def draw(self, surface, editor_offset, scale, font):
        """Draws the Socket in the color of his datatype and representing form."""
        pos = self.get_pos(editor_offset, scale)
        color = DATA_TYPES.get(self.data_type, DEFAULT_SOCKET_COLOR)
        
        current_radius = max(2, int(self.radius * scale))
        
        if self.is_input:
            size = current_radius * 2 - 2
            input_rect = pg.Rect(pos[0] - size // 2, pos[1] - size // 2, size, size)
            pg.draw.rect(surface, color, input_rect, border_radius=2)
            pg.draw.rect(surface, BLACK, input_rect, 1, border_radius=2)
        else:
            pg.draw.circle(surface, color, pos, current_radius)
            pg.draw.circle(surface, BLACK, pos, current_radius, 1)

        if font.get_height() < FONT_MIN_SIZE_DRAW:
            return

        text_surface = font.render(f"{self.name} ({self.data_type})", True, WHITE)
        
        text_offset = max(5, int((self.radius + 5) * scale))
        
        if self.is_input:
            surface.blit(text_surface, (pos[0] + text_offset, pos[1] - text_surface.get_height() // 2))
        else:
            text_rect = text_surface.get_rect(right=pos[0] - text_offset, centery=pos[1])
            surface.blit(text_surface, text_rect)
            
class Node:
    """Repräsentiert einen Knoten im System."""
    node_counter = 0
    HEADER_HEIGHT = 25
    LINE_HEIGHT = 20

    def __init__(self, name, x, y, input_defs, output_defs, node_id=None):
        self.x = x
        self.y = y
        self.input_defs = input_defs 
        self.output_defs = output_defs
        
        self.width = self._calculate_width(name, input_defs, output_defs)
        self.height = self.HEADER_HEIGHT + max(len(input_defs), len(output_defs)) * self.LINE_HEIGHT
        
        if node_id is None:
            self.id = Node.node_counter
            Node.node_counter += 1
        else:
            self.id = node_id
            Node.node_counter = max(Node.node_counter, self.id + 1)
        
        self.is_dragging = False
        
        self.inputs = [Socket(n, self, True, i, t) for i, (n, t) in enumerate(input_defs)]
        self.outputs = [Socket(n, self, False, i, t) for i, (n, t) in enumerate(output_defs)]
        
        self.title_input = TextInput(
            pg.Rect(self.x, self.y, self.width, self.HEADER_HEIGHT), 
            name, 
            pg.font.SysFont('Consolas',FONT_SIZE_BASE)
        )
        self.is_editing_title = False

    def _calculate_width(self, name, input_defs, output_defs):
        """Berechnet die notwendige Breite des Knotens basierend auf Basis-Fontgröße."""
        padding = 50 
        
        base_font = pg.font.SysFont('Consolas',FONT_SIZE_BASE)
        
        title_width = base_font.render(name, True, WHITE).get_width() + 10 
        
        max_socket_width = 0
        all_defs = input_defs + output_defs
        
        for sock_name, sock_type in all_defs:
            text = f"{sock_name} ({sock_type})"
            max_socket_width = max(max_socket_width, base_font.render(text, True, WHITE).get_width())

        min_content_width = max(title_width, max_socket_width)
        
        return max(150, min_content_width + padding)

    def get_global_rect(self, editor_offset, scale):
        """Gibt das SKALIERTE Rechteck des Nodes auf dem Bildschirm zurück."""
        return pg.Rect(
            (self.x * scale) + editor_offset[0], 
            (self.y * scale) + editor_offset[1], 
            self.width * scale, 
            self.height * scale
        )
        
    def get_local_rect(self):
        """Gibt das lokale (nicht skalierte/nicht verschobene) Rechteck zurück."""
        return pg.Rect(self.x, self.y, self.width, self.height)


    def draw(self, surface, editor_offset, scale, font):
        draw_rect = self.get_global_rect(editor_offset, scale)
        header_rect = pg.Rect(draw_rect.left, draw_rect.top, draw_rect.width, self.HEADER_HEIGHT * scale)
        
        pg.draw.rect(surface, NODE_COLOR, draw_rect, border_radius=5)
        pg.draw.rect(surface, NODE_HEADER_COLOR, header_rect, border_top_left_radius=5, border_top_right_radius=5)
        
        self.title_input.font = font
        
        if font.get_height() < FONT_MIN_SIZE_DRAW:
            pass
        elif self.is_editing_title:
            self.title_input.set_rect(header_rect)
            self.title_input.draw(surface)
        else:
            text_surface = font.render(self.title_input.text, True, WHITE)
            text_rect = text_surface.get_rect(centerx=header_rect.centerx, centery=header_rect.centery)
            surface.blit(text_surface, text_rect)
        
        for socket in self.inputs + self.outputs:
            socket.draw(surface, editor_offset, scale, font)

    def handle_event(self, event, editor_offset, scale):
        
        if self.is_editing_title:
            self.title_input.rect = self.get_local_rect()
            self.title_input.handle_event(event)
            self.width = self._calculate_width(self.title_input.text, self.input_defs, self.output_defs)
            if not self.title_input.active:
                self.is_editing_title = False
        
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            draw_rect = self.get_global_rect(editor_offset, scale)
            header_rect = pg.Rect(draw_rect.left, draw_rect.top, draw_rect.width, self.HEADER_HEIGHT * scale)

            if header_rect.collidepoint(event.pos):
                self.is_editing_title = True
                self.title_input.active = True

    def get_socket_at_pos(self, pos, editor_offset, scale):
        """Sucht nach Socket-Kollision mit Mausposition (pos ist skaliert)."""
        for socket in self.inputs + self.outputs:
            sock_pos = socket.get_pos(editor_offset, scale)
            current_radius = max(2, int(socket.radius * scale))
            
            socket_rect = pg.Rect(sock_pos[0] - current_radius, sock_pos[1] - current_radius, 
                                     current_radius * 2, current_radius * 2)
            if socket_rect.collidepoint(pos):
                return socket
        return None

    def start_drag(self, mouse_pos, editor_offset, scale):
        self.is_dragging = True
        self.is_editing_title = False
        
        self.offset_x = self.x - ((mouse_pos[0] - editor_offset[0]) / scale)
        self.offset_y = self.y - ((mouse_pos[1] - editor_offset[1]) / scale)

    def stop_drag(self):
        self.is_dragging = False

    def update(self, mouse_pos, editor_offset, scale):
        if self.is_dragging:
            self.x = ((mouse_pos[0] - editor_offset[0]) / scale) + self.offset_x
            self.y = ((mouse_pos[1] - editor_offset[1]) / scale) + self.offset_y

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title_input.text,
            "x": self.x,
            "y": self.y,
            "input_defs": self.input_defs,
            "output_defs": self.output_defs
        }

class Edge:
    """Repräsentiert eine Verbindung zwischen zwei Sockets."""
    def __init__(self, start_socket, end_socket):
        self.start_socket = start_socket
        self.end_socket = end_socket
        
    def draw(self, surface, editor_offset, scale):
        """Zeichnet die Verbindungslinie als Bézier-Kurve mit Skalierung."""
        start_pos = self.start_socket.get_pos(editor_offset, scale)
        end_pos = self.end_socket.get_pos(editor_offset, scale)
        
        p1 = start_pos
        p4 = end_pos
        
        offset = 50 * scale
        p2 = (p1[0] + offset, p1[1])
        p3 = (p4[0] - offset, p4[1])
        
        line_width = max(1, int(3 * scale))
        
        try:
            draw_beziere(surface,[p1, p2, p3, p4], color=self.start_socket.get_color(),width = line_width)
        except AttributeError:
             pg.draw.line(surface, WHITE, p1, p4, line_width)

    def to_dict(self):
        return {
            "start_node_id": self.start_socket.node.id,
            "start_socket_name": self.start_socket.name,
            "end_node_id": self.end_socket.node.id,
            "end_socket_name": self.end_socket.name
        }
    
class NodeEditor:
    def __init__(self):
        self.factory = NodeFactory()
        
        self.nodes = []
        self.edges = []
        self.current_drag_socket = None
        self.drag_start_pos = None
        
        self.offset_x = 0
        self.offset_y = 0
        self.scale = 1.0
        self.is_panning = False
        
        self.ui_panel = UIPanel(self.factory, pg.Rect(0, 0, 200, SCREEN_HEIGHT), self)
        
        self.editor_font = pg.font.SysFont('Consolas',FONT_SIZE_BASE)
        
        if not self.load_state():
            start_preset = self.factory.get_preset_by_name("Start Node - Long Name")
            second_preset = self.factory.get_preset_by_name("Type Converter")
            
            if start_preset and second_preset:
                self.nodes = [
                    start_preset.create_node(250, 100),
                    second_preset.create_node(550, 100)
                ]
            else:
                 self.nodes = []

    def set_scale(self, new_scale, zoom_center_pos):
        """Ändert den Zoom-Faktor und korrigiert den Offset."""
        
        world_x = (zoom_center_pos[0] - self.offset_x) / self.scale
        world_y = (zoom_center_pos[1] - self.offset_y) / self.scale
        
        self.scale = max(0.2, min(3.0, new_scale))
        
        self.offset_x = zoom_center_pos[0] - (world_x * self.scale)
        self.offset_y = zoom_center_pos[1] - (world_y * self.scale)
        
        self.editor_font = pg.font.Font(FONT_NAME, max(2, int(FONT_SIZE_BASE * self.scale)))

    def are_types_compatible(self, type1, type2):
        """Methode zur Prüfung der Typenkompatibilität (fehlt in der vorigen Antwort, daher hier hinzugefügt, um die Vollständigkeit zu gewährleisten)."""
        if type1 == "any" or type2 == "any":
            return True
        if (type1 == "float" and type2 == "int") or (type1 == "int" and type2 == "float"):
            return True
        
        return type1 == type2

    def handle_connection(self, start_socket, target_socket):
        """Methode zur Handhabung der Verbindung zwischen Sockets."""
        if not start_socket.is_input and target_socket.is_input:
            out_sock = start_socket
            in_sock = target_socket
        elif start_socket.is_input and not target_socket.is_input:
            out_sock = target_socket
            in_sock = start_socket
        else:
            print("Ungültiger Verbindungsversuch (Input zu Input oder Output zu Output).")
            return

        if not self.are_types_compatible(out_sock.data_type, in_sock.data_type):
            print(f"❌ Verbindung ABGELEHNT: Typen inkompatibel ({out_sock.data_type} -> {in_sock.data_type}).")
            return
            
        existing_edge = next((
            edge for edge in self.edges 
            if edge.start_socket == out_sock and edge.end_socket == in_sock
        ), None)

        if existing_edge:
            self.edges.remove(existing_edge)
            print(f"Verbindung zwischen '{out_sock.node.title_input.text}.{out_sock.name}' und '{in_sock.node.title_input.text}.{in_sock.name}' GETRENNT.")
            return

        new_edge = Edge(out_sock, in_sock)
        self.edges.append(new_edge)
        print(f"Neue Verbindung zwischen '{out_sock.node.title_input.text}.{out_sock.name}' und '{in_sock.node.title_input.text}.{in_sock.name}' HERGESTELLT ({out_sock.data_type} Type).")


    def get_socket_at_pos_global(self, pos):
        """Sucht nach einem Socket an der Mausposition (pos ist skaliert/verschoben)."""
        for node in reversed(self.nodes):
            socket = node.get_socket_at_pos(pos, (self.offset_x, self.offset_y), self.scale)
            if socket:
                return socket
        return None

    def is_node_visible(self, node):
        """Prüft, ob der Node (oder Teile davon) auf dem Bildschirm sichtbar ist, mit Puffer."""
        rect = node.get_global_rect((self.offset_x, self.offset_y), self.scale)
        
        visible_rect = pg.Rect(-CULL_PADDING, -CULL_PADDING, 
                                   SCREEN_WIDTH + 2 * CULL_PADDING, 
                                   SCREEN_HEIGHT + 2 * CULL_PADDING)
        
        return rect.colliderect(visible_rect)

    def remove_node(self, node_to_remove):
        """Entfernt einen Node und alle damit verbundenen Edges."""
        
        self.edges = [
            edge for edge in self.edges 
            if edge.start_socket.node != node_to_remove and edge.end_socket.node != node_to_remove
        ]
        
        if node_to_remove in self.nodes:
            self.nodes.remove(node_to_remove)
            print(f"Node '{node_to_remove.title_input.text}' (ID: {node_to_remove.id}) entfernt.")
            return True
        return False


    def save_state(self):
        data = {
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
            "editor_offset_x": self.offset_x,
            "editor_offset_y": self.offset_y,
            "scale": self.scale,
            "next_node_id": Node.node_counter 
        }
        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"\n✅ Zustand erfolgreich in '{SAVE_FILE}' gespeichert. (S-Taste)")
            return True
        except Exception as e:
            print(f"\n❌ Fehler beim Speichern: {e}")
            return False

    def load_state(self):
        if not os.path.exists(SAVE_FILE):
            return False
            
        try:
            with open(SAVE_FILE, 'r') as f:
                data = json.load(f)

            self.nodes = []
            self.edges = []
            Node.node_counter = data.get("next_node_id", 0)

            loaded_nodes = {}
            for n_data in data["nodes"]:
                new_node = Node(
                    name=n_data["title"], 
                    x=n_data["x"], 
                    y=n_data["y"], 
                    input_defs=n_data["input_defs"],
                    output_defs=n_data["output_defs"],
                    node_id=n_data["id"]
                )
                self.nodes.append(new_node)
                loaded_nodes[new_node.id] = new_node
            
            for e_data in data["edges"]:
                start_node = loaded_nodes.get(e_data["start_node_id"])
                end_node = loaded_nodes.get(e_data["end_node_id"])
                
                if start_node and end_node:
                    start_socket = next((s for s in start_node.outputs if s.name == e_data["start_socket_name"]), None)
                    end_socket = next((s for s in end_node.inputs if s.name == e_data["end_socket_name"]), None)
                    
                    if start_socket and end_socket:
                        self.edges.append(Edge(start_socket, end_socket))

            self.offset_x = data.get("editor_offset_x", 0)
            self.offset_y = data.get("editor_offset_y", 0)
            
            self.scale = data.get("scale", 1.0)
            self.editor_font = pg.font.Font(FONT_NAME, max(2, int(FONT_SIZE_BASE * self.scale)))
            
            print(f"\n✅ Zustand erfolgreich aus '{SAVE_FILE}' geladen. (L-Taste)")
            return True

        except Exception as e:
            print(f"\n❌ Fehler beim Laden der Datei: {e}")
            return False
            
    def draw(self, surface):
        
        visible_nodes = [node for node in self.nodes if self.is_node_visible(node)]
        
        for edge in self.edges:
            start_node_visible = self.is_node_visible(edge.start_socket.node)
            end_node_visible = self.is_node_visible(edge.end_socket.node)
            
            if start_node_visible or end_node_visible:
                edge.draw(surface, (self.offset_x, self.offset_y), self.scale)

        for node in visible_nodes:
            node.draw(surface, (self.offset_x, self.offset_y), self.scale, self.editor_font)
        
        if self.current_drag_socket and self.drag_start_pos:
            p1 = self.drag_start_pos
            p4 = pg.mouse.get_pos()
            offset = 50 * self.scale
            dir_mult = -1 if self.current_drag_socket.is_input else 1
            
            drag_color = DATA_TYPES.get(self.current_drag_socket.data_type, WHITE)
            
            p2 = (p1[0] + offset * dir_mult, p1[1])
            p3 = (p4[0] - offset, p4[1])
            
            line_width = max(1, int(3 * self.scale))
            
            try:
                draw_beziere(surface,[p1, p2, p3, p4],color=drag_color,width= line_width)
            except AttributeError as E:
                print(E)
                pg.draw.line(surface, drag_color, p1, p4, line_width)
        
        self.ui_panel.draw(surface)



def main_loop():
    editor = NodeEditor()
    running = True

    while running:
        mouse_pos = pg.mouse.get_pos()
        editor_offset = (editor.offset_x, editor.offset_y)
        
        # -----------------
        # Event Handling
        # -----------------
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            
            elif event.type == pg.MOUSEWHEEL:
                zoom_factor = 1.0 + (event.y * 0.1)
                editor.set_scale(editor.scale * zoom_factor, mouse_pos)
            
            elif event.type == pg.MOUSEBUTTONDOWN and event.button in (4, 5):
                if event.button == 4:
                    editor.set_scale(editor.scale * 1.1, event.pos)
                elif event.button == 5:
                    editor.set_scale(editor.scale * 0.9, event.pos)

            # --- NODE HANDLING ---
            for node in editor.nodes:
                node.handle_event(event, editor_offset, editor.scale)
                
            editor.ui_panel.handle_event(event)

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_a: 
                    # Fügt Node hinzu (könnte auch eine Methode des Editors sein)
                    preset = random.choice(editor.factory.presets)
                    new_node_x = (SCREEN_WIDTH // 2 - editor.offset_x) / editor.scale
                    new_node_y = (SCREEN_HEIGHT // 2 - editor.offset_y) / editor.scale
                    editor.nodes.append(preset.create_node(new_node_x, new_node_y))
                if event.key == pg.K_s:
                    editor.save_state()
                if event.key == pg.K_l:
                    editor.load_state()

            elif event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if editor.ui_panel.rect.collidepoint(mouse_pos):
                        pass
                    else:
                        clicked_socket = editor.get_socket_at_pos_global(mouse_pos)
                        
                        if clicked_socket:
                            editor.current_drag_socket = clicked_socket
                            editor.drag_start_pos = clicked_socket.get_pos(editor_offset, editor.scale)
                        else:
                            clicked_node = None
                            for node in reversed(editor.nodes):
                                if node.get_global_rect(editor_offset, editor.scale).collidepoint(mouse_pos):
                                    if not node.is_editing_title:
                                        clicked_node = node
                                        break
                                    
                            if clicked_node:
                                clicked_node.start_drag(mouse_pos, editor_offset, editor.scale)
                            else:
                                editor.is_panning = True
                                editor.pan_start_x = mouse_pos[0] - editor.offset_x
                                editor.pan_start_y = mouse_pos[1] - editor.offset_y
                
                elif event.button == 3: # Rechtsklick (Löschen)
                    clicked_node = None
                    for node in reversed(editor.nodes):
                        if node.get_global_rect(editor_offset, editor.scale).collidepoint(mouse_pos):
                            clicked_node = node
                            break
                    
                    if clicked_node:
                        editor.remove_node(clicked_node)


            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1:
                    for node in editor.nodes:
                        node.stop_drag()

                    if editor.current_drag_socket:
                        target_socket = editor.get_socket_at_pos_global(mouse_pos)
                        
                        if target_socket and target_socket != editor.current_drag_socket:
                            # AUFRUF VON 'editor.handle_connection'
                            editor.handle_connection(editor.current_drag_socket, target_socket)
                        
                        editor.current_drag_socket = None
                        editor.drag_start_pos = None

                    editor.is_panning = False
        
        # -----------------
        # Aktualisierung
        # -----------------
        for node in editor.nodes:
            node.update(mouse_pos, editor_offset, editor.scale)
            
        if editor.is_panning:
            editor.offset_x = mouse_pos[0] - editor.pan_start_x
            editor.offset_y = mouse_pos[1] - editor.pan_start_y


        # -----------------
        # Zeichnen
        # -----------------
        SCREEN.fill(BLACK)
        
        editor.draw(SCREEN)

        pg.display.flip()
        CLOCK.tick(60)

    pg.quit()


if __name__ == "__main__":
    main_loop()