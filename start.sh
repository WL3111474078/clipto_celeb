#!/bin/bash

echo "正在启动Celebrity应用..."

# 确保必要的依赖已安装
pip install waitress flask flask-cors

# 设置环境变量
export SCRIPT_NAME=/celeb

# 运行应用
python run.py 