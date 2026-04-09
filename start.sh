#!/bin/bash

echo "========================================"
echo "nuonuo-pet 快速启动脚本"
echo "========================================"
echo ""

# 检查虚拟环境是否存在
if [ ! -f ".venv-backend/bin/activate" ]; then
    echo "[ERROR] 虚拟环境不存在，请先运行 setup.sh"
    exit 1
fi

# 激活虚拟环境
echo "[1/3] 激活虚拟环境..."
source .venv-backend/bin/activate

# 检查依赖是否安装
echo "[2/3] 检查依赖..."
python -c "import fastapi" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "[INFO] 依赖未安装，正在安装..."
    pip install -r backend/requirements.txt
fi

# 启动应用
echo "[3/3] 启动应用..."
echo ""
echo "========================================"
echo "应用正在启动..."
echo "API 文档: http://localhost:8000/docs"
echo "Web 界面: http://localhost:8000/"
echo "按 Ctrl+C 停止应用"
echo "========================================"
echo ""

uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
