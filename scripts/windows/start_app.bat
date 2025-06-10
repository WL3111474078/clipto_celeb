@echo off
echo 正在启动Celebrity应用...

:: 确保在正确的目录
cd /d %~dp0\..\..

:: 激活虚拟环境（请根据实际情况修改路径）
:: 如果您使用的是Anaconda/Miniconda虚拟环境
call D:\3_professional_softwares\Anaconda3\Scripts\activate.bat cel_collect

:: 如果您使用的是标准Python venv环境，取消下面一行的注释并修改路径
:: call venv\Scripts\activate.bat

:: 确保必要的依赖已安装
pip install waitress flask flask-cors

:: 设置环境变量
set SCRIPT_NAME=/celeb

:: 启动应用 - 生产模式
python -m trans_web.scripts.start --mode prod

pause 