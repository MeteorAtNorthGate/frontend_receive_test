# import mimetypes

# # 强制修复 Windows 注册表中的 .js MIME 类型错误
# mimetypes.add_type('application/javascript', '.js')
# mimetypes.add_type('text/css', '.css')

import sys
import threading
import argparse
from PySide6.QtWidgets import QApplication
from gui_window import MainWindow
from api_server import run_server, signals

if __name__ == "__main__":
    # --- 参数解析逻辑 ---
    parser = argparse.ArgumentParser(description="启动 PyQt 客户端与 FastAPI 服务端")
    # 添加 --host 和 --port 参数，并设置默认值
    parser.add_argument("--host", type=str, default="localhost", help="绑定的 Host 地址")
    parser.add_argument("--port", type=int, default=8000, help="绑定的端口号")
    
    # 使用 parse_known_args 避免与 PyQt 自带的命令行参数冲突
    args, unknown_args = parser.parse_known_args()
    host = args.host
    port = args.port
    # ------------------

    # 将脚本名和剩余未识别的参数传给 QApplication
    qt_args = [sys.argv[0]] + unknown_args
    app = QApplication(qt_args)

    # 1. 创建界面并传入端口号
    window = MainWindow(host=host, port=port)
    
    # 2. 连接信号
    signals.data_received.connect(window.update_display)

    # 3. 在子线程中启动 FastAPI，通过 args 将 host 和 port 一起传给 run_server
    server_thread = threading.Thread(target=run_server, args=(host, port), daemon=True)
    server_thread.start()

    window.show()
    sys.exit(app.exec())