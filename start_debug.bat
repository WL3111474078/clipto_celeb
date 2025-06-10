@echo off
echo ===================================
echo   Celebrity数据管理系统调试启动
echo ===================================

:: 检查并安装必要的依赖
python -c "import sys; import pip; pip.main(['install', 'flask', 'flask-cors', 'waitress', 'ijson'])" 2>nul

:: 先检查关键文件
echo.
echo 检查关键文件...
python check_files.py

:: 直接运行应用，使用最简化版启动脚本和调试模式
echo.
echo 启动应用服务...
python run_direct.py

if errorlevel 1 (
    echo 运行失败，请查看错误信息
    pause
) 