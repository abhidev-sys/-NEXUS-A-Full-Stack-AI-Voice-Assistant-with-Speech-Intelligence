from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget,
    QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton,
    QFrame, QLabel, QSizePolicy, QGraphicsDropShadowEffect, QStackedLayout
)
from PyQt5.QtGui import (
    QIcon,
    QPainter,
    QMovie,
    QColor,
    QTextCharFormat,
    QFont,
    QPixmap,
    QTextBlockFormat,
    QPen,
    QLinearGradient,
    QBrush,
)

from PyQt5.QtCore import Qt, QSize, QTimer, QPointF, QDateTime
import random
from dotenv import dotenv_values
import sys
import os


# load the important .env and more variables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname") or "Assistant"
current_dir = os.getcwd()
old_chat_message = ""
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TempDirPath = os.path.join(BASE_DIR, "Data")
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"


# ============================================================
#  THEME  —  single source of truth for the futuristic palette
#  (change these values and the whole UI re-tunes itself)
# ============================================================
class Theme:
    BG = "#050b12"              # deep space background
    PANEL = "#0a141f"           # panel / bar background
    PANEL_EDGE = "rgba(0, 220, 255, 45)"
    CYAN = "#00e5ff"
    CYAN_DIM = "#0090b0"
    BLUE = "#0078b4"
    VIOLET = "#7c4dff"
    AMBER = "#ffb347"
    GREEN = "#38ffb0"
    TEXT = "#e8f6ff"
    TEXT_DIM = "#7fa8bf"
    DANGER = "#ff5566"


def getGraphicsPath(filename):
    return rf"{GraphicsDirPath}\{filename}"


def GraphicsDirectoryPath(Filename):
    Path = rf'{GraphicsDirPath}\{Filename}'
    return Path


def TempDirectoryPath(Filename):
    Path = rf'{TempDirPath}\{Filename}'
    return Path


# ============================================================
#  PARTICLE FIELD  —  animated HUD starfield used as a live
#  background layer behind the home screen content
# ============================================================
class ParticleField(QWidget):
    def __init__(self, parent=None, count=90):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.particles = []
        for _ in range(count):
            self.particles.append({
                "x": random.uniform(0, 1),
                "y": random.uniform(0, 1),
                "speed": random.uniform(0.00006, 0.00035),
                "size": random.uniform(1.0, 2.6),
                "phase": random.uniform(0, 6.28),
                "violet": random.random() < 0.18,
            })

        self.tick = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._advance)
        self.timer.start(33)  # ~30 FPS is plenty for a subtle background

    def _advance(self):
        self.tick += 1
        for p in self.particles:
            p["y"] -= p["speed"]
            if p["y"] < 0:
                p["y"] = 1.0
                p["x"] = random.uniform(0, 1)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setPen(Qt.NoPen)

        w, h = self.width(), self.height()
        for particle in self.particles:
            twinkle = 0.5 + 0.5 * ((self.tick * 0.05 + particle["phase"]) % 6.28 / 6.28)
            alpha = int(40 + 90 * twinkle)
            color = QColor(124, 77, 255, alpha) if particle["violet"] else QColor(0, 220, 255, alpha)
            p.setBrush(color)
            x = particle["x"] * w
            y = particle["y"] * h
            r = particle["size"]
            p.drawEllipse(QPointF(x, y), r, r)


# ============================================================
#  ARC REACTOR  —  core HUD centerpiece
#  same animation timers / angles / drag behaviour as before,
#  repainted with a live HUD grid + richer glow layering
# ============================================================
class ArcReactor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(420, 420)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Animation states
        self.outer_angle = 0
        self.inner_angle = 0
        self.scan_angle = 0
        self.micro_angle = 0

        self.pulse = 0
        self.pulse_up = True

        # HUD background animation
        self.grid_offset = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(16)  # ~60 FPS

        self.drag_pos = None

    # ---------------- ANIMATION ----------------
    def animate(self):
        self.outer_angle += 0.4
        self.inner_angle -= 0.7
        self.scan_angle += 2.2
        self.micro_angle += 3.5

        self.grid_offset = (self.grid_offset + 0.6) % 40

        if self.pulse_up:
            self.pulse += 0.4
            if self.pulse > 14:
                self.pulse_up = False
        else:
            self.pulse -= 0.4
            if self.pulse < 0:
                self.pulse_up = True

        self.update()

    # ---------------- PAINT ----------------
    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        center = QPointF(self.width() / 2, self.height() / 2)

        # ===== LIVE HUD GRID (uses grid_offset, previously unused) =====
        p.setPen(QPen(QColor(0, 200, 255, 18), 1))
        p.save()
        p.setClipRect(0, 0, self.width(), self.height())
        step = 40
        offset = self.grid_offset
        for x in range(-step, self.width() + step, step):
            p.drawLine(int(x + offset), 0, int(x + offset), self.height())
        for y in range(-step, self.height() + step, step):
            p.drawLine(0, int(y + offset), self.width(), int(y + offset))
        p.restore()

        # ===== SOFT FUTURISTIC BACKGROUND =====
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(0, 120, 180, 55))
        p.drawEllipse(center, 210, 210)

        p.setBrush(QColor(0, 0, 0, 130))
        p.drawEllipse(center, 190, 190)

        # ===== HUD CIRCULAR GRID =====
        p.setPen(QPen(QColor(0, 200, 255, 35), 1))
        for r in range(140, 230, 20):
            p.drawEllipse(center, r, r)

        # ===== TICK MARKS AROUND THE OUTER RIM =====
        p.save()
        p.translate(center)
        p.setPen(QPen(QColor(0, 220, 255, 90), 2))
        for i in range(0, 360, 6):
            p.save()
            p.rotate(i)
            length = 10 if i % 30 == 0 else 5
            p.drawLine(0, -205, 0, -205 + length)
            p.restore()
        p.restore()

        # ===== OUTER SOFT GLOW =====
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(0, 200, 255, 40))
        p.drawEllipse(center, 95, 95)

        # ===== MID GLOW =====
        p.setBrush(QColor(0, 200, 255, 90))
        p.drawEllipse(center, 70, 70)

        # ===== CORE ENERGY =====
        core_radius = 35 + self.pulse
        core_grad = QLinearGradient(
            center.x() - core_radius, center.y() - core_radius,
            center.x() + core_radius, center.y() + core_radius,
        )
        core_grad.setColorAt(0, QColor(180, 245, 255))
        core_grad.setColorAt(0.5, QColor(0, 220, 255))
        core_grad.setColorAt(1, QColor(0, 130, 200))
        p.setBrush(QBrush(core_grad))
        p.drawEllipse(center, core_radius, core_radius)

        # ===== INNER RING =====
        p.setPen(QPen(QColor(0, 220, 255, 140), 4))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(center, 55, 55)

        # ===== SOLID ROTATING RING =====
        p.save()
        p.translate(center)
        p.rotate(self.outer_angle)
        p.setPen(QPen(QColor(0, 200, 255, 180), 4))
        p.drawEllipse(QPointF(0, 0), 120, 120)
        p.restore()

        # ===== DASHED INNER RING =====
        p.save()
        p.translate(center)
        p.rotate(self.inner_angle)
        pen = QPen(QColor(0, 160, 255, 160), 3)
        pen.setDashPattern([8, 10])
        p.setPen(pen)
        p.drawEllipse(QPointF(0, 0), 150, 150)
        p.restore()

        # ===== MICRO FAST RING (accent violet for depth) =====
        p.save()
        p.translate(center)
        p.rotate(self.micro_angle)
        pen = QPen(QColor(124, 77, 255, 190), 2)
        pen.setDashPattern([2, 14])
        p.setPen(pen)
        p.drawEllipse(QPointF(0, 0), 115, 115)
        p.restore()

        # ===== BROKEN SEGMENTS =====
        p.setPen(QPen(QColor(0, 220, 255), 4))
        for i in range(0, 360, 24):
            p.drawArc(
                int(center.x() - 185),
                int(center.y() - 185),
                370,
                370,
                i * 16,
                10 * 16
            )

        # ===== SCAN HUD ARC =====
        p.save()
        p.translate(center)
        p.rotate(self.scan_angle)

        p.setPen(QPen(QColor(0, 255, 255, 190), 6))
        p.drawArc(-160, -160, 320, 320, 0, 40 * 16)

        p.setPen(QPen(QColor(0, 255, 255, 60), 14))
        p.drawArc(-160, -160, 320, 320, 0, 40 * 16)

        p.restore()

    # ---------------- DRAG ----------------
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.drag_pos = e.globalPos()

    def mouseMoveEvent(self, e):
        if self.drag_pos:
            delta = e.globalPos() - self.drag_pos
            self.move(self.pos() + delta)
            self.drag_pos = e.globalPos()

    def mouseReleaseEvent(self, e):
        self.drag_pos = None


