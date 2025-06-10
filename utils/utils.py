"""
工具函数模块
包含用于数据处理、文件操作和日志设置的各种辅助函数
"""

import json
import os
import shutil
import logging
from datetime import datetime
import sys

def load_json(file_path):
    """
    从指定路径加载JSON数据
    
    Args:
        file_path: JSON文件的路径
    
    Returns:
        加载的JSON数据(通常是一个列表或字典)
    """
    if not os.path.exists(file_path):
        return []
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"加载JSON文件失败: {str(e)}")
        return []

def save_json(data, file_path):
    """
    将数据保存为JSON文件
    
    Args:
        data: 要保存的数据
        file_path: 保存的文件路径
    
    Returns:
        bool: 保存是否成功
    """
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"保存JSON文件失败: {str(e)}")
        return False

def backup_main_db(source_file, backup_dir):
    """
    备份主数据库文件
    
    Args:
        source_file: 源文件路径
        backup_dir: 备份目录路径
    
    Returns:
        str: 备份文件路径或失败信息
    """
    if not os.path.exists(source_file):
        return f"源文件不存在: {source_file}"
    
    os.makedirs(backup_dir, exist_ok=True)
    
    # 使用时间戳创建备份文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"backup_{timestamp}.json")
    
    try:
        shutil.copy2(source_file, backup_file)
        return backup_file
    except Exception as e:
        return f"备份失败: {str(e)}"

def init_json_file(file_path):
    """
    初始化JSON文件，如果文件不存在则创建一个空的JSON数组
    
    Args:
        file_path: 要初始化的JSON文件路径
    """
    if not os.path.exists(file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)

def setup_logger(name, log_file, level=logging.INFO):
    """
    设置一个日志记录器
    
    Args:
        name: 记录器名称
        log_file: 日志文件路径
        level: 日志级别
    
    Returns:
        logging.Logger: 配置好的记录器
    """
    # 确保日志目录存在
    log_dir = os.path.dirname(log_file)
    os.makedirs(log_dir, exist_ok=True)
    
    # 创建记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 防止重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger 