from PyQt6 import QtWidgets, QtGui, QtCore

class GlowingAvatar(QtWidgets.QLabel):
    def __init__(self, name="NOVA"):
        super().__init__(name)
        self.setStyleSheet("color: #00ffe7; font-size: 18px; font-weight: bold; text-shadow: 0 0 10px #00ffe7;")
        # Placeholder for animation 