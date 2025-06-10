#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试导入功能
用于验证项目的关键导入是否正常工作
"""

import os
import sys

# 确保项目根目录在路径中
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

def test_imports():
    """测试关键模块和类的导入"""
    print("开始测试导入...")
    
    success = True
    modules = [
        # 模块: (描述, 导入语句)
        ("核心应用", "from trans_web.core.app import create_app"),
        ("备份调度器", "from trans_web.utils.backup_scheduler import BackupScheduler"),
        ("工具函数", "from trans_web.utils.utils import load_json, save_json"),
        ("配置加载", "from trans_web.config import load_config"),
        ("中间件", "from trans_web.core.middlewares import ReverseProxied"),
        ("启动脚本", "from trans_web.scripts.start import main"),
    ]
    
    for desc, import_stmt in modules:
        try:
            print(f"测试: {desc}...", end="")
            exec(import_stmt)
            print(" ✓ 成功")
        except ImportError as e:
            success = False
            print(f" ✗ 失败: {str(e)}")
            print(f"  导入语句: {import_stmt}")
    
    if success:
        print("\n✓ 所有导入测试通过！项目依赖配置正确。")
    else:
        print("\n✗ 部分导入测试失败。请检查项目结构和PYTHONPATH设置。")
        print("建议：")
        print("1. 确保项目根目录在PYTHONPATH中")
        print("2. 检查对应的模块文件是否存在")
        print("3. 安装所有必要的依赖: pip install flask flask-cors waitress")
    
    return success

if __name__ == "__main__":
    os.environ["PYTHONPATH"] = ROOT_DIR
    test_imports() 