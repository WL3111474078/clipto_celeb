"""
Celebrity数据管理系统
====================

一个用于管理名人数据的Flask应用
"""

__version__ = '1.0.14'
__author__ = '灵感时刻'
__email__ = 'Lingganshike@example.com'

import os
import sys

# 确保当前目录在Python路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir) 