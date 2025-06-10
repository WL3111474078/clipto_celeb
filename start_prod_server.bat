@echo off
echo 正在启动生产环境服务器...

:: 设置环境变量，防止中文乱码
set PYTHONIOENCODING=utf-8

:: 进入trans_web目录
cd /d %~dp0\trans_web

:: 激活虚拟环境（请根据实际情况修改路径）
:: 如果您使用的是Anaconda/Miniconda虚拟环境
call D:\3_professional_softwares\Anaconda3\Scripts\activate.bat cel_collect

:: 如果您使用的是标准Python venv环境，取消下面一行的注释并修改路径
:: call ..\venv\Scripts\activate.bat

:: 确保waitress已安装
pip install waitress

:: 运行生产服务器
python run_production.py

pause 