#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
文件检查工具
用于诊断应用中关键文件是否存在
"""

import os
import sys

def check_files():
    """检查关键文件是否存在"""
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 检查模板目录
    template_dir = os.path.join(current_dir, 'templates')
    if not os.path.exists(template_dir):
        print(f"[错误] 模板目录不存在: {template_dir}")
        os.makedirs(template_dir)
        print(f"[修复] 已创建模板目录: {template_dir}")
    else:
        print(f"[成功] 模板目录存在: {template_dir}")
    
    # 检查index.html模板是否存在
    index_file = os.path.join(template_dir, 'index.html')
    if not os.path.exists(index_file):
        print(f"[错误] index.html模板不存在: {index_file}")
        # 创建简单的index.html
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Celebrity数据管理系统</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            min-height: 95vh;
        }
        .container {
            max-width: 800px;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        h1 { color: #333; }
        .menu { margin: 25px 0; }
        .menu a {
            background-color: #0078D7;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            margin: 0 10px;
            display: inline-block;
        }
        .menu a:hover { background-color: #005a9e; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Celebrity数据管理系统</h1>
        <p>欢迎使用Celebrity数据管理系统</p>
        
        <div class="menu">
            <a href="/celeb/list">查看列表</a>
            <a href="/celeb/search">搜索数据</a>
            <a href="/celeb/add">添加数据</a>
        </div>
    </div>
</body>
</html>""")
        print(f"[修复] 已创建简单的index.html模板: {index_file}")
    else:
        print(f"[成功] index.html模板存在: {index_file}")
    
    # 检查其他功能页面模板
    templates = {
        'list.html': """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>人物库列表 - Celebrity数据管理系统</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 { 
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .back-btn {
            background-color: #555;
            color: white;
            padding: 8px 15px;
            text-decoration: none;
            border-radius: 5px;
        }
        .back-btn:hover { background-color: #333; }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #0078D7;
            color: white;
        }
        tr:hover { background-color: #f5f5f5; }
        .action-btn {
            background-color: #0078D7;
            color: white;
            padding: 6px 12px;
            text-decoration: none;
            border-radius: 4px;
            margin-right: 5px;
            display: inline-block;
        }
        .action-btn:hover { background-color: #005a9e; }
        .delete-btn { background-color: #d9534f; }
        .delete-btn:hover { background-color: #c9302c; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <a href="/celeb/" class="back-btn">返回首页</a>
            <h1>人物库列表</h1>
            <a href="/celeb/add" class="action-btn">添加新人物</a>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>ID</th>
                    <th>姓名</th>
                    <th>性别</th>
                    <th>职业</th>
                    <th>国籍</th>
                    <th>操作</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>1</td>
                    <td>张三</td>
                    <td>男</td>
                    <td>演员</td>
                    <td>中国</td>
                    <td>
                        <a href="/celeb/edit?id=1" class="action-btn">编辑</a>
                        <a href="/celeb/delete?id=1" class="action-btn delete-btn">删除</a>
                    </td>
                </tr>
                <tr>
                    <td>2</td>
                    <td>李四</td>
                    <td>女</td>
                    <td>歌手</td>
                    <td>中国</td>
                    <td>
                        <a href="/celeb/edit?id=2" class="action-btn">编辑</a>
                        <a href="/celeb/delete?id=2" class="action-btn delete-btn">删除</a>
                    </td>
                </tr>
                <tr>
                    <td>3</td>
                    <td>王五</td>
                    <td>男</td>
                    <td>导演</td>
                    <td>中国</td>
                    <td>
                        <a href="/celeb/edit?id=3" class="action-btn">编辑</a>
                        <a href="/celeb/delete?id=3" class="action-btn delete-btn">删除</a>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>""",
        'search.html': """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>搜索人物 - Celebrity数据管理系统</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 { 
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .back-btn {
            background-color: #555;
            color: white;
            padding: 8px 15px;
            text-decoration: none;
            border-radius: 5px;
        }
        .back-btn:hover { background-color: #333; }
        .search-form {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        input[type="text"], select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        .btn-search {
            background-color: #0078D7;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        .btn-search:hover { background-color: #005a9e; }
        .results {
            margin-top: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #0078D7;
            color: white;
        }
        tr:hover { background-color: #f5f5f5; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <a href="/celeb/" class="back-btn">返回首页</a>
            <h1>搜索人物</h1>
        </div>
        
        <div class="search-form">
            <form action="/celeb/search" method="post">
                <div class="form-group">
                    <label for="name">姓名</label>
                    <input type="text" id="name" name="name" placeholder="输入姓名关键词">
                </div>
                
                <div class="form-group">
                    <label for="occupation">职业</label>
                    <input type="text" id="occupation" name="occupation" placeholder="输入职业关键词">
                </div>
                
                <div class="form-group">
                    <label for="nationality">国籍</label>
                    <input type="text" id="nationality" name="nationality" placeholder="输入国籍关键词">
                </div>
                
                <div class="form-group">
                    <label for="gender">性别</label>
                    <select id="gender" name="gender">
                        <option value="">全部</option>
                        <option value="male">男</option>
                        <option value="female">女</option>
                    </select>
                </div>
                
                <button type="submit" class="btn-search">搜索</button>
            </form>
        </div>
        
        <div class="results">
            <h2>搜索结果</h2>
            <p>请输入搜索条件并点击搜索按钮</p>
        </div>
    </div>
</body>
</html>""",
        'add.html': """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>添加人物 - Celebrity数据管理系统</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 { 
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .back-btn {
            background-color: #555;
            color: white;
            padding: 8px 15px;
            text-decoration: none;
            border-radius: 5px;
        }
        .back-btn:hover { background-color: #333; }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        input[type="text"], 
        input[type="date"], 
        select, 
        textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
            font-size: 16px;
        }
        textarea {
            height: 120px;
            resize: vertical;
        }
        .btn-submit {
            background-color: #0078D7;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            display: block;
            margin: 30px auto 0;
            min-width: 200px;
        }
        .btn-submit:hover { background-color: #005a9e; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <a href="/celeb/" class="back-btn">返回首页</a>
            <h1>添加新人物</h1>
        </div>
        
        <form action="/celeb/add" method="post">
            <div class="form-group">
                <label for="name">姓名 *</label>
                <input type="text" id="name" name="name" required placeholder="请输入姓名">
            </div>
            
            <div class="form-group">
                <label for="english_name">英文名</label>
                <input type="text" id="english_name" name="english_name" placeholder="请输入英文名（如有）">
            </div>
            
            <div class="form-group">
                <label for="gender">性别 *</label>
                <select id="gender" name="gender" required>
                    <option value="">请选择</option>
                    <option value="male">男</option>
                    <option value="female">女</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="birth_date">出生日期</label>
                <input type="date" id="birth_date" name="birth_date">
            </div>
            
            <div class="form-group">
                <label for="nationality">国籍 *</label>
                <input type="text" id="nationality" name="nationality" required placeholder="请输入国籍">
            </div>
            
            <div class="form-group">
                <label for="occupation">职业 *</label>
                <input type="text" id="occupation" name="occupation" required placeholder="请输入职业，多个职业用逗号分隔">
            </div>
            
            <div class="form-group">
                <label for="description">简介</label>
                <textarea id="description" name="description" placeholder="请输入人物简介"></textarea>
            </div>
            
            <button type="submit" class="btn-submit">提交</button>
        </form>
    </div>
</body>
</html>""",
        'edit.html': """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>编辑人物 - Celebrity数据管理系统</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 { 
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .back-btn {
            background-color: #555;
            color: white;
            padding: 8px 15px;
            text-decoration: none;
            border-radius: 5px;
        }
        .back-btn:hover { background-color: #333; }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        input[type="text"], 
        input[type="date"], 
        select, 
        textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
            font-size: 16px;
        }
        textarea {
            height: 120px;
            resize: vertical;
        }
        .btn-submit {
            background-color: #0078D7;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            display: block;
            margin: 30px auto 0;
            min-width: 200px;
        }
        .btn-submit:hover { background-color: #005a9e; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <a href="/celeb/" class="back-btn">返回首页</a>
            <h1>编辑人物信息</h1>
        </div>
        
        <form action="/celeb/edit" method="post">
            <input type="hidden" id="id" name="id" value="1">
            
            <div class="form-group">
                <label for="name">姓名 *</label>
                <input type="text" id="name" name="name" required value="张三">
            </div>
            
            <div class="form-group">
                <label for="english_name">英文名</label>
                <input type="text" id="english_name" name="english_name" value="Zhang San">
            </div>
            
            <div class="form-group">
                <label for="gender">性别 *</label>
                <select id="gender" name="gender" required>
                    <option value="">请选择</option>
                    <option value="male" selected>男</option>
                    <option value="female">女</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="birth_date">出生日期</label>
                <input type="date" id="birth_date" name="birth_date" value="1980-01-01">
            </div>
            
            <div class="form-group">
                <label for="nationality">国籍 *</label>
                <input type="text" id="nationality" name="nationality" required value="中国">
            </div>
            
            <div class="form-group">
                <label for="occupation">职业 *</label>
                <input type="text" id="occupation" name="occupation" required value="演员">
            </div>
            
            <div class="form-group">
                <label for="description">简介</label>
                <textarea id="description" name="description">著名演员，主演过多部电影和电视剧。</textarea>
            </div>
            
            <button type="submit" class="btn-submit">保存修改</button>
        </form>
    </div>
</body>
</html>""",
        'delete.html': """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>删除人物 - Celebrity数据管理系统</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background-color: #f5f5f5;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        h1 { 
            color: #333;
            margin-bottom: 30px;
        }
        .warning {
            color: #d9534f;
            font-size: 18px;
            margin-bottom: 30px;
        }
        .info {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
            text-align: left;
        }
        .info p {
            margin: 10px 0;
        }
        .info strong {
            display: inline-block;
            width: 80px;
        }
        .buttons {
            margin-top: 30px;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin: 0 10px;
        }
        .btn-delete {
            background-color: #d9534f;
            color: white;
        }
        .btn-delete:hover { background-color: #c9302c; }
        .btn-cancel {
            background-color: #555;
            color: white;
            text-decoration: none;
            display: inline-block;
        }
        .btn-cancel:hover { background-color: #333; }
    </style>
</head>
<body>
    <div class="container">
        <h1>删除人物确认</h1>
        
        <p class="warning">警告：此操作将永久删除该人物的所有信息，无法恢复！</p>
        
        <div class="info">
            <p><strong>ID:</strong> 1</p>
            <p><strong>姓名:</strong> 张三</p>
            <p><strong>性别:</strong> 男</p>
            <p><strong>职业:</strong> 演员</p>
            <p><strong>国籍:</strong> 中国</p>
        </div>
        
        <div class="buttons">
            <form action="/celeb/delete" method="post" style="display:inline;">
                <input type="hidden" name="id" value="1">
                <button type="submit" class="btn btn-delete">确认删除</button>
            </form>
            <a href="/celeb/list" class="btn btn-cancel">取消</a>
        </div>
    </div>
</body>
</html>"""
    }
    
    # 检查并创建所有模板文件
    for template_name, template_content in templates.items():
        template_path = os.path.join(template_dir, template_name)
        if not os.path.exists(template_path):
            print(f"[错误] {template_name}模板不存在: {template_path}")
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template_content)
            print(f"[修复] 已创建{template_name}模板: {template_path}")
        else:
            print(f"[成功] {template_name}模板存在: {template_path}")
    
    # 检查静态文件目录
    static_dir = os.path.join(current_dir, 'static')
    if not os.path.exists(static_dir):
        print(f"[错误] 静态文件目录不存在: {static_dir}")
        os.makedirs(static_dir)
        print(f"[修复] 已创建静态文件目录: {static_dir}")
    else:
        print(f"[成功] 静态文件目录存在: {static_dir}")
    
    # 检查其他关键目录
    key_dirs = ['core', 'features', 'utils']
    for dir_name in key_dirs:
        dir_path = os.path.join(current_dir, dir_name)
        if not os.path.exists(dir_path):
            print(f"[警告] {dir_name}目录不存在: {dir_path}")
        else:
            print(f"[成功] {dir_name}目录存在: {dir_path}")
    
    print("\n文件检查完成。如果有任何问题，请根据提示修复。")

if __name__ == "__main__":
    check_files()