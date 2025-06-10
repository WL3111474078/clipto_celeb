@echo off
echo 正在启动Celebrity应用...

:: 确保当前目录是项目根目录
cd /d %~dp0

:: 确保必要的依赖已安装
echo 正在检查并安装依赖...
pip install waitress flask flask-cors

:: 设置环境变量
set SCRIPT_NAME=/celeb
set PYTHONPATH=%CD%

:: 运行应用
echo 正在启动应用服务器...
python run.py

if %ERRORLEVEL% NEQ 0 (
    echo 启动失败！请查看上面的错误信息。
    pause
    exit /b %ERRORLEVEL%
)

pause 