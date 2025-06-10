#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
统一启动脚本
自动设置环境变量并启动应用
"""

import os
import sys
import argparse

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="启动Celebrity应用")
    parser.add_argument("--mode", choices=["dev", "prod"], default="prod",
                        help="运行模式: dev=开发模式, prod=生产模式(默认)")
    parser.add_argument("--port", type=int, default=5000,
                        help="服务器端口号(默认: 5000)")
    parser.add_argument("--host", default="0.0.0.0",
                        help="服务器监听地址(默认: 0.0.0.0)")
    parser.add_argument("--root", default="/celeb",
                        help="应用根目录路径(默认: /celeb)")
    args = parser.parse_args()
    
    # 设置环境变量
    os.environ['SCRIPT_NAME'] = args.root
    os.environ['PYTHONPATH'] = project_root
    print(f"设置环境变量SCRIPT_NAME={os.environ['SCRIPT_NAME']}")
    
    # 根据模式启动应用
    if args.mode == "dev":
        # 开发模式
        config_mode = "development"
        debug = True
        print(f"以开发模式启动应用，使用Flask内置服务器")
    else:
        # 生产模式
        config_mode = "production"
        debug = False
        print(f"以生产模式启动应用，使用Waitress WSGI服务器")
    
    # 通用访问地址提示
    print(f"访问地址: http://localhost:{args.port}{args.root}/")
    
    # 导入应用
    try:
        from trans_web.core.app import create_app
        app = create_app(config_mode)
        
        # 启动服务器
        if args.mode == "dev":
            # 开发模式：使用Flask内置服务器
            app.run(host=args.host, port=args.port, debug=debug)
        else:
            # 生产模式：使用Waitress服务器
            try:
                from waitress import serve
                print(f"Waitress服务器已启动，监听 {args.host}:{args.port}")
                serve(app, host=args.host, port=args.port, threads=8)
            except ImportError:
                print("错误: 未安装waitress库，请执行: pip install waitress")
                sys.exit(1)
            except Exception as e:
                print(f"错误: 启动服务器失败 - {str(e)}")
                sys.exit(1)
    except ImportError as e:
        print(f"错误: 导入应用失败 - {str(e)}")
        print("请确保您在正确的目录中运行此脚本，并且已安装所有依赖项")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 启动应用失败 - {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 