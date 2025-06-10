#!/bin/bash

echo "正在启动Celebrity应用..."

# 切换到项目根目录
cd "$(dirname "$0")/../.."

# 激活虚拟环境（如果有）
# 取消注释下面一行并修改路径
# source venv/bin/activate

# 确保必要的依赖已安装
pip install waitress flask flask-cors

# 设置环境变量
export SCRIPT_NAME=/celeb

# 启动应用 - 生产模式
python -m trans_web.scripts.start --mode prod 