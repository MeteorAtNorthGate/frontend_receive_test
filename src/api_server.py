from fastapi import FastAPI, Body # 导入 Body
from PySide6.QtCore import QObject, Signal
import uvicorn
import json
from typing import Any # 导入 Any 

class ApiSignals(QObject):
    data_received = Signal(str)

app = FastAPI()
signals = ApiSignals()

# 使用 payload: Any = Body(...) 
# 让 FastAPI 在 Swagger UI 里显示 "Request Body" 输入框
@app.post("/receive")
async def receive_data(payload: Any = Body(...)):
    # payload 直接就是解析好的字典或列表，不需要再 await request.json()
    formatted_json = json.dumps(payload, indent=4, ensure_ascii=False)
    
    # 发射信号给 GUI 线程
    signals.data_received.emit(formatted_json)
    
    return {"status": "success", "received": payload}

def run_server():
    # 建议加上 try-except 防止端口占用导致程序直接退出
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except Exception as e:
        print(f"Server Error: {e}")