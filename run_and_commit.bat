@echo off
chcp 65001 > nul
cd /d "%~dp0"

:: 设置 Python 输出编码
set PYTHONIOENCODING=utf-8

echo [%date% %time%] ===== 开始运行 ===== >> log.txt

:: 1. 抓取数据
echo [%date% %time%] 步骤1: 抓取壁纸数据... >> log.txt
python main.py --no-html --no-image >> log.txt 2>&1
if errorlevel 1 (
    echo [%date% %time%] ❌ main.py 执行失败！ >> log.txt
    goto :error
)

:: 2. 生成 JSON 数据
echo [%date% %time%] 步骤2: 生成 JSON 数据... >> log.txt
python generate_data.py >> log.txt 2>&1
if errorlevel 1 (
    echo [%date% %time%] ❌ generate_data.py 执行失败！ >> log.txt
    goto :error
)

:: 3. 先强制添加所有变更（包括 JSON）
git add source_list.csv data/wallpapers.json >> log.txt 2>&1

:: 4. 检查是否有变化
git diff --cached --quiet
if errorlevel 1 (
    echo [%date% %time%] 检测到新壁纸，准备提交... >> log.txt
    
    :: 获取标准日期
    for /f "tokens=1-3 delims=/-. " %%a in ('powershell -Command "Get-Date -Format 'yyyy-MM-dd'"') do (
        set TODAY=%%a-%%b-%%c
    )
    
    :: 提交本地更改
    git commit -m "chnbsdan_bot: %TODAY%" >> log.txt 2>&1
    if errorlevel 1 (
        echo [%date% %time%] ❌ 提交失败！ >> log.txt
        goto :error
    )
    
    :: ★★★ 关键修复：先拉取远程更新（使用普通 pull，不要 rebase）★★★
    echo [%date% %time%] 正在同步远程仓库... >> log.txt
    git pull origin main --no-edit >> log.txt 2>&1
    
    :: 如果有合并冲突，自动解决（保留本地版本）
    if errorlevel 1 (
        echo [%date% %time%] ⚠️ 拉取有冲突，尝试强制推送... >> log.txt
        git push origin main --force-with-lease >> log.txt 2>&1
    ) else (
        :: 推送本地更改
        git push origin main >> log.txt 2>&1
    )
    
    if errorlevel 1 (
        echo [%date% %time%] ❌ 推送失败！ >> log.txt
        goto :error
    )
    
    echo [%date% %time%] ✅ 提交完成！ >> log.txt
) else (
    echo [%date% %time%] ℹ️ 今天没有新的壁纸更新。 >> log.txt
)

:success
echo [%date% %time%] ===== 运行结束（成功） ===== >> log.txt
echo.
echo ✅ 运行完成！
timeout /t 3 > nul
exit /b 0

:error
echo [%date% %time%] ===== 运行结束（失败） ===== >> log.txt
echo.
echo ❌ 运行出错！请查看 log.txt 了解详情。
pause
exit /b 1