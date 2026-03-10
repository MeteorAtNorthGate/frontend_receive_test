import sys
import threading
from PySide6.QtWidgets import QApplication
from gui_window import MainWindow
from api_server import run_server, signals

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 1. 创建界面
    window = MainWindow()
    
    # 2. 连接信号：当 API 收到数据时，调用界面的 update_display
    signals.data_received.connect(window.update_display)

    # 3. 在子线程中启动 FastAPI
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    window.show()
    sys.exit(app.exec())