import PySide6.QtWidgets as QtW


class OutputField(QtW.QLineEdit):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setReadOnly(True)
        self.setStyleSheet("background: palette(window);")
