@echo off
chcp 65001 >nul
echo --------------------------------------------------
echo 检查虚拟环境是否存在...
if exist venv (
  echo 虚拟环境已存在。
) else (
  echo 虚拟环境不存在，正在创建...
  python -m venv venv
  echo 激活虚拟环境并安装依赖...
  call venv\Scripts\activate.bat
  pip install -r requirements.txt
  goto run_script
)

echo 激活虚拟环境...
call venv\Scripts\activate.bat

:run_script
echo 运行转换脚本...
python main.py

echo --------------------------------------------------
echo 完成！
pause
