@echo off
chcp 65001 > nul
cd /d "%~dp0"

:: ★★★ 关键：设置 Python 输出编码 ★★★
set PYTHONIOENCODING=utf-8

echo [%date% %time%] 开始抓取壁纸... >> log.txt

:: 1. 抓取数据
python main.py --no-html --no-image >> log.txt 2>&1

:: 2. 生成 JSON 数据
echo [%date% %time%] 生成 JSON 数据... >> log.txt
python generate_data.py >> log.txt 2>&1

:: ★★★ 3. 先强制添加所有改动（解决 unstaged changes 问题）★★★
git add . >> log.txt 2>&1

:: 4. 检查是否有变化
git diff --cached --quiet
if errorlevel 1 (
    echo [%date% %time%] 检测到新壁纸，正在提交... >> log.txt
    git commit -m "Daily Update: %date:~0,4%/%date:~5,2%/%date:~8,2%" >> log.txt 2>&1
    git pull origin main --rebase >> log.txt 2>&1
    git push origin main >> log.txt 2>&1
    echo [%date% %time%] ✅ 提交完成！ >> log.txt
) else (
    echo [%date% %time%] ℹ️ 今天没有新的壁纸更新。 >> log.txt
)

echo.
echo 按任意键关闭窗口...
pause > nul