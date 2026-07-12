from pydoc import text
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout , QPushButton , QFrame , QLabel , QSizePolicy
from PyQt5.QtGui import (
    QIcon,
    QPainter,
    QMovie,
    QColor,
    QTextCharFormat,
    QFont,
    QPixmap,
    QTextBlockFormat,
    QPen
)

from PyQt5.QtCore import Qt, QSize, QTimer, QPointF
from dotenv import dotenv_values
import sys
import os 


#load the important .env and more vairables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname")
current_dir = os.getcwd()
old_chat_message = ""
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TempDirPath = os.path.join(BASE_DIR, "Data")
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"

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

     # ===== SAFE FUTURISTIC BACKGROUND (NO GRADIENT WARNING) =====
     p.setPen(Qt.NoPen)

     # soft cyan halo background
     p.setBrush(QColor(0, 120, 180, 60))
     p.drawEllipse(center, 210, 210)

     # darker depth layer
     p.setBrush(QColor(0, 0, 0, 120))
     p.drawEllipse(center, 190, 190)

    # ===== HUD CIRCULAR GRID =====
     p.setPen(QPen(QColor(0, 200, 255, 35), 1))
     for r in range(140, 230, 20):
        p.drawEllipse(center, r, r)

    # ===== OUTER SOFT GLOW =====
     p.setPen(Qt.NoPen)
     p.setBrush(QColor(0, 200, 255, 40))
     p.drawEllipse(center, 95, 95)

    # ===== MID GLOW =====
     p.setBrush(QColor(0, 200, 255, 90))
     p.drawEllipse(center, 70, 70)

    # ===== CORE ENERGY (UNCHANGED – DON'T TOUCH) =====
     core_radius = 35 + self.pulse
     p.setBrush(QColor(0, 220, 255))
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

    # ===== MICRO FAST RING =====
     p.save()
     p.translate(center)
     p.rotate(self.micro_angle)
     pen = QPen(QColor(0, 255, 255, 200), 2)
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

     p.setPen(QPen(QColor(0, 255, 255, 180), 6))
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



def getGraphicsPath(filename):
    return rf"{GraphicsDirPath}\{filename}"

def AnswerModifire(Answer):
     lines = Answer.split('\n')
     non_empty_lines = [line for line in lines if line.strip()]
     modified_answer = '\n'.join(non_empty_lines)
     return modified_answer


# function for the user input 
def QueryModifier(Query):
    
        new_query = Query.lower().strip() # it will remove the extra spae and ad losercase form the user input 
        query_words = new_query.split() #its break the sntence in words list
        question_words = ["how" , "what" ,"who" , "where" , "when" , "why" , "which" , "whose" , "whom" ," can you" , "what's" , "where's", "how's",]
       
       
        if any(word + " " in new_query for word in question_words): # its will check is there any question word is present in sentence
            if query_words[-1][-1] in ['.', '?' ,'!']:  #if there is queestion word is present so it is end with these signs or not 
                   new_query = new_query[:-1] + "?" 
            else:
                   new_query  += "?" # its will rmove the last pucation and repalace woth ?
        
        else:
             if query_words[-1][-1] in ['.' , '?' , '!']:
                 new_query = new_query[:-1] + "."
             else:
                  new_query += "."
                  
        return new_query.capitalize()
 
                
#----------------define the function one by one ---------------
         
         
            
def SetMicrophoneStatus(Command):
     with open(rf'{TempDirPath}\MIC.data', "w" , encoding='utf-8') as file:
        file.write(Command)
        
def GetMicrophoneStatus():
     with open(rf'{TempDirPath}\MIC.data' , "r" , encoding='utf-8') as file:
           Status = file.read()
     return Status
 
 
def SetAssistantStatus(text):
    with open(rf'{TempDirPath}\Status.data', "w", encoding='utf-8') as file:
        file.write(text)


def GetAssistantStatus():
    with open(rf'{TempDirPath}\Status.data' , "r", encoding='utf-8') as file:
        Status = file.read()
    return Status


def MicButtonInitialed():
     SetMicrophoneStatus("True")


def MicbuttonClosed():
     SetMicrophoneStatus("False")
     
     
def GraphicsDirectoryPath(Filename):
    Path = rf'{GraphicsDirPath}\{Filename}'
    return Path 
    

def TempDirectoryPath(Filename):
     Path = rf'{TempDirPath}\{Filename}'
     return Path       


def ShowTextToScreen(Text):
    with open(rf'{TempDirPath}\Response.data', "w", encoding="utf-8") as file:
        file.write(Text)
        
    
