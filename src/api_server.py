from fastapi import FastAPI, Body
# 1. 导入手动生成文档页面的函数
from fastapi.openapi.docs import get_swagger_ui_html 
from PySide6.QtCore import QObject, Signal
import uvicorn
import json
from typing import Any 

class ApiSignals(QObject):
    data_received = Signal(str)

# 2. 初始化时禁用默认的 docs_url
app = FastAPI(docs_url=None) 
signals = ApiSignals()

# 3. 手动定义一个新的 /docs 路由，使用更稳定的 CDN 资源
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        # 这里换成了 cloudflare 的 CDN，通常比 jsdelivr 更稳定
        swagger_js_url="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.9.0/swagger-ui-bundle.js",
        swagger_css_url="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/5.9.0/swagger-ui.css",
    )

@app.post("/receive")
async def receive_data(payload: Any = Body(...)):
    formatted_json = json.dumps(payload, indent=4, ensure_ascii=False)
    signals.data_received.emit(formatted_json)
    return {"status": "success", "received": payload}

def run_server(port: int = 8000):
    try:
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        print(f"Server Error: {e}")