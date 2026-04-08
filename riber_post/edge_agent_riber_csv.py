import os
import time
import json
import requests
import datetime
from collections import deque
import sys
import glob
from pathlib import Path

from data_tools import setup_logger, LoggerMixin

class EdgeAgentRiberCSV(LoggerMixin):
    def __init__(self, config_path: str = "riber_csv_agent_config.json"):
        setup_logger() # 初始化日志系统
        self.config_path = config_path
        
        # 默认配置（如果没有配置文件将自动创建）
        self.config = {
            "BACKEND_URL": "http://192.168.211.9:8001/api/v1/auto_check",
            "DEVICE_ID": "Riber_Machine_02",
            "INSPECT_INTERVAL_SECONDS": 60,
            "CSV_DIRECTORY": "./",  # 指向 CSV 所在的目录
        }
        
        self._load_or_create_config()
        
        self.backend_url = self.config["BACKEND_URL"]
        self.device_id = self.config["DEVICE_ID"]
        self.interval = self.config["INSPECT_INTERVAL_SECONDS"]
        self.csv_dir = Path(self.config["CSV_DIRECTORY"])
        
        self.data_buffer = deque(maxlen=1000)

        self.logger.info("="*50)
        self.logger.info("Riber CSV Edge Agent 启动配置:")
        self.logger.info(f" -> 设备 ID: {self.device_id}")
        self.logger.info(f" -> 后端地址: {self.backend_url}")
        self.logger.info(f" -> 采集间隔: {self.interval} 秒")
        self.logger.info(f" -> CSV 目录: {self.csv_dir.resolve()}")
        self.logger.info("="*50)

    def _load_or_create_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
                self.config.update(loaded)
        else:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
                
    def _get_latest_file(self, suffix: str) -> Path:
        """获取目录下指定后缀的最新的文件"""
        search_pattern = self.csv_dir / f"*{suffix}"
        files = glob.glob(str(search_pattern))
        if not files:
            return None
        # 按照文件修改时间排序找最新
        return Path(max(files, key=os.path.getmtime))

    def _read_latest_data(self, filepath: Path) -> dict:
        """高效读取大文件的表头和最后一行有效数据"""
        if not filepath or not filepath.exists():
            return {}
            
        try:
            # 1. 读取表头 (第一行)
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                header_line = f.readline().strip()
                headers = header_line.split(',')

            # 2. 从尾部读取最后一行 (倒序扫描避免加载整个文件)
            with open(filepath, 'rb') as f:
                f.seek(0, 2)
                file_size = f.tell()
                # 往回多读一点，比如 4096 字节，足够包含多行长数据了
                buffer_size = min(4096, file_size)
                f.seek(file_size - buffer_size)
                
                # 读取最后一块字节并按行分割
                chunk = f.read().decode('utf-8', errors='replace')
                lines = chunk.splitlines()
                
                last_valid_line = None
                # 从后往前找有效行（过滤掉类似 ",,,,,,,," 的占位空行）
                for line in reversed(lines):
                    line = line.strip()
                    if line and line.replace(',', '').strip():
                        last_valid_line = line
                        break
                        
            if not last_valid_line:
                return {}
                
            values = last_valid_line.split(',')
            
            # 将 header 和 values 打包成字典，长度不对齐的丢弃或补空
            data_dict = {}
            for i, h in enumerate(headers):
                if h:  # 忽略空表头
                    val = values[i] if i < len(values) else ""
                    
                    # 按点号分割成层级结构
                    parts = h.split('.')
                    current_level = data_dict
                    for part in parts[:-1]:
                        if part not in current_level:
                            current_level[part] = {}
                        current_level = current_level[part]
                    current_level[parts[-1]] = val
            return data_dict

        except PermissionError:
            self.logger.warning(f"读取被拒绝，可能是厂商程序正在独占写入: {filepath.name}")
            return {}
        except Exception as e:
            self.logger.error(f"解析 {filepath.name} 失败: {e}")
            return {}

    def run_forever(self):
        while True:
            try:
                # 抓取数据
                prep_file = self._get_latest_file("_Prep.csv")
                growth_file = self._get_latest_file("_Growth.csv")
                
                prep_data = self._read_latest_data(prep_file)
                growth_data = self._read_latest_data(growth_file)
                
                # 合并数据
                combined_data = {}
                if prep_data:
                    combined_data["Prep"] = prep_data
                if growth_data:
                    combined_data["Growth"] = growth_data

                if not combined_data:
                    self.logger.warning("未能从 CSV 提取到任何有效数据。")
                else:
                    payload = {
                        "device_id": self.device_id,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "data": combined_data
                    }
                    self.data_buffer.append(payload)
                
                self.upload_buffer()

            except Exception as e:
                self.logger.error(f"点检发生异常: {e}", exc_info=True)

            time.sleep(self.interval)

    def upload_buffer(self):
        """向后端上传缓存队列中的数据"""
        while self.data_buffer:
            payload = self.data_buffer[0]
            try:
                response = requests.post(self.backend_url, json=payload, timeout=5.0)
                if response.status_code == 200:
                    self.data_buffer.popleft()
                else:
                    self.logger.warning(f"服务器返回非 200: {response.status_code}")
                    break
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"网络异常，上传失败。暂存队列: {len(self.data_buffer)}。错误: {e}")
                break

    def stop(self):
        self.logger.info("正在关闭 Edge Agent...")

if __name__ == "__main__":
    agent = EdgeAgentRiberCSV()
    try:
        agent.run_forever()
    except KeyboardInterrupt:
        agent.stop()
        print("Edge Agent 已手动停止。")
