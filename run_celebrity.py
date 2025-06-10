#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Celebrity数据管理应用直接运行脚本
无需配置，直接双击即可运行
"""

import os
import sys
import time

# 获取当前脚本所在目录（trans_web）
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录（trans_web的父目录）
PARENT_DIR = os.path.dirname(CURRENT_DIR)

# 将两个目录都添加到Python路径
for path in [CURRENT_DIR, PARENT_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

# 设置必要的环境变量
os.environ['SCRIPT_NAME'] = '/celeb'
os.environ['PYTHONPATH'] = f"{PARENT_DIR}"

def print_with_delay(message):
    """打印消息并延迟一小段时间"""
    print(message)
    time.sleep(0.1)  # 轻微延迟，让消息有序显示

def main():
    """主函数"""
    print_with_delay("\n" + "="*60)
    print_with_delay("Celebrity数据管理系统启动器")
    print_with_delay("="*60)
    print_with_delay("\n正在启动应用服务器...")
    
    try:
        # 确保安装了必要的依赖
        missing_deps = []
        try:
            import flask
        except ImportError:
            missing_deps.append("flask")
        
        try:
            import flask_cors
        except ImportError:
            missing_deps.append("flask_cors")
        
        try:
            import waitress
        except ImportError:
            missing_deps.append("waitress")
        
        try:
            import ijson
        except ImportError:
            missing_deps.append("ijson")
        
        # 如果有缺失依赖，尝试安装
        if missing_deps:
            print_with_delay(f"\n检测到缺失依赖: {', '.join(missing_deps)}")
            print_with_delay("正在自动安装...")
            
            try:
                import pip
                for dep in missing_deps:
                    print_with_delay(f"安装 {dep}...")
                    pip.main(['install', dep])
                print_with_delay("依赖安装完成!\n")
            except Exception as e:
                print_with_delay(f"安装依赖时出错: {str(e)}")
                print_with_delay("请手动运行: pip install flask flask-cors waitress ijson")
                input("按Enter键退出...")
                return
        
        # 尝试多种导入方式
        import_success = False
        error_messages = []
        
        # 尝试方法1: 使用start.py模块
        try:
            print_with_delay("尝试方法1: 使用脚本模块导入...")
            # 导入本地目录下的start模块
            import start
            print_with_delay("导入成功! 正在启动...")
            start.main()
            import_success = True
        except ImportError as e:
            error_messages.append(f"方法1失败: {str(e)}")
            print_with_delay("方法1失败，尝试其他方法...")
        except Exception as e:
            error_messages.append(f"方法1运行错误: {str(e)}")
            print_with_delay(f"运行方法1时出错: {str(e)}")
        
        # 如果方法1失败，尝试方法2: 通过scripts目录导入
        if not import_success:
            try:
                print_with_delay("尝试方法2: 通过scripts模块导入...")
                from scripts.start import main as scripts_main
                print_with_delay("导入成功! 正在启动...")
                scripts_main()
                import_success = True
            except ImportError as e:
                error_messages.append(f"方法2失败: {str(e)}")
                print_with_delay("方法2失败，尝试其他方法...")
            except Exception as e:
                error_messages.append(f"方法2运行错误: {str(e)}")
                print_with_delay(f"运行方法2时出错: {str(e)}")
        
        # 如果方法2失败，尝试方法3: 直接使用core.app
        if not import_success:
            try:
                print_with_delay("尝试方法3: 直接通过core.app启动...")
                from core.app import create_app
                app = create_app('production')
                
                print_with_delay("成功创建应用实例!")
                print_with_delay("正在启动Waitress服务器...")
                
                from waitress import serve
                print_with_delay("应用启动于 http://localhost:5000/celeb/")
                serve(app, host='0.0.0.0', port=5000, threads=8)
                import_success = True
            except ImportError as e:
                error_messages.append(f"方法3失败: {str(e)}")
                print_with_delay("方法3失败...")
            except Exception as e:
                error_messages.append(f"方法3运行错误: {str(e)}")
                print_with_delay(f"运行方法3时出错: {str(e)}")
        
        # 如果所有方法都失败，显示诊断信息
        if not import_success:
            print_with_delay("\n所有启动方法都失败!")
            print_with_delay("诊断信息:")
            for i, error in enumerate(error_messages, 1):
                print_with_delay(f"  错误 {i}: {error}")
            
            print_with_delay("\n环境信息:")
            print_with_delay(f"  当前目录: {os.getcwd()}")
            print_with_delay(f"  PYTHONPATH: {os.environ.get('PYTHONPATH', '未设置')}")
            print_with_delay(f"  sys.path: {sys.path}")
            
            print_with_delay("\n请确保trans_web目录结构正确，并且已安装所有依赖")
            input("按Enter键退出...")
            
    except KeyboardInterrupt:
        print_with_delay("\n用户中断，程序退出")
    except Exception as e:
        print_with_delay(f"\n发生未知错误: {str(e)}")
        import traceback
        traceback.print_exc()
        input("按Enter键退出...")

if __name__ == "__main__":
    main() 