#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
应用启动模块，简化版
提供启动应用的函数
"""

import os
import sys

# 获取当前目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)

# 确保项目根目录在路径中
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

def main():
    """启动应用的主函数"""
    # 设置环境变量
    os.environ['SCRIPT_NAME'] = '/celeb'
    os.environ['PYTHONPATH'] = PARENT_DIR
    
    # 打印环境变量，便于调试
    print(f"SCRIPT_NAME={os.environ.get('SCRIPT_NAME')}")
    print(f"PYTHONPATH={os.environ.get('PYTHONPATH')}")
    
    try:
        # 安装缺失的依赖
        try:
            import ijson
        except ImportError:
            print("正在安装缺失的ijson库...")
            import pip
            pip.main(['install', 'ijson'])
            print("ijson库安装完成")
            
        # 尝试导入app并启动
        from core.app import create_app
        app = create_app('production')
        
        # 确保中间件已应用
        from core.middlewares import ReverseProxied
        if not isinstance(app.wsgi_app, ReverseProxied):
            print("应用中间件以处理子目录")
            app.wsgi_app = ReverseProxied(app.wsgi_app)
        
        print("应用实例创建成功")
        print("正在启动Waitress服务器...")
        print(f"应用根目录设置为: {app.config.get('APPLICATION_ROOT')}")
        print(f"环境变量SCRIPT_NAME={os.environ.get('SCRIPT_NAME')}")
        
        from waitress import serve
        print("应用启动于 http://localhost:5000/celeb/")
        serve(app, host='0.0.0.0', port=5000, threads=8)
    except Exception as e:
        print(f"启动应用时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 