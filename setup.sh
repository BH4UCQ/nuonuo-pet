#!/bin/bash

echo "========================================"
echo "nuonuo-pet 环境设置脚本"
echo "========================================"
echo ""

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 未安装或不在 PATH 中"
    echo "请先安装 Python 3.7 或更高版本"
    exit 1
fi

echo "[1/5] Python 版本检查通过"
python3 --version

# 创建虚拟环境
echo ""
echo "[2/5] 创建虚拟环境..."
if [ -d ".venv-backend" ]; then
    echo "[INFO] 虚拟环境已存在，跳过创建"
else
    python3 -m venv .venv-backend
    echo "[OK] 虚拟环境创建成功"
fi

# 激活虚拟环境
echo ""
echo "[3/5] 激活虚拟环境..."
source .venv-backend/bin/activate

# 升级 pip
echo ""
echo "[4/5] 升级 pip..."
python -m pip install --upgrade pip

# 安装依赖
echo ""
echo "[5/5] 安装项目依赖..."
pip install -r backend/requirements.txt

echo ""
echo "========================================"
echo "环境设置完成！"
echo "========================================"
echo ""
echo "下一步："
echo "1. 运行 ./start.sh 启动应用"
echo "2. 访问 http://localhost:8000/docs 查看 API 文档"
echo "3. 访问 http://localhost:8000/ 使用 Web 界面"
echo ""
