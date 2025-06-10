@echo off
echo ===================================
echo   启动Celebrity数据管理系统
echo ===================================

:: 检查并安装必要的依赖
python -c "import sys; import pip; pip.main(['install', 'flask', 'flask-cors', 'waitress', 'ijson'])" 2>nul

:: 直接运行应用，使用最简化版启动脚本
python run_direct.py

if errorlevel 1 (
    echo 运行失败，请查看错误信息
    pause
) 