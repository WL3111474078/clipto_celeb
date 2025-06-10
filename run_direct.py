#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
最精简版的启动脚本
使用最基本的Flask方式启动应用
"""

import os
import sys
import logging
import traceback

# 获取当前目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 添加当前目录到路径
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

def run_app():
    """直接运行应用，不使用中间件和复杂配置"""
    print("\n======================================")
    print("    直接模式启动Celebrity数据管理系统")
    print("======================================\n")
    
    # 安装所有必要依赖
    try:
        import pip
        print("安装所有必要依赖...")
        dependencies = ["flask", "flask-cors", "waitress", "ijson"]
        for dep in dependencies:
            print(f"正在安装 {dep}...")
            pip.main(['install', dep])
        print("依赖安装完成")
    except Exception as e:
        print(f"依赖安装出错: {str(e)}")
    
    # 导入Flask并创建最简单的应用
    try:
        from flask import Flask, render_template, request, send_from_directory, jsonify, redirect, url_for
        
        # 配置基本日志
        logging.basicConfig(level=logging.DEBUG, 
                           format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger = logging.getLogger('direct_app')
        
        # 创建最简单的Flask应用
        app = Flask(__name__, 
                   template_folder=os.path.join(CURRENT_DIR, 'templates'),
                   static_folder=os.path.join(CURRENT_DIR, 'static'),
                   static_url_path='/static')
        
        # 禁用严格的URL斜杠处理
        app.url_map.strict_slashes = False
        
        # 添加异常处理器，方便调试
        @app.errorhandler(Exception)
        def handle_exception(e):
            error_tb = traceback.format_exc()
            logger.error(f"发生错误: {str(e)}", exc_info=True)
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>服务器错误</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    pre {{ background: #f0f0f0; padding: 10px; border-radius: 5px; overflow: auto; }}
                    h1 {{ color: #d9534f; }}
                    .error-details {{ margin-top: 20px; }}
                </style>
            </head>
            <body>
                <h1>服务器错误</h1>
                <p>应用程序遇到了一个错误: {str(e)}</p>
                
                <div class="error-details">
                    <h2>错误详情</h2>
                    <pre>{error_tb}</pre>
                </div>
                
                <div class="error-details">
                    <h2>请求信息</h2>
                    <pre>
路径: {request.path}
方法: {request.method}
URL: {request.url}
路径信息: {request.environ.get('PATH_INFO', '未知')}
脚本名称: {request.environ.get('SCRIPT_NAME', '未知')}
                    </pre>
                </div>
                
                <p><a href="/">返回首页</a> | <a href="/debug">查看调试信息</a></p>
            </body>
            </html>
            """, 500
            
        @app.errorhandler(404)
        def page_not_found(e):
            logger.error(f"页面未找到: {request.path}")
            
            # 获取所有已注册的路由
            routes = []
            for rule in app.url_map.iter_rules():
                routes.append({
                    'endpoint': rule.endpoint,
                    'methods': [m for m in rule.methods if m != 'OPTIONS' and m != 'HEAD'],
                    'rule': str(rule)
                })
            
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>页面未找到</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    pre {{ background: #f0f0f0; padding: 10px; border-radius: 5px; overflow: auto; }}
                    h1 {{ color: #d9534f; }}
                    .error-details {{ margin-top: 20px; }}
                    .route {{ margin-bottom: 5px; }}
                </style>
            </head>
            <body>
                <h1>页面未找到 (404)</h1>
                <p>请求的URL <code>{request.path}</code> 在服务器上未找到。</p>
                
                <div class="error-details">
                    <h2>请求信息</h2>
                    <pre>
路径: {request.path}
方法: {request.method}
URL: {request.url}
路径信息: {request.environ.get('PATH_INFO', '未知')}
脚本名称: {request.environ.get('SCRIPT_NAME', '未知')}
                    </pre>
                </div>
                
                <div class="error-details">
                    <h2>可用路由</h2>
                    <div>
                        {"".join(f'<div class="route"><code>{r["rule"]}</code> - {", ".join(r["methods"])} - {r["endpoint"]}</div>' for r in routes)}
                    </div>
                </div>
                
                <p><a href="/">返回首页</a> | <a href="/debug">查看调试信息</a></p>
            </body>
            </html>
            """, 404
        
        # 添加请求钩子，记录每个请求
        @app.before_request
        def log_request():
            logger.info(f"请求: {request.method} {request.url}")
            logger.debug(f"请求头: {dict(request.headers)}")
            logger.debug(f"请求路径: PATH_INFO={request.environ.get('PATH_INFO')}, SCRIPT_NAME={request.environ.get('SCRIPT_NAME')}")
        
        # 注册基本路由 - 支持多种访问方式
        @app.route('/')
        @app.route('/index')
        @app.route('/index.html')
        def index():
            logger.info("访问首页")
            from datetime import datetime
            return render_template('index_new.html', now=datetime.now())
        
        # 为确保能够通过'/celeb/'访问
        @app.route('/celeb')
        @app.route('/celeb/')
        @app.route('/celeb/index')
        @app.route('/celeb/index.html')
        def celeb_root():
            logger.info("通过/celeb/访问首页")
            from datetime import datetime
            return render_template('index_new.html', now=datetime.now())
        
        # 特殊调试路由
        @app.route('/debug')
        @app.route('/celeb/debug')
        def debug_route():
            import json
            route_info = []
            for rule in app.url_map.iter_rules():
                route_info.append({
                    'endpoint': rule.endpoint,
                    'methods': [m for m in rule.methods if m != 'OPTIONS' and m != 'HEAD'],
                    'rule': str(rule)
                })
            
            env_info = {
                'PATH_INFO': request.environ.get('PATH_INFO', '未设置'),
                'SCRIPT_NAME': request.environ.get('SCRIPT_NAME', '未设置'),
                'HTTP_HOST': request.environ.get('HTTP_HOST', '未设置'),
                'REQUEST_METHOD': request.environ.get('REQUEST_METHOD', '未设置'),
                'SERVER_NAME': request.environ.get('SERVER_NAME', '未设置'),
                'SERVER_PORT': request.environ.get('SERVER_PORT', '未设置'),
                'OS': os.name, 
                'CWD': os.getcwd(),
                'PYTHONPATH': os.environ.get('PYTHONPATH', '未设置'),
                'FLASK_APP': os.environ.get('FLASK_APP', '未设置'),
                'FLASK_ENV': os.environ.get('FLASK_ENV', '未设置')
            }
            
            files_info = {}
            important_dirs = ['templates', 'static', 'core', 'features', 'utils']
            for dir_name in important_dirs:
                dir_path = os.path.join(CURRENT_DIR, dir_name)
                if os.path.exists(dir_path):
                    files = os.listdir(dir_path)
                    files_info[dir_name] = files[:20] # 限制显示数量
            
            template_files = []
            if os.path.exists(os.path.join(CURRENT_DIR, 'templates')):
                template_files = os.listdir(os.path.join(CURRENT_DIR, 'templates'))
                
            response = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>调试信息</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    pre {{ background: #f0f0f0; padding: 10px; border-radius: 5px; overflow: auto; }}
                    h2 {{ color: #333; border-bottom: 1px solid #ccc; padding-bottom: 5px; }}
                    .route {{ margin-bottom: 5px; }}
                    .section {{ margin-bottom: 30px; }}
                </style>
            </head>
            <body>
                <h1>Celebrity应用调试信息</h1>
                
                <div class="section">
                    <h2>环境信息</h2>
                    <pre>{json.dumps(env_info, indent=2, ensure_ascii=False)}</pre>
                </div>
                
                <div class="section">
                    <h2>模板文件 ({len(template_files)}个)</h2>
                    <pre>{json.dumps(template_files, indent=2, ensure_ascii=False)}</pre>
                </div>
                
                <div class="section">
                    <h2>注册的路由 ({len(route_info)}个)</h2>
                    <div>
                        {"".join(f'<div class="route"><code>{r["rule"]}</code> - {", ".join(r["methods"])} - {r["endpoint"]}</div>' for r in route_info)}
                    </div>
                </div>
                
                <div class="section">
                    <h2>目录内容</h2>
                    <pre>{json.dumps(files_info, indent=2, ensure_ascii=False)}</pre>
                </div>
                
                <div class="section">
                    <h2>测试链接</h2>
                    <ul>
                        <li><a href="/">根路径 (/)</a></li>
                        <li><a href="/index">Index (/index)</a></li>
                        <li><a href="/celeb">Celeb (/celeb)</a></li>
                        <li><a href="/celeb/">Celeb 带斜杠 (/celeb/)</a></li>
                        <li><a href="/list">列表页 (/list)</a></li>
                        <li><a href="/celeb/list">列表页 (/celeb/list)</a></li>
                        <li><a href="/add">添加页 (/add)</a></li>
                        <li><a href="/celeb/add">添加页 (/celeb/add)</a></li>
                    </ul>
                </div>
            </body>
            </html>
            """
            return response
        
        # 注册其他重要路由
        @app.route('/list')
        def list_page():
            logger.info("访问列表页")
            try:
                return render_template('list.html')
            except Exception as e:
                logger.error(f"渲染list.html时出错: {str(e)}", exc_info=True)
                return f"渲染模板出错: {str(e)}", 500
            
        @app.route('/celeb/list')
        def celeb_list_page():
            logger.info("通过/celeb/访问列表页")
            try:
                return render_template('list.html')
            except Exception as e:
                logger.error(f"渲染list.html时出错: {str(e)}", exc_info=True)
                return f"渲染模板出错: {str(e)}", 500
            
        @app.route('/search')
        def search_page():
            logger.info("访问搜索页")
            try:
                return render_template('search.html')
            except Exception as e:
                logger.error(f"渲染search.html时出错: {str(e)}", exc_info=True)
                return f"渲染模板出错: {str(e)}", 500
            
        @app.route('/celeb/search')
        def celeb_search_page():
            logger.info("通过/celeb/访问搜索页")
            try:
                return render_template('search.html')
            except Exception as e:
                logger.error(f"渲染search.html时出错: {str(e)}", exc_info=True)
                return f"渲染模板出错: {str(e)}", 500
            
        @app.route('/add')
        def add_page():
            logger.info("访问添加页")
            try:
                return render_template('add.html')
            except Exception as e:
                logger.error(f"渲染add.html时出错: {str(e)}", exc_info=True)
                return f"渲染模板出错: {str(e)}", 500
        
        @app.route('/celeb/add')
        def celeb_add_page():
            logger.info("通过/celeb/访问添加页")
            try:
                return render_template('add.html')
            except Exception as e:
                logger.error(f"渲染add.html时出错: {str(e)}", exc_info=True)
                return f"渲染模板出错: {str(e)}", 500
        
        @app.route('/edit')
        def edit_page():
            logger.info("访问编辑页")
            try:
                return render_template('edit.html')
            except Exception as e:
                logger.error(f"渲染edit.html时出错: {str(e)}", exc_info=True)
                return f"渲染模板出错: {str(e)}", 500
        
        @app.route('/celeb/edit')
        def celeb_edit_page():
            logger.info("通过/celeb/访问编辑页")
            try:
                return render_template('edit.html')
            except Exception as e:
                logger.error(f"渲染edit.html时出错: {str(e)}", exc_info=True)
                return f"渲染模板出错: {str(e)}", 500
        
        @app.route('/delete')
        def delete_page():
            logger.info("访问删除页")
            try:
                return render_template('delete.html')
            except Exception as e:
                logger.error(f"渲染delete.html时出错: {str(e)}", exc_info=True)
                return f"渲染模板出错: {str(e)}", 500
            
        @app.route('/celeb/delete')
        def celeb_delete_page():
            logger.info("通过/celeb/访问删除页")
            try:
                return render_template('delete.html')
            except Exception as e:
                logger.error(f"渲染delete.html时出错: {str(e)}", exc_info=True)
                return f"渲染模板出错: {str(e)}", 500
            
        @app.route('/static/<path:filename>')
        def serve_static(filename):
            logger.debug(f"提供静态文件: {filename}")
            return send_from_directory(app.static_folder, filename)
            
        @app.route('/celeb/static/<path:filename>')
        def serve_celeb_static(filename):
            logger.debug(f"通过/celeb/提供静态文件: {filename}")
            return send_from_directory(app.static_folder, filename)
        
        # 确认应用是否正常
        print("\n所有路由已配置，启动服务器...")
        print(f"模板目录: {app.template_folder}")
        print(f"静态文件目录: {app.static_folder}")
        print("注册的路由:")
        for rule in app.url_map.iter_rules():
            print(f"  {rule}")
        
        # 优先使用Flask开发服务器运行，更容易调试
        print("\n=== 启动Flask开发服务器 ===")
        print("访问地址: http://localhost:5000/ 或 http://localhost:5000/celeb/")
        print("调试页面: http://localhost:5000/debug")
        app.run(host='0.0.0.0', port=5000, debug=True)
            
    except ImportError as e:
        print(f"导入错误: {str(e)}")
        print("请手动安装所需依赖: pip install flask flask-cors waitress ijson")
    except Exception as e:
        print(f"启动失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_app() 