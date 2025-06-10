# Celebrity 数据管理应用

本应用是一个用于管理名人数据的Web平台，支持增删改查、数据导入导出等功能。

## 快速启动

### Windows系统
1. 双击运行 `trans_web/scripts/windows/start_app.bat`
2. 在浏览器中访问 http://localhost:5000/celeb/

### Linux/Mac系统
1. 设置可执行权限: `chmod +x trans_web/scripts/unix/start_app.sh`
2. 运行脚本: `./trans_web/scripts/unix/start_app.sh`
3. 在浏览器中访问 http://localhost:5000/celeb/

### 通过Python直接运行
```bash
# 安装依赖
pip install waitress flask flask-cors

# 设置环境变量
# Windows
set SCRIPT_NAME=/celeb
# Linux/Mac
export SCRIPT_NAME=/celeb

# 运行
python run.py
```

## 目录结构

```
trans_web/
├── core/              # 核心应用逻辑
│   ├── __init__.py    # 版本信息
│   ├── app.py         # 应用工厂函数
│   ├── middlewares.py # 中间件定义
│   └── wsgi.py        # WSGI应用入口
│
├── config/            # 配置目录
│   ├── __init__.py    # 配置加载机制
│   ├── default.py     # 默认配置
│   ├── development.py # 开发环境配置
│   └── production.py  # 生产环境配置
│
├── scripts/           # 启动和工具脚本
│   ├── start.py       # 统一启动脚本
│   ├── windows/       # Windows脚本
│   └── unix/          # Linux/Mac脚本
│
├── docs/              # 文档
│
├── features/          # 功能模块
├── static/            # 静态资源
├── templates/         # HTML模板
├── utils/             # 工具函数
├── logs/              # 日志文件
├── db_main/           # 主数据库
└── uploads/           # 上传文件
```

## 开发指南

### 运行开发环境
```bash
python -m trans_web.scripts.start --mode dev
```

### 添加新功能
1. 在`features`目录中添加新的功能模块
2. 在`core/app.py`中注册新模块的蓝图

## 配置说明

配置文件位于`config`目录：
- `default.py`: 包含默认配置
- `development.py`: 开发环境配置
- `production.py`: 生产环境配置 

可以通过`--mode`参数选择配置模式：
```bash
python run.py --mode dev  # 使用开发环境配置
python run.py --mode prod # 使用生产环境配置(默认)
```

## 部署指南

请参阅 `docs/DEPLOYMENT.md` 获取部署详细说明。

## 功能特性

- 名人数据管理：添加、修改、删除、查询名人信息
- 数据导入导出：支持JSON格式的数据导入导出
- 数据库备份：自动定时备份和手动备份功能
- 用户认证：基于会话的用户登录认证系统
- 用户管理：管理员可以添加、编辑和删除用户账号

## 用户认证系统

本应用包含基本的用户认证功能：

### 默认用户
- 管理员账号：admin / admin123
- 普通用户账号：user / user123

### 用户管理
- 管理员可以通过用户管理页面添加、修改和删除用户
- 只有管理员可以访问用户管理功能
- 用户信息保存在 `trans_web/config/users.json` 文件中

### 安全注意事项
- 在生产环境中，请修改默认密码
- 考虑实施更强的密码策略和加密存储 