from PySide6.QtWidgets import QMainWindow, QTextEdit, QVBoxLayout, QWidget, QLabel
from PySide6.QtGui import QFont
from json_highlighter import JsonHighlighter

class MainWindow(QMainWindow):
    # 接收 port 参数
    def __init__(self, port: int = 8000):
        super().__init__()
        self.setWindowTitle("JSON Passive Receiver (Test Tool)")
        self.resize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 根据传入的 port 更新显示文本
        self.info_label = QLabel(f"Listening on http://localhost:{port}/receive")
        layout.addWidget(self.info_label)

        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setFont(QFont("Courier New", 12))
        self.text_display.setPlaceholderText("Waiting for data from frontend...")
        
        self.highlighter = JsonHighlighter(self.text_display.document())
        layout.addWidget(self.text_display)

    def update_display(self, text):
        self.text_display.setPlainText(text)