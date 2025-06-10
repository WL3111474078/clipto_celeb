"""
配置管理模块
支持从多种环境加载配置
"""

import os
import importlib

def load_config(mode='production'):
    """
    根据指定的模式加载配置
    
    参数:
    - mode: 配置模式，可选值 'default', 'development', 'production'
    
    返回:
    - config: 配置对象
    """
    try:
        # 尝试加载指定模式的配置
        module_path = f'trans_web.config.{mode}'
        config = importlib.import_module(module_path)
        print(f"已加载'{mode}'配置")
        return config
    except (ImportError, ModuleNotFoundError):
        # 如果指定模式的配置不存在，回退到默认配置
        try:
            config = importlib.import_module('trans_web.config.default')
            print(f"警告: '{mode}'配置不存在，使用默认配置")
            return config
        except (ImportError, ModuleNotFoundError):
            # 如果默认配置也不存在，返回空的配置对象
            print(f"错误: 未找到任何配置文件")
            return type('EmptyConfig', (), {}) 