class ChatSection(QWidget):

    def __init__(self):
        super(ChatSection, self).__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(100)

        # ---------------- CHAT TEXT ----------------
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        self.chat_text_edit.setFont(QFont("", 13))
        layout.addWidget(self.chat_text_edit)

        text_format = QTextCharFormat()
        text_format.setForeground(QColor(Qt.blue))
        self.chat_text_edit.setCurrentCharFormat(text_format)

        # ---------------- GIF ----------------
        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")

        movie = QMovie(getGraphicsPath("Jarvis.gif"))
        movie.setScaledSize(QSize(480, 270))
        self.gif_label.setMovie(movie)
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        movie.start()

        layout.addWidget(self.gif_label)

        # ---------------- STATUS LABEL ----------------
        self.label = QLabel("")
        self.label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                margin-right: 195px;
                border: none;
            }
        """)
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)

        # ---------------- TIMER ----------------
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(200)

        # ---------------- STYLE ----------------
        self.setStyleSheet("""
CustomTopBar {
    background-color: rgba(15, 15, 15, 200);
    border-bottom: 1px solid rgba(255, 255, 255, 40);
}

QPushButton {
    background-color: transparent;
    border: none;
    padding: 6px 12px;
}

QPushButton:hover {
    background-color: rgba(255, 255, 255, 30);
    border-radius: 6px;
}

QLabel {
    color: white;
    font-size: 18px;
    font-weight: bold;
}
""")
   
    def loadMessages(self):
          global old_chat_message
          
          path = TempDirectoryPath('RESPONSES.DATA')
          if not os.path.exists(path):
              
              print("Response file not found" , path )
              return
          
          with open(path , "r" , encoding = ' utf-8') as file:
              messages = file.read().strip()
              
          #print("READ THE MESSAGE:" , messages)
              
          if not messages:
              return
          
          if messages == old_chat_message:
              return
          
          self.addMessage(messages, color='white')
          old_chat_message = messages    
  
  
  
    def SpeechRecogText(self):   
         if os.path.exists(TempDirectoryPath("Status.data")):                          
          with open(TempDirectoryPath('Status.data'), "r" ,encoding='utf-8') as file:
             messages= file.read()
             self.label.setText(messages)
             
    def load_icon(self , path , width=60, height=60):
         pixmap = QPixmap(path)
         new_pixmap = pixmap.scaled(width, height)   
         self.icon_label.setPixmap(new_pixmap)
         
    def toggel_icon(self, event=None):
         pass
         if self.toggled:
             self.load_icon(GraphicsDirectoryPath('voice.png'), 60,60)
             MicButtonInitialed()
         else:
             self.load_icon(GraphicsDirectoryPath('mic.png'), 60, 60)
             MicbuttonClosed()
         self.toggled = not self.toggled
         
    def addMessage(self , message, color):
         cursor = self.chat_text_edit.textCursor()
         format = QTextCharFormat()
         formatm = QTextBlockFormat()
         formatm.setTopMargin(10)
         formatm.setLeftMargin(10)
         format.setForeground(QColor(color))       
         cursor.setCharFormat(format)
         cursor.setBlockFormat(formatm)
         cursor.insertText(message + "\n")
         self.chat_text_edit.setTextCursor(cursor)  


#in this section here we initlilize the all component jo humne upload kiye  aha 

class InitialScreen(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()      
        screen = QApplication.primaryScreen().size()
        screen_width = screen.width()
        screen_height = screen.height()

        layout = QVBoxLayout(self)

        self.gif_label = QLabel()
        movie = QMovie(getGraphicsPath("Jarvis.gif"))
        movie.setScaledSize(QSize(screen_width, int(screen_width * 9 / 16)))
        self.gif_label.setMovie(movie)
        self.gif_label.setAlignment(Qt.AlignCenter)
        movie.start()
        self.label = QLabel("")
        self.label.setStyleSheet("color:white; font-size:16px;")
        self.label.setAlignment(Qt.AlignCenter)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(150,150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.arc = ArcReactor()
        layout.addStretch()
        layout.addWidget(self.arc, alignment=Qt.AlignCenter)
        layout.addWidget(self.label)
        layout.addStretch()
        layout.setContentsMargins(0,0,0,150)
        self.setLayout(layout)
        self.setFixedSize(screen_width, screen_height)
        self.setStyleSheet("background-color: black;")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecogText)
        self.timer.start(300)
        self.toggled = False

       
    #define the speechrecog part by the initila screen   
    def SpeechRecogText(self):
           with open(TempDirectoryPath('Status.data'), "r", encoding="utf-8") as f:
                self.label.setText(f.read())
                self.label.setStyleSheet("color:white; font-size:16px;")
                
                
     
    def Load_icon(self , path , width=60, height=60 ):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width,height)
        self.icon_label.setPixmap(new_pixmap)
        
    def toggle_icon(self , event=None):
        
        
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('mic_on.png'), 60 , 60) 
            MicButtonInitialed()
            
        else:
            self.load_icon(GraphicsDirectoryPath('mic_off.png'), 60 ,60)
            MicbuttonClosed()
        self.toggled = not self.toggled


class MessageScreen(QWidget):
    
    def __init__(self , parent=None):
        super().__init__(parent)

        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        layout = QVBoxLayout()

        label = QLabel("")
        layout.addWidget(label)

        chat_section = ChatSection()
        layout.addWidget(chat_section)

        self.setLayout(layout)
        self.setStyleSheet("background-color:  #050b12;")
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        label = QLabel("Start chatting with Nexus AI 🚀")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
        color: #888;
        font-size: 22px;   
            """)
        layout.addWidget(label)

 

