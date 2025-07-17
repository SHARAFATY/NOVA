from PyQt6 import QtWidgets, QtCore, QtGui
import sys
import psutil
from voice.text_to_speech import get_tts

class NovaUI(QtWidgets.QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(400, 180)
        self.move(40, QtWidgets.QApplication.primaryScreen().size().height() - 240)

        # Neon/glass effect placeholder
        self.setStyleSheet("background: rgba(30, 30, 40, 0.7); border-radius: 20px; border: 2px solid #00ffe7;")

        layout = QtWidgets.QVBoxLayout(self)
        self.input = QtWidgets.QLineEdit(self)
        self.input.setPlaceholderText("Ask NOVA...")
        self.input.returnPressed.connect(self.on_enter)
        layout.addWidget(self.input)

        # Placeholder for glowing circle/avatar
        self.avatar = QtWidgets.QLabel("NOVA", self)
        self.avatar.setStyleSheet("color: #00ffe7; font-size: 18px; font-weight: bold; text-shadow: 0 0 10px #00ffe7;")
        layout.addWidget(self.avatar)

        # Result display area
        self.result = QtWidgets.QLabel("", self)
        self.result.setWordWrap(True)
        self.result.setStyleSheet("color: #e0f7fa; font-size: 15px; padding: 8px; border-radius: 10px; background: rgba(0,255,231,0.08); margin-top: 8px;")
        layout.addWidget(self.result)

        # System info on hover (real values)
        self.sysinfo = QtWidgets.QLabel("", self)
        self.sysinfo.setStyleSheet("color: #00ffe7; font-size: 13px; background: transparent;")
        self.sysinfo.hide()
        layout.addWidget(self.sysinfo)
        self.setLayout(layout)

    def enterEvent(self, event):
        # Show real system info
        cpu = psutil.cpu_percent(interval=0.2)
        ram = psutil.virtual_memory().percent
        self.sysinfo.setText(f"CPU: {cpu}%  RAM: {ram}%")
        self.sysinfo.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.sysinfo.hide()
        super().leaveEvent(event)

    def on_enter(self):
        command = self.input.text()
        self.handle_and_display(command)
        self.input.clear()

    def handle_and_display(self, command):
        result = self.engine.handle_command(command)
        if result.get("status") == "ok":
            self.result.setStyleSheet("color: #00ffe7; font-size: 15px; padding: 8px; border-radius: 10px; background: rgba(0,255,231,0.08); margin-top: 8px;")
        else:
            self.result.setStyleSheet("color: #ff4b6e; font-size: 15px; padding: 8px; border-radius: 10px; background: rgba(255,75,110,0.08); margin-top: 8px;")
        self.result.setText(result.get("message", str(result)))
        # Speak the result
        get_tts().speak(result.get("message", ""))

    def show_and_focus(self):
        self.show()
        self.raise_()
        self.activateWindow()
        self.input.setFocus()

    def accept_voice_command(self, command):
        self.show_and_focus()
        self.handle_and_display(command)

    def run(self):
        app = QtWidgets.QApplication(sys.argv)
        self.show()
        sys.exit(app.exec()) 