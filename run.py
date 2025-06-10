#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Celebrity数据管理应用主入口
"""

import os
import sys

# 确保项目根目录在Python路径中
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# 设置默认环境变量
os.environ['SCRIPT_NAME'] = '/celeb'
os.environ['PYTHONPATH'] = BASE_DIR

# 导入和启动应用
if __name__ == "__main__":
    try:
        from trans_web.scripts.start import main
        main()
    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保您在正确的目录中运行此脚本，并且已安装所有依赖项")
        sys.exit(1)
    except Exception as e:
        print(f"启动应用时出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 