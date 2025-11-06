from src.ui.ui_element import UIElement

class UIButton(UIElement):
    def __init__(self, app, pos, size, **kwargs):
        super().__init__(app, pos, size, **kwargs)
        