def AnswerModifire(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer


# function for the user input
def QueryModifier(Query):

    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", " can you", "what's", "where's", "how's", ]

    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"

    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."

    return new_query.capitalize()


# ---------------- define the function one by one ----------------

def SetMicrophoneStatus(Command):
    with open(rf'{TempDirPath}\MIC.data', "w", encoding='utf-8') as file:
        file.write(Command)


def GetMicrophoneStatus():
    with open(rf'{TempDirPath}\MIC.data', "r", encoding='utf-8') as file:
        Status = file.read()
    return Status


def SetAssistantStatus(text):
    with open(rf'{TempDirPath}\Status.data', "w", encoding='utf-8') as file:
        file.write(text)


def GetAssistantStatus():
    with open(rf'{TempDirPath}\Status.data', "r", encoding='utf-8') as file:
        Status = file.read()
    return Status


def MicButtonInitialed():
    SetMicrophoneStatus("True")


def MicbuttonClosed():
    SetMicrophoneStatus("False")


def ShowTextToScreen(Text):
    with open(rf'{TempDirPath}\Response.data', "w", encoding="utf-8") as file:
        file.write(Text)


# ============================================================
#  CHAT SECTION  —  now renders as left/right HUD bubbles
#  instead of flat plain-text lines. File reading logic and
#  timer cadence are untouched.
# ============================================================
class ChatSection(QWidget):

    def __init__(self):
        super(ChatSection, self).__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 30, 20, 20)
        layout.setSpacing(14)

        # ---------------- CHAT TEXT ----------------
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        self.chat_text_edit.setFont(QFont("Segoe UI", 12))
        self.chat_text_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {Theme.BG};
                border: none;
                border-radius: 10px;
                padding: 10px;
            }}
            QScrollBar:vertical {{
                background: transparent;
                width: 8px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(0, 220, 255, 90);
                border-radius: 4px;
                min-height: 30px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)
        layout.addWidget(self.chat_text_edit)

        text_format = QTextCharFormat()
        text_format.setForeground(QColor(Theme.TEXT))
        self.chat_text_edit.setCurrentCharFormat(text_format)

        # ---------------- GIF ----------------
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")

        movie = QMovie(getGraphicsPath("Jarvis.gif"))
        movie.setScaledSize(QSize(340, 190))
        self.gif_label.setMovie(movie)
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        movie.start()

        layout.addWidget(self.gif_label)

        # ---------------- STATUS LABEL ----------------
        self.label = QLabel("")
        self.label.setStyleSheet(f"""
            QLabel {{
                color: {Theme.CYAN};
                font-size: 15px;
                font-weight: 600;
                margin-right: 10px;
                border: none;
            }}
        """)
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)

        # ---------------- TIMER ----------------
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(200)

        # ---------------- STYLE ----------------
        self.setStyleSheet(f"""
            ChatSection {{
                background-color: {Theme.BG};
            }}
        """)

    def loadMessages(self):
        global old_chat_message

        path = TempDirectoryPath('RESPONSES.DATA')
        if not os.path.exists(path):
            print("Response file not found", path)
            return

        with open(path, "r", encoding=' utf-8') as file:
            messages = file.read().strip()

        if not messages:
            return

        if messages == old_chat_message:
            return

        self.addMessage(messages, color='white')
        old_chat_message = messages

    def SpeechRecogText(self):
        if os.path.exists(TempDirectoryPath("Status.data")):
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                self.label.setText(messages)
                self._styleStatusLabel(messages)

    def _styleStatusLabel(self, status_text):
        """Colour the status label based on what state it reports.
        Purely cosmetic — reads the same string, no logic changed."""
        s = status_text.lower()
        if "listen" in s:
            color = Theme.CYAN
        elif "think" in s or "search" in s:
            color = Theme.AMBER
        elif "answer" in s:
            color = Theme.VIOLET
        elif "available" in s:
            color = Theme.GREEN
        else:
            color = Theme.TEXT_DIM
        self.label.setStyleSheet(f"""
            QLabel {{
                color: {color};
                font-size: 15px;
                font-weight: 600;
                margin-right: 10px;
                border: none;
            }}
        """)

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggel_icon(self, event=None):
        pass
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('voice.png'), 60, 60)
            MicButtonInitialed()
        else:
            self.load_icon(GraphicsDirectoryPath('mic.png'), 60, 60)
            MicbuttonClosed()
        self.toggled = not self.toggled

    def addMessage(self, message, color):
        """Renders the message as a HUD-style chat bubble.
        Assistant lines float left in a cyan-glass bubble,
        everything else floats right in a brighter cyan bubble."""
        cursor = self.chat_text_edit.textCursor()

        stripped = message.strip()
        is_assistant = stripped.lower().startswith(Assistantname.lower())

        block_format = QTextBlockFormat()
        block_format.setTopMargin(8)
        block_format.setBottomMargin(8)

        char_format = QTextCharFormat()

        if is_assistant:
            block_format.setAlignment(Qt.AlignLeft)
            block_format.setLeftMargin(10)
            block_format.setRightMargin(120)
            block_format.setBackground(QColor(0, 150, 200, 35))
            char_format.setForeground(QColor(Theme.TEXT))
        else:
            block_format.setAlignment(Qt.AlignRight)
            block_format.setLeftMargin(120)
            block_format.setRightMargin(10)
            block_format.setBackground(QColor(0, 229, 255, 28))
            char_format.setForeground(QColor("#ffffff"))

        cursor.movePosition(cursor.End)
        cursor.insertBlock(block_format)
        cursor.setCharFormat(char_format)
        cursor.insertText(message)
        self.chat_text_edit.setTextCursor(cursor)


