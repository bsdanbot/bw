@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo [%date% %time%] 开始抓取壁纸... >> log.txt

:: 运行主程序（跳过HTML生成，跳过图片下载以加快速度）
python main.py --no-html --no-image >> log.txt 2>&1

:: 检查 source_list.csv 是否有变化
git diff --quiet source_list.csv
if errorlevel 1 (
    echo [%date% %time%] 检测到新壁纸，正在提交... >> log.txt
    git add source_list.csv data\wallpapers.json >> log.txt 2>&1
    git commit -m "Daily Update: source_list.csv %date:~0,4%/%date:~5,2%/%date:~8,2%" >> log.txt 2>&1
    git push origin main >> log.txt 2>&1
    echo [%date% %time%] 提交完成！ >> log.txt
) else (
    echo [%date% %time%] 今天没有新的壁纸更新。 >> log.txt
)

echo.
echo 按任意键关闭窗口...
pause > nul