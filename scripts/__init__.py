"""
启动脚本包
包含应用的各种启动脚本和工具
"""

# 在此导入必要的模块，以便可以直接从脚本包中导入
try:
    from trans_web.scripts.start import main
except ImportError:
    # 处理作为内部模块导入的情况
    pass

__all__ = ['main'] 