class CustomTopBar(QWidget):  
    def __init__(self, parent ,stakced_widget):
        super(). __init__(parent)
        self.initUI()
        self.current_screen = None
        self.stacked_widget = stakced_widget
        
    def initUI(self):
        self.setFixedHeight(50)
        layout = QHBoxLayout(self)
        layout.setAlignment(Qt.AlignRight)
        home_button = QPushButton()
        home_icon = QIcon(getGraphicsPath("home.png"))
        home_button.setIconSize(QSize(20,20))
        home_button.setIcon(home_icon)
        home_button.setText(" home ")
        home_button.setStyleSheet("""QPushButton {height : 40px; line-height: 40px; background-color: white; border: none; } """)
        message_button = QPushButton()
        message_icon = QIcon(getGraphicsPath("chat.png"))
        message_button.setIconSize(QSize(20,20))
        message_button.setIcon(message_icon)
        message_button.setText(" chat")
        message_button.setStyleSheet("height:40px; line-height:40px; background-color: white; border: none;")
        minimize_button = QPushButton()
        minimize_icon = QIcon(getGraphicsPath('minimize-(1).png'))
        minimize_button.clicked.connect(self.minimizeWindow)
        self.maximize_button = QPushButton()
        self.maximize_icon = QIcon(getGraphicsPath("maximize.png"))
        self.restore_icon = QIcon(getGraphicsPath("minimize-remove.png"))

        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFlat(True)
        self.maximize_button.setStyleSheet("background-color:white")
        self.maximize_button.clicked.connect(self.maximizeWindow)
        close_button = QPushButton()
        close_icon = QIcon(getGraphicsPath('close.png'))
        close_button = QPushButton()
        close_button.setIcon(close_icon)
        close_button.setStyleSheet("background-color:white")
        close_button.clicked.connect(self.closeWindow)
        line_frame = QFrame()
        line_frame.setFixedHeight(1)
        line_frame.setFrameShape(QFrame.HLine)
        line_frame.setFrameShadow(QFrame.Raised)
        title_label = QLabel("NEXUS AI")
        title_label.setStyleSheet("color : black ; font-size : 18px ; background-color:white")
        home_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        message_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(message_button)
        layout.addStretch(1)
        layout.addWidget(minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(close_button)
        layout.addWidget(line_frame)
        self.draggable = True
        self.offset = None
        
        
    def paintEvent(self , event):
        painter = QPainter(self)
        painter.fillRect(self.rect() , Qt.white)
        super().paintEvent(event)
        
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
        self.mic_btn.setText("MIC ON")
        SetMicrophoneStatus("True")
        SetAssistantStatus("Available")
     else:
        self.mic_btn.setText("MIC OFF")
        SetMicrophoneStatus("False")
        SetAssistantStatus("Mic muted")

                
                
                
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
        self.setStyleSheet("background-color: black;")

        top_bar = CustomTopBar(self, stacked_widget)
        self.setMenuWidget(top_bar)
        self.setCentralWidget(stacked_widget)
        
        # ---------- MIC BUTTON (CREATE FIRST) ----------
        self.mic_btn = QPushButton("MIC ON")
        self.mic_btn.setCheckable(True)
        self.mic_btn.setChecked(True)
        self.mic_btn.setStyleSheet("""
QPushButton {
    color: white;
    background: #001d2b;
    border: 2px solid #00aaff;
    padding: 10px 30px;
    font-size: 14px;
}
QPushButton:checked {
    background: #002f4f;
}
""")

        self.mic_btn.clicked.connect(self.toggleMic)
        mic_layout = QHBoxLayout()
        mic_layout.addStretch()
        mic_layout.addWidget(self.mic_btn)
        mic_layout.addStretch()

        central_layout = QVBoxLayout()
        central_layout.addWidget(stacked_widget)
        central_layout.addLayout(mic_layout)

        container = QWidget()
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