# in this section we initialize all the components
class InitialScreen(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen = QApplication.primaryScreen().size()
        screen_width = screen.width()
        screen_height = screen.height()

        self.setFixedSize(screen_width, screen_height)
        self.setStyleSheet(f"background-color: {Theme.BG};")

        # ---------------- LAYERED BACKGROUND ----------------
        # StackAll means every layer paints on top of the previous one,
        # instead of only showing whichever widget is "current".
        root_layout = QStackedLayout(self)
        root_layout.setStackingMode(QStackedLayout.StackAll)

        self.particles = ParticleField(self)
        root_layout.addWidget(self.particles)

        content = QWidget()
        content.setAttribute(Qt.WA_TranslucentBackground)
        content.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 0, 150)

        self.gif_label = QLabel()
        movie = QMovie(getGraphicsPath("Jarvis.gif"))
        movie.setScaledSize(QSize(screen_width, int(screen_width * 9 / 16)))
        self.gif_label.setMovie(movie)
        self.gif_label.setAlignment(Qt.AlignCenter)
        movie.start()

        # ---------------- BRAND TITLE ----------------
        self.title_label = QLabel("N E X U S   A I")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(f"""
            color: {Theme.CYAN};
            font-size: 30px;
            font-weight: 800;
            background: transparent;
        """)
        self.title_glow = self._addGlow(self.title_label, Theme.CYAN, blur=28)

        self.label = QLabel("")
        self.label.setStyleSheet(f"color:{Theme.TEXT_DIM}; font-size:15px; font-weight:500; background: transparent;")
        self.label.setAlignment(Qt.AlignCenter)
        self._addGlow(self.label, Theme.CYAN, blur=18)

        self.icon_label = QLabel()
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.arc = ArcReactor()

        # ---------------- HUD TELEMETRY ROW (decorative + live uptime) ----------------
        self.telemetry_label = QLabel("")
        self.telemetry_label.setAlignment(Qt.AlignCenter)
        self.telemetry_label.setStyleSheet(f"""
            color: {Theme.CYAN_DIM};
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 2px;
            background: transparent;
        """)

        layout.addStretch()
        layout.addWidget(self.title_label)
        layout.addSpacing(10)
        layout.addWidget(self.arc, alignment=Qt.AlignCenter)
        layout.addSpacing(6)
        layout.addWidget(self.label)
        layout.addSpacing(4)
        layout.addWidget(self.telemetry_label)
        layout.addStretch()

        root_layout.addWidget(content)
        self.setLayout(root_layout)

        # ---------------- STATUS POLL TIMER (unchanged cadence) ----------------
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(300)
        self.toggled = False

        # ---------------- LIVE UPTIME ----------------
        self.start_time = QDateTime.currentDateTime()
        self.uptime_timer = QTimer(self)
        self.uptime_timer.timeout.connect(self._updateTelemetry)
        self.uptime_timer.start(1000)
        self._updateTelemetry()

        # ---------------- BREATHING GLOW ON THE TITLE ----------------
        self._glow_dir = 1
        self.glow_timer = QTimer(self)
        self.glow_timer.timeout.connect(self._breatheGlow)
        self.glow_timer.start(40)

    def _addGlow(self, widget, color, blur=25):
        glow = QGraphicsDropShadowEffect(widget)
        glow.setBlurRadius(blur)
        glow.setColor(QColor(color))
        glow.setOffset(0, 0)
        widget.setGraphicsEffect(glow)
        return glow

    def _breatheGlow(self):
        blur = self.title_glow.blurRadius()
        blur += self._glow_dir * 0.6
        if blur > 42:
            self._glow_dir = -1
        elif blur < 18:
            self._glow_dir = 1
        self.title_glow.setBlurRadius(blur)

    def _updateTelemetry(self):
        elapsed = self.start_time.secsTo(QDateTime.currentDateTime())
        h, rem = divmod(elapsed, 3600)
        m, s = divmod(rem, 60)
        self.telemetry_label.setText(
            f"NEURAL LINK: STABLE   |   SIGNAL: STRONG   |   UPTIME {h:02d}:{m:02d}:{s:02d}"
        )

    # define the speech-recog part for the initial screen
    def SpeechRecogText(self):
        with open(TempDirectoryPath('Status.data'), "r", encoding="utf-8") as f:
            text = f.read()
            self.label.setText(text)
            s = text.lower()
            if "listen" in s:
                color = Theme.CYAN
            elif "think" in s or "search" in s:
                color = Theme.AMBER
            elif "answer" in s:
                color = Theme.VIOLET
            elif "available" in s:
                color = Theme.GREEN
            else:
                color = Theme.TEXT_DIM
            self.label.setStyleSheet(f"color:{color}; font-size:15px; font-weight:500; background: transparent;")

    def Load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):

        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('mic_on.png'), 60, 60)
            MicButtonInitialed()

        else:
            self.load_icon(GraphicsDirectoryPath('mic_off.png'), 60, 60)
            MicbuttonClosed()
        self.toggled = not self.toggled


