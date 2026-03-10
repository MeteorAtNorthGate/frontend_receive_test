from PySide6.QtWidgets import QMainWindow, QTextEdit, QVBoxLayout, QWidget, QLabel
from PySide6.QtGui import QFont
from json_highlighter import JsonHighlighter # 如果在同级目录请注意引用路径

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("JSON Passive Receiver (Test Tool)")
        self.resize(800, 600)

        # UI 布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.info_label = QLabel("Listening on http://localhost:8000/receive")
        layout.addWidget(self.info_label)

        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setFont(QFont("Courier New", 12))
        self.text_display.setPlaceholderText("Waiting for data from frontend...")
        
        # 绑定语法着色器
        self.highlighter = JsonHighlighter(self.text_display.document())
        
        layout.addWidget(self.text_display)

    def update_display(self, text):
        # 刷新界面文本
        self.text_display.setPlainText(text)