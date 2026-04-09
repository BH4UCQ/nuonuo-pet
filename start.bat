@echo off
echo ========================================
echo nuonuo-pet 快速启动脚本
echo ========================================
echo.

REM 检查虚拟环境是否存在
if not exist ".venv-backend\Scripts\activate.bat" (
    echo [ERROR] 虚拟环境不存在，请先运行 setup.bat
    pause
    exit /b 1
)

REM 激活虚拟环境
echo [1/3] 激活虚拟环境...
call .venv-backend\Scripts\activate.bat

REM 检查依赖是否安装
echo [2/3] 检查依赖...
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo [INFO] 依赖未安装，正在安装...
    pip install -r backend/requirements.txt
)

REM 启动应用
echo [3/3] 启动应用...
echo.
echo ========================================
echo 应用正在启动...
echo API 文档: http://localhost:8000/docs
echo Web 界面: http://localhost:8000/
echo 按 Ctrl+C 停止应用
echo ========================================
echo.

uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000

pause