class MessageScreen(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QLabel("NEXUS AI  ·  LIVE SESSION")
        header.setAlignment(Qt.AlignCenter)
        header.setFixedHeight(46)
        header.setStyleSheet(f"""
            color: {Theme.CYAN};
            font-size: 14px;
            font-weight: 700;
            background-color: {Theme.PANEL};
            border-bottom: 1px solid {Theme.PANEL_EDGE};
        """)
        layout.addWidget(header)

        chat_section = ChatSection()
        layout.addWidget(chat_section)

        self.setLayout(layout)
        self.setStyleSheet(f"background-color: {Theme.BG};")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)


class CustomTopBar(QWidget):
    def __init__(self, parent, stakced_widget):
        super().__init__(parent)
        self.stacked_widget = stakced_widget
        self.initUI()
        self.current_screen = None

    def initUI(self):
        self.setFixedHeight(52)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 6, 12, 6)
        layout.setSpacing(10)

        title_label = QLabel("NEXUS AI")
        title_label.setStyleSheet(f"""
            color: {Theme.CYAN};
            font-size: 17px;
            font-weight: 800;
            background: transparent;
        """)

        status_dot = QLabel("●")
        status_dot.setStyleSheet(f"color: {Theme.GREEN}; font-size: 12px; background: transparent;")

        self.nav_style_inactive = f"""
            QPushButton {{
                color: {Theme.TEXT_DIM};
                background-color: rgba(0, 200, 255, 10);
                border: 1px solid rgba(0, 220, 255, 25);
                border-radius: 10px;
                padding: 7px 18px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                color: {Theme.TEXT};
                background-color: rgba(0, 220, 255, 30);
                border: 1px solid {Theme.CYAN};
            }}
        """

        self.nav_style_active = f"""
            QPushButton {{
                color: {Theme.BG};
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00e5ff, stop:1 #00b3d9
                );
                border: 1px solid {Theme.CYAN};
                border-radius: 10px;
                padding: 7px 18px;
                font-size: 13px;
                font-weight: 800;
            }}
        """

        self.home_button = QPushButton()
        home_icon = QIcon(getGraphicsPath("home.png"))
        self.home_button.setIconSize(QSize(18, 18))
        self.home_button.setIcon(home_icon)
        self.home_button.setText(" Home")
        self.home_button.setCursor(Qt.PointingHandCursor)

        self.message_button = QPushButton()
        message_icon = QIcon(getGraphicsPath("chat.png"))
        self.message_button.setIconSize(QSize(18, 18))
        self.message_button.setIcon(message_icon)
        self.message_button.setText(" Chat")
        self.message_button.setCursor(Qt.PointingHandCursor)

        home_button = self.home_button
        message_button = self.message_button
        self._updateActiveTab(0)

        window_btn_style = f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 6px 10px;
            }}
            QPushButton:hover {{
                background-color: rgba(0, 220, 255, 35);
            }}
        """

        minimize_button = QPushButton()
        minimize_icon = QIcon(getGraphicsPath('minimize-(1).png'))
        minimize_button.setIcon(minimize_icon)
        minimize_button.setStyleSheet(window_btn_style)
        minimize_button.clicked.connect(self.minimizeWindow)

        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(getGraphicsPath("maximize.png"))
        self.restore_icon = QIcon(getGraphicsPath("minimize-remove.png"))
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet(window_btn_style)
        self.maximize_button.clicked.connect(self.maximizeWindow)

        close_button = QPushButton()
        close_icon = QIcon(getGraphicsPath('close.png'))
        close_button.setIcon(close_icon)
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 6px;
                padding: 6px 10px;
            }}
            QPushButton:hover {{
                background-color: {Theme.DANGER};
            }}
        """)
        close_button.clicked.connect(self.closeWindow)

        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.stacked_widget.currentChanged.connect(self._updateActiveTab)

        layout.addWidget(status_dot)
        layout.addWidget(title_label)
        layout.addSpacing(20)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)

        self.draggable = True
        self.offset = None

        self.setStyleSheet(f"""
            CustomTopBar {{
                background-color: {Theme.PANEL};
                border-bottom: 1px solid {Theme.PANEL_EDGE};
            }}
        """)

        # ---------------- SHIMMER SWEEP ----------------
        self._shimmer_pos = 0
        self.shimmer_timer = QTimer(self)
        self.shimmer_timer.timeout.connect(self._advanceShimmer)
        self.shimmer_timer.start(16)

    def _advanceShimmer(self):
        self._shimmer_pos += 3
        if self._shimmer_pos > self.width() + 200:
            self._shimmer_pos = -200
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(Theme.PANEL))
        painter.setPen(QPen(QColor(Theme.CYAN), 2))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)

        # bright shimmer segment sweeping left -> right
        gradient = QLinearGradient(self._shimmer_pos - 100, 0, self._shimmer_pos + 100, 0)
        gradient.setColorAt(0.0, QColor(0, 229, 255, 0))
        gradient.setColorAt(0.5, QColor(0, 229, 255, 220))
        gradient.setColorAt(1.0, QColor(0, 229, 255, 0))
        painter.setPen(QPen(QBrush(gradient), 3))
        painter.drawLine(0, self.height() - 1, self.width(), self.height() - 1)

        super().paintEvent(event)

    def _updateActiveTab(self, index):
        self.home_button.setStyleSheet(
            self.nav_style_active if index == 0 else self.nav_style_inactive
        )
        self.message_button.setStyleSheet(
            self.nav_style_active if index == 1 else self.nav_style_inactive
        )

    def minimizeWindow(self):
        self.parent().showMinimized()

    def maximizeWindow(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
            self.maximize_button.setIcon(self.maximize_icon)
        else:
            self.parent().showMaximized()
            self.maximize_button.setIcon(self.restore_icon)

    def closeWindow(self):
        self.parent().close()

    def mousePressEvent(self, event):
        if self.draggable:
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalPos() - self.offset
            self.parent().move(new_pos)

    def showMessageScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()

        message_screen = MessageScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(message_screen)
        self.current_screen = message_screen

    def showInitialScreen(self):
        if self.current_screen is not None:
            self.current_screen.hide()

        initial_screen = InitialScreen(self)
        layout = self.parent().layout()
        if layout is not None:
            layout.addWidget(initial_screen)
        self.current_screen = initial_screen


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NEXUS AI")
        self.initUI()

    def toggleMic(self):
        if self.mic_btn.isChecked():
            self.mic_btn.setText("● MIC ON")
            SetMicrophoneStatus("True")
            SetAssistantStatus("Available")
        else:
            self.mic_btn.setText("○ MIC OFF")
            SetMicrophoneStatus("False")
            SetAssistantStatus("Mic muted")

    def _breatheMicGlow(self):
        # Gentle pulsing glow while the mic is live; calmer/dimmer when muted.
        target_max = 55 if self.mic_btn.isChecked() else 20
        target_min = 25 if self.mic_btn.isChecked() else 10
        blur = self.mic_glow.blurRadius()
        blur += self._mic_glow_dir * 0.8
        if blur > target_max:
            self._mic_glow_dir = -1
        elif blur < target_min:
            self._mic_glow_dir = 1
        self.mic_glow.setBlurRadius(blur)

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        message_screen = MessageScreen()

        stacked_widget.addWidget(initial_screen)
        stacked_widget.addWidget(message_screen)

        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet(f"background-color: {Theme.BG};")

        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)

        # ---------- MIC BUTTON ----------
        self.mic_btn = QPushButton("● MIC ON")
        self.mic_btn.setCheckable(True)
        self.mic_btn.setChecked(True)
        self.mic_btn.setCursor(Qt.PointingHandCursor)
        self.mic_btn.setFixedHeight(48)
        self.mic_btn.setMinimumWidth(190)
        self.mic_btn.setStyleSheet(f"""
            QPushButton {{
                color: {Theme.BG};
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00e5ff, stop:1 #00b3d9
                );
                border: none;
                border-radius: 24px;
                padding: 10px 36px;
                font-size: 14px;
                font-weight: 800;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4df3ff, stop:1 #00c9f0
                );
            }}
            QPushButton:pressed {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00b3d9, stop:1 #008cad
                );
            }}
            QPushButton:!checked {{
                color: {Theme.CYAN};
                background: rgba(0, 30, 45, 220);
                border: 2px solid {Theme.CYAN_DIM};
            }}
            QPushButton:!checked:hover {{
                border: 2px solid {Theme.CYAN};
                background: rgba(0, 45, 65, 230);
            }}
        """)
        mic_glow = QGraphicsDropShadowEffect(self.mic_btn)
        mic_glow.setBlurRadius(35)
        mic_glow.setColor(QColor(Theme.CYAN))
        mic_glow.setOffset(0, 0)
        self.mic_btn.setGraphicsEffect(mic_glow)
        self.mic_glow = mic_glow

        self._mic_glow_dir = 1
        self.mic_glow_timer = QTimer(self)
        self.mic_glow_timer.timeout.connect(self._breatheMicGlow)
        self.mic_glow_timer.start(40)

        self.mic_btn.clicked.connect(self.toggleMic)
        mic_layout = QHBoxLayout()
        mic_layout.setContentsMargins(0, 14, 0, 18)
        mic_layout.addStretch()
        mic_layout.addWidget(self.mic_btn)
        mic_layout.addStretch()

        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        central_layout.addWidget(stacked_widget)
        central_layout.addLayout(mic_layout)

        container = QWidget()
        container.setStyleSheet(f"background-color: {Theme.BG};")
        container.setLayout(central_layout)
        self.setCentralWidget(container)


def GraphicalUserInterface():
    window = MainWindow()
    window.show()
    return window


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    try:
        window = GraphicalUserInterface()
        sys.exit(app.exec_())
    except Exception as e:
        print("🔥 CRASH ERROR 🔥")
        print(e)
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")