@echo off
echo ===================================
echo   启动Celebrity数据管理系统
echo ===================================

:: 设置当前目录
cd /d %~dp0

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo Python未安装或未添加到PATH环境变量！
    echo 请安装Python 3.7或更高版本。
    pause
    exit /b 1
)

:: 运行Celebrity启动脚本
python run_celebrity.py

if errorlevel 1 (
    echo 运行失败，请查看错误信息
    pause
) 