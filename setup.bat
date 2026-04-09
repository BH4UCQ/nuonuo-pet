@echo off
echo ========================================
echo nuonuo-pet 环境设置脚本
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 未安装或不在 PATH 中
    echo 请先安装 Python 3.7 或更高版本
    pause
    exit /b 1
)

echo [1/5] Python 版本检查通过
python --version

REM 创建虚拟环境
echo.
echo [2/5] 创建虚拟环境...
if exist ".venv-backend" (
    echo [INFO] 虚拟环境已存在，跳过创建
) else (
    python -m venv .venv-backend
    echo [OK] 虚拟环境创建成功
)

REM 激活虚拟环境
echo.
echo [3/5] 激活虚拟环境...
call .venv-backend\Scripts\activate.bat

REM 升级 pip
echo.
echo [4/5] 升级 pip...
python -m pip install --upgrade pip

REM 安装依赖
echo.
echo [5/5] 安装项目依赖...
pip install -r backend/requirements.txt

echo.
echo ========================================
echo 环境设置完成！
echo ========================================
echo.
echo 下一步：
echo 1. 运行 start.bat 启动应用
echo 2. 访问 http://localhost:8000/docs 查看 API 文档
echo 3. 访问 http://localhost:8000/ 使用 Web 界面
echo.
pause
