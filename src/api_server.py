from fastapi import FastAPI, Body
from PySide6.QtCore import QObject, Signal
import uvicorn
import json
from typing import Any 

class ApiSignals(QObject):
    data_received = Signal(str)

app = FastAPI()
signals = ApiSignals()

@app.post("/receive")
async def receive_data(payload: Any = Body(...)):
    formatted_json = json.dumps(payload, indent=4, ensure_ascii=False)
    signals.data_received.emit(formatted_json)
    return {"status": "success", "received": payload}

# 添加 port 参数，默认为 8000
def run_server(port: int = 8000):
    try:
        # 将 port 传递给 uvicorn
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        print(f"Server Error: {e}")