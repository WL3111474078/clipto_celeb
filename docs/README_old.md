# Celebrity 数据管理应用

本应用是一个用于管理名人数据的Web平台，支持增删改查、数据导入导出等功能。

## 快速启动

### Windows系统
1. 双击运行 `start_app.bat`
2. 在浏览器中访问 http://localhost:5000/celeb/

### Linux/Mac系统
1. 设置可执行权限: `chmod +x start_app.sh`
2. 运行脚本: `./start_app.sh`
3. 在浏览器中访问 http://localhost:5000/celeb/

## 启动选项

本应用提供多种启动方式：

### 统一启动脚本 (推荐)
```bash
# 生产模式（默认）
python start.py

# 开发模式
python start.py --mode dev

# 自定义端口
python start.py --port 8080

# 自定义应用根路径
python start.py --root /celebrity
```

### 子目录访问脚本
```bash
# Windows
run_celeb.bat

# Linux/Mac
./run_celeb.sh
```

### 生产环境专用
```bash
python run_production.py
```

### 直接运行应用（不推荐）
```bash
python app.py
```
注意：直接运行app.py可能在某些环境中无法正确处理子目录访问。

## 环境变量设置

如需手动设置环境变量：

### Windows
```cmd
set SCRIPT_NAME=/celeb
```

### Linux/Mac
```bash
export SCRIPT_NAME=/celeb
```

也可以使用提供的环境变量设置脚本：
- Windows: `set_celeb_env.bat`
- Linux/Mac: `source set_celeb_env.sh`

## 目录结构

- `app.py`: 应用主程序
- `start.py`: 统一启动脚本
- `run_production.py`: 生产环境启动脚本
- `wsgi.py`: WSGI服务器配置
- `production_config.py`: 生产环境配置
- `features/`: 功能模块
- `templates/`: HTML模板
- `static/`: 静态资源
- `db_main/`: 主数据库
- `logs/`: 日志文件

## 部署说明

关于如何在生产环境中部署本应用，请参阅 `PRODUCTION_DEPLOYMENT.md` 文件。 