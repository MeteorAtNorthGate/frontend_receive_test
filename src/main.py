import sys
import threading
from PySide6.QtWidgets import QApplication
from gui_window import MainWindow
from api_server import run_server, signals

if __name__ == "__main__":
    # --- 参数解析逻辑 ---
    port = 8000  # 默认端口
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Warning: '{sys.argv[1]}' is not a valid port number. Using default 8000.")
    # ------------------

    app = QApplication(sys.argv)

    # 1. 创建界面并传入端口号
    window = MainWindow(port=port)
    
    # 2. 连接信号
    signals.data_received.connect(window.update_display)

    # 3. 在子线程中启动 FastAPI，通过 args 传递端口参数
    server_thread = threading.Thread(target=run_server, args=(port,), daemon=True)
    server_thread.start()

    window.show()
    sys.exit(app.exec())