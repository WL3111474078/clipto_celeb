#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
简化版的Flask应用，专门处理index页面
"""

import os
import sys

# 获取当前目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# 设置环境变量
os.environ['SCRIPT_NAME'] = '/celeb'

# 添加当前目录到PATH
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

def debug_url_route():
    """
    用于调试的辅助函数，打印请求信息
    """
    from flask import Flask, request, render_template, redirect
    
    app = Flask(__name__,
                template_folder=os.path.join(CURRENT_DIR, 'templates'),
                static_folder=os.path.join(CURRENT_DIR, 'static'),
                static_url_path='/static')
    
    # 添加明确的路由处理
    @app.route('/')
    @app.route('/index')
    def index():
        return render_template('index.html')
    
    @app.route('/celeb')
    @app.route('/celeb/')
    def celeb_index():
        return render_template('index.html')
    
    @app.route('/test')
    def test():
        """测试路由，显示环境信息"""
        import json
        env_info = {
            'REQUEST_URI': request.environ.get('REQUEST_URI', '未设置'),
            'PATH_INFO': request.environ.get('PATH_INFO', '未设置'),
            'SCRIPT_NAME': request.environ.get('SCRIPT_NAME', '未设置'),
            'HTTP_HOST': request.environ.get('HTTP_HOST', '未设置'),
            'SERVER_NAME': request.environ.get('SERVER_NAME', '未设置'),
            'SERVER_PORT': request.environ.get('SERVER_PORT', '未设置'),
            'REQUEST_METHOD': request.environ.get('REQUEST_METHOD', '未设置'),
            'application.root_path': app.root_path,
            'application.instance_path': app.instance_path,
            'application_root': app.config.get('APPLICATION_ROOT', '未设置')
        }
        
        return f"""
        <html>
        <head><title>URL路由调试</title></head>
        <body>
        <h1>URL路由调试信息</h1>
        <h2>环境变量:</h2>
        <pre>{json.dumps(env_info, indent=2)}</pre>
        <h2>已注册路由:</h2>
        <ul>
        {''.join(f'<li>{rule}</li>' for rule in app.url_map.iter_rules())}
        </ul>
        <h2>链接测试:</h2>
        <ul>
        <li><a href="/">根路径(/)</a></li>
        <li><a href="/index">Index路径(/index)</a></li>
        <li><a href="/celeb">Celeb路径(/celeb)</a></li>
        <li><a href="/celeb/">Celeb路径带斜杠(/celeb/)</a></li>
        </ul>
        </body>
        </html>
        """
    
    return app

if __name__ == "__main__":
    print("创建简化Flask应用...")
    app = debug_url_route()
    print("运行简化Flask应用...")
    app.run(host='0.0.0.0', port=5000, debug=True) 