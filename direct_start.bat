@echo off

echo 正在启动Celebrity数据管理应用(直接模式)...
echo.

:: 安装必要依赖
pip install -q flask flask-cors waitress ijson

:: 使用直接启动脚本 
python "%~dp0run_direct.py"

pause 