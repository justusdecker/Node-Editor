# 👾 Pygame Node Editor (UI Refactoring Project)

Project Name: Pynodle(will be changed in GitHub later)

A performant and modular visual Node Editor, developed with Pygame.
This project aims to refactor the core architecture of an existing Node Editor and implement a robust, extensible library of custom UI elements. 

*✨ Key Features & GoalsBased* on the development plan, the focus is on creating a professional user experience and modular components *🎴 Phase 2: Add all needed UI Elements* Fully functional text fields with cursor handling and keyboard focus.

You find the currently planned UI-Elements [here](#-phase-2-add-all-needed-ui-elements)

# 💻 Installation (Placeholder)
Installation details will follow shortly.
```bash
git clone git@github.com:justusdecker/Node-Editor.git
```

Install dependencies: 
```bash
pip install -r requirements.txt
```
Run:
```bash
python main.py
```

# 🧰 Quick & Dirty Preview 
How this should look in the future:

![test](demo/preview%20node.png)

# 🗺️ Development Plan: 

Node Editor UI/Refactoring
This plan details the process for refactoring the existing core and implementing the specialized UI components, ensuring a robust and extensible foundation.

## 🏗️ Phase 1: Refactoring and Base Structure Optimization (Foundation)Goal: 

* Basic UI Structure(draw, handle_input & draw)
In this structure we need to get the highest in the Z-Layer and block all the other.
Maybe copying the code from the PygameEngine Project?

* Remove AI garbage
* Ensure a clean, maintainable, and performant core codebase.
* Simplify Node management (creation, deletion, serialization/deserialization)
* Better event handling.
* First inputs & then outputs not in / out on the same line!
* Visual Feedback: Clear visual highlighting (Outlining) for the currently selected Node.

### 🐍 Python Pseudocode (Phase 1)
```python
# Base Class for all interactable components
class UIElement:
    def __init__(self, rect):
        self.rect = rect
        self.is_focused = False
        self.is_clicked = False
        self.last_frame_hovered = False
        self.last_frame_clicked = False
        self.is_pressed = False

    def draw(self, screen):
        # Implement rendering logic specific to the element
        pass

    def handle_input(self, event):
        # Process mouse clicks, key presses, etc. Return True if input was consumed.
        return False

    def check_collision(self, pos):
        # Check if position 'pos' is within the element's bounding box
        return self.rect.collidepoint(pos)
```
## 🎴 Phase 2: Add all needed UI Elements
Add a variety of new UI Elements
* [ ] Node
    * Clicking, holding the header and moving the mouse will move the Node accross the space.
    * Clicking and releasing on the header will let the user input a new title
    * Clicking on X will remove the Node
    * Clicking on the arrow will holster / unholster the Node(Activate / Deactivate UI)
* [x] Button
* [ ] DragButton(For Knot Connections & Nodes)
    * uses the `press` attribute to get the `draggablilty`

* [x] SpinBox
* [x] ColorPicker(currently show color & use the tkinter colorpicker for simplicity)
* [x] TextInput(With Type Check)
* [x] MultiLineTextInput
* [x] DropDown
* [x] MenuBar
* [x] SideBar(For Settings etc.)

## 🛡️ Phase 3: UI Blocking System & Focus Management (The Overlap Fix)
### Goal: Prevent overlapping input events (like a button click activating a node drag underneath).

TaskDescriptionInput ManagerImplement a centralized InputManager to control the flow of Pygame events.Blocking StackUse a LIFO (Last-In, First-Out) stack (blocking_elements) where elements like active TextInputs or open DropDowns can register to receive exclusive input.Input DistributionLogic to check the stack first. If blocked, only send input to the top element; otherwise, distribute to all general elements (Nodes, non-focused Buttons).
## 🐍 Python Pseudocode (Phase 3)class InputManager:
```python
    def __init__(self):
        self.blocking_elements = [] # Stack for exclusive input focus

    def push_blocker(self, element):
        self.blocking_elements.append(element)

    def distribute_input(self, event):
        if self.blocking_elements:
            # Only the top element receives input
            top_element = self.blocking_elements[-1]
            top_element.handle_input(event)
        else:
            # Distribute to all general elements (Nodes, Buttons on the Canvas)
            for element in all_canvas_elements:
                if element.handle_input(event):
                    break # Input consumed, stop checking
```

## ✨ Phase 4: Visual Feedback and PolishingGoal: 
Provide clear visual context to the user.FeatureImplementation NotesNode OutliningAdd an is_selected state to the Node class. When true, draw a distinct, high-contrast border (e.g., bright yellow) around the Node's bounding box.Z-Order CheckConfirm that the outline is drawn above the node's background but below any foreground UI elements within the node.
### 🐍 Python Pseudocode (Phase 4)class Node:
```python
    # ... (initialization code)

    def draw(self, screen):
        # 1. Draw Node background
        pygame.draw.rect(screen, self.color, self.rect)

        # 2. Draw Selection Outline (ensures visual feedback is clear)
        if self.is_selected:
            # Inflate rect to create a border outside the main body
            outline_rect = self.rect.inflate(4, 4) 
            pygame.draw.rect(screen, (255, 255, 0), outline_rect, 3) # Yellow border

        # 3. Draw contained UI elements (Buttons, TextInputs, etc.)
        for element in self.ui_elements:
            element.draw(screen)
```