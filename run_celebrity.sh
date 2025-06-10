#!/bin/bash
echo "==================================="
echo "   启动Celebrity数据管理系统"
echo "==================================="

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "Python3未安装！"
    echo "请安装Python 3.7或更高版本。"
    read -p "按Enter键退出..."
    exit 1
fi

# 运行Celebrity启动脚本
python3 run_celebrity.py

if [ $? -ne 0 ]; then
    echo "运行失败，请查看错误信息"
    read -p "按Enter键继续..."
fi 