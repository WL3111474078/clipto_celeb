#!/bin/bash

echo "==================================="
echo "   启动Celebrity数据管理系统"
echo "==================================="

# 检查并安装必要的依赖
python3 -c "import sys; import pip; pip.main(['install', 'flask', 'flask-cors', 'waitress', 'ijson'])" 2>/dev/null

# 直接运行应用，使用最简化版启动脚本
python3 run_direct.py

if [ $? -ne 0 ]; then
    echo "运行失败，请查看错误信息"
    read -p "按任意键继续..."
fi 