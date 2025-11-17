# 👾 Pygame Node Editor (UI Refactoring Project)

Project Name: Pynodle(will be changed in GitHub later)

A performant and modular visual Node Editor, developed with Pygame.
This project aims to refactor the core architecture of my Node Editor and implement a robust, extensible library of custom UI elements. 

*✨ Key Features & GoalsBased* on the development plan, the focus is on creating a professional user experience and modular components.

You find the currently planned UI-Elements [here](#-phase-2-add-all-needed-ui-elements)

# 💻 Installation
```bash
git clone git@github.com:justusdecker/Node-Editor.git
```

Install dependencies: 
```bash
pip install -r requirements.txt
```
Run(UIPreview):
```bash
python main.py
```

# 🧰 Dirty Preview 

<img src="./demo/preview.png" width="50%">


# 🗺️ Development Plan: 

This plan details the process for refactoring the existing core and implementing the specialized UI components, ensuring a robust and extensible foundation.

### 🛡️ Phase 1: UIManager(UI Blocking System / Overlap Fix)
* [x] Creating a UIManager that prevent from clicking trough overlapping elements
* [x] Custom Pygame Event Handling for UI Elements
### 🎛 Phase 2: Add the "Essential UIE"
* [x] UIElement(act as button)
* [x] TextInput
### 🎴 Phase 3: Add all needed UI Elements
Add a variety of new UI Elements
* [ ] Node
    * Clicking, holding the header and moving the mouse will move the Node accross the space.
    * Clicking and releasing on the header will let the user input a new title
    * Clicking on X will remove the Node
    * Clicking on the arrow will holster / unholster the Node(Activate / Deactivate UI)
* [ ] DragButton(For Knot Connections & Nodes)
    * uses the `press` attribute to get the `draggablilty`
* [x] SpinBox
* [x] ColorPicker(currently show color & use the tkinter colorpicker for simplicity)
* [x] DropDown
* [x] MenuBar
* [x] SideBar(For Settings etc.)
### ✨ Phase 4: Visual Feedback / UX fixes & layouts
Fix the broken UX Offsets etc.
### 🧰 Phase 5: Polishing
* [ ] Fix major flaws in the UIManager / UIElements
### 📃 Phase 6: Documentation