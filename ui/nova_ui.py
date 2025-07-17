from PyQt6 import QtWidgets, QtCore, QtGui
import sys
import psutil
from voice.text_to_speech import get_tts

class GlowingAvatar(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(48, 48)
        self.state = 'idle'
        self.anim = QtCore.QVariantAnimation(self)
        self.anim.valueChanged.connect(self.update)
        self.anim.setStartValue(0)
        self.anim.setEndValue(360)
        self.anim.setDuration(1200)
        self.anim.setLoopCount(-1)
        self.set_state('idle')

    def set_state(self, state):
        self.state = state
        if state == 'listening':
            self.anim.setDuration(600)
            self.anim.setLoopCount(-1)
            self.anim.start()
        elif state == 'thinking':
            self.anim.setDuration(1200)
            self.anim.setLoopCount(-1)
            self.anim.start()
        else:
            self.anim.stop()
            self.update()

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        r = self.rect()
        color = QtGui.QColor('#00ffe7')
        if self.state == 'listening':
            color.setAlpha(220)
        elif self.state == 'thinking':
            color = QtGui.QColor('#ffea00')
            color.setAlpha(180)
        else:
            color.setAlpha(100)
        pen = QtGui.QPen(color, 4)
        qp.setPen(pen)
        qp.setBrush(QtCore.Qt.BrushStyle.NoBrush)
        angle = self.anim.currentValue() if self.anim.state() == QtCore.QAbstractAnimation.State.Running else 0
        if self.state == 'listening':
            qp.drawEllipse(r.adjusted(6, 6, -6, -6))
            qp.setPen(QtGui.QPen(color, 2))
            qp.drawArc(r.adjusted(12, 12, -12, -12), int(angle*16), 120*16)
        elif self.state == 'thinking':
            qp.drawEllipse(r.adjusted(8, 8, -8, -8))
            qp.setPen(QtGui.QPen(color, 3))
            qp.drawArc(r.adjusted(4, 4, -4, -4), int(angle*16), 270*16)
        else:
            qp.drawEllipse(r.adjusted(10, 10, -10, -10))
        qp.end()

class NovaUI(QtWidgets.QWidget):
    def __init__(self, engine):
        super().__init__()
        self.engine = engine
        self.idle_timer = QtCore.QTimer(self)
        self.idle_timer.setInterval(5000)
        self.idle_timer.timeout.connect(self.hide)
        self.init_ui()

    def reset_idle_timer(self):
        self.idle_timer.stop()
        self.idle_timer.start()

    def init_ui(self):
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint | QtCore.Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(400, 240)
        screen = QtWidgets.QApplication.primaryScreen().geometry()
        self.move(screen.width() - 440, screen.height() - 300)

        # Neon/glass effect placeholder
        self.setStyleSheet("background: rgba(30, 30, 40, 0.7); border-radius: 20px; border: 2px solid #00ffe7;")

        layout = QtWidgets.QVBoxLayout(self)
        self.input = QtWidgets.QLineEdit(self)
        self.input.setPlaceholderText("Ask NOVA...")
        self.input.returnPressed.connect(self.on_enter)
        self.input.installEventFilter(self)
        self.input.textEdited.connect(self.pause_idle_timer)
        self.input.editingFinished.connect(self.resume_idle_timer)
        layout.addWidget(self.input)

        # Animated glowing circle/avatar
        self.avatar = GlowingAvatar(self)
        layout.addWidget(self.avatar, alignment=QtCore.Qt.AlignmentFlag.AlignHCenter)

        # Suggestions area
        self.suggestions = QtWidgets.QWidget(self)
        self.suggestions_layout = QtWidgets.QHBoxLayout(self.suggestions)
        self.suggestions.setLayout(self.suggestions_layout)
        layout.addWidget(self.suggestions)
        self.update_suggestions()

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

        self.reset_idle_timer()

    def eventFilter(self, obj, event):
        if obj == self.input:
            if event.type() == QtCore.QEvent.Type.FocusIn:
                self.pause_idle_timer()
            elif event.type() == QtCore.QEvent.Type.FocusOut:
                self.resume_idle_timer()
        return super().eventFilter(obj, event)

    def pause_idle_timer(self):
        self.idle_timer.stop()

    def resume_idle_timer(self):
        self.reset_idle_timer()

    @QtCore.pyqtSlot(str)
    def set_avatar_state(self, state):
        self.avatar.set_state(state)
        self.reset_idle_timer()

    def update_suggestions(self):
        # Clear old suggestions
        for i in reversed(range(self.suggestions_layout.count())):
            w = self.suggestions_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        # Get suggestions from brain
        brain = getattr(self.engine, 'brain', None)
        if not brain:
            return
        suggestions = brain.suggest() + brain.get_habits()
        shown = set()
        for cmd in suggestions:
            if cmd in shown:
                continue
            btn = QtWidgets.QPushButton(cmd, self)
            btn.setStyleSheet("background: rgba(0,255,231,0.12); color: #00ffe7; border-radius: 8px; padding: 4px 10px; margin: 2px; font-size: 13px;")
            btn.clicked.connect(lambda _, c=cmd: self.handle_and_display(c))
            self.suggestions_layout.addWidget(btn)
            shown.add(cmd)
        self.reset_idle_timer()

    def enterEvent(self, event):
        # Show real system info
        cpu = psutil.cpu_percent(interval=0.2)
        ram = psutil.virtual_memory().percent
        self.sysinfo.setText(f"CPU: {cpu}%  RAM: {ram}%")
        self.sysinfo.show()
        self.reset_idle_timer()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.sysinfo.hide()
        self.reset_idle_timer()
        super().leaveEvent(event)

    def on_enter(self):
        command = self.input.text()
        self.handle_and_display(command)
        self.input.clear()
        self.update_suggestions()
        self.reset_idle_timer()

    def handle_and_display(self, command):
        result = self.engine.handle_command(command)
        if result.get("status") == "confirm":
            reply = QtWidgets.QMessageBox.question(self, "Confirm Action", result["message"], QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                # Send confirmation to engine
                result = self.engine.handle_command("yes")
            else:
                result = self.engine.handle_command("no")
        if result.get("status") == "ok":
            self.result.setStyleSheet("color: #00ffe7; font-size: 15px; padding: 8px; border-radius: 10px; background: rgba(0,255,231,0.08); margin-top: 8px;")
        else:
            self.result.setStyleSheet("color: #ff4b6e; font-size: 15px; padding: 8px; border-radius: 10px; background: rgba(255,75,110,0.08); margin-top: 8px;")
        self.result.setText(result.get("message", str(result)))
        # Speak the result
        get_tts().speak(result.get("message", ""))
        self.update_suggestions()
        self.reset_idle_timer()

    @QtCore.pyqtSlot()
    def show_and_focus(self):
        self.show()
        self.raise_()
        self.activateWindow()
        self.input.setFocus()
        self.update_suggestions()
        self.reset_idle_timer()

    @QtCore.pyqtSlot(str)
    def accept_voice_command(self, command):
        self.show_and_focus()
        self.handle_and_display(command)
        self.reset_idle_timer()

    def run(self):
        self.show()
        self.reset_idle_timer() 