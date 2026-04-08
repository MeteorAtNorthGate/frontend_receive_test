import logging
import logging.handlers
import re  # <--- 新增
from pathlib import Path
from typing import Dict, Any, Optional, Union

def transform_ocr_data(flat_ocr_data: Dict[str, str]) -> Dict[str, Any]:
	"""
	将扁平的OCR结果字典转换为嵌套字典。
	返回的字典总是以 'vacuum_and_cryo' 作为根键。
	示例:
	Input: {'GM1_vacuum': '1.25e-11'}
	Output: {'vacuum_and_cryo': {'GM1': {'vacuum': '1.25e-11'}}}
	"""

	# 初始化嵌套结构
	nested_structure = {}

	# 遍历扁平的OCR数据
	for combined_key, value in flat_ocr_data.items():

		parts = combined_key.split('_')

		if len(parts) != 2:
			print(f"警告：跳过无效的OCR键 '{combined_key}'。预期格式为 'Device_Parameter'。")
			continue

		device_name = parts[0]  # 'GM1'
		metric_name = parts[1]  # 'vacuum'

		# 确保第二层字典 (Device) 存在
		if device_name not in nested_structure:
			nested_structure[device_name] = {}

		# 赋值
		nested_structure[device_name][metric_name] = value

	# 将转换后的结构放入顶层键
	return {'vacuum_and_cryo': nested_structure}


def parse_numeric_value(value_str: Union[str, float, int]) -> Optional[float]:
	"""
	从可能包含单位的字符串中解析出浮点数。
	支持: "123.45", "1.23E-5", "10.5K", "3.49E-10T", "1.5 MPa"
	如果无法解析，返回 None。
	"""
	if value_str is None:
		return None

	# 如果已经是数字，直接返回
	if isinstance(value_str, (int, float)):
		return float(value_str)

	# 使用正则提取符合浮点数格式的子串
	# 格式说明：
	# [-+]?             可选的正负号
	# (?: ... )         非捕获组
	# \d+(?:\.\d*)?     整数或小数 (例如 123, 123.45, 123.)
	# |\.\d+            或者是 .45 这种形式
	# (?:[eE][-+]?\d+)? 可选的科学计数法指数部分 (例如 E-10)
	match = re.search(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?", str(value_str))

	if match:
		try:
			return float(match.group())
		except ValueError:
			return None
	return None

def setup_logger(log_level: int = logging.INFO) -> None:
	"""
	为控制台程序设置一个简单的日志记录器
	"""
	log_dir = Path("logs")
	log_dir.mkdir(exist_ok=True)
	log_file = log_dir / "debug_console.log"

	formatter = logging.Formatter(
		fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S'
	)

	# 配置根日志器
	root_logger = logging.getLogger()
	root_logger.setLevel(log_level)
	root_logger.handlers.clear()

	# 文件处理器
	file_handler = logging.handlers.RotatingFileHandler(
		log_file, maxBytes=5 * 1024 * 1024, backupCount=2, encoding='utf-8'
	)
	file_handler.setFormatter(formatter)
	root_logger.addHandler(file_handler)

	# 控制台处理器
	console_handler = logging.StreamHandler()
	console_handler.setFormatter(formatter)
	root_logger.addHandler(console_handler)

	logging.info("=" * 20 + " Logger Initialized " + "=" * 20)


class LoggerMixin:
	"""
	为其他类提供日志功能的混入类
	"""

	@property
	def logger(self) -> logging.Logger:
		return logging.getLogger(self.__class__.__name__)