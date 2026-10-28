@echo off
chcp 65001 >nul
title D4 快速启动

echo ========================================
echo   久坐肩颈腰背科学运动干预助手 - 快速启动
echo   (纯前端本地MVP，无需后端/数据库)
echo ========================================
echo.

echo [1/2] 检查前端依赖...
cd /d "%~dp0frontend"
if not exist node_modules (
    echo 安装依赖中，请稍候...
    call pnpm install
)

echo [2/2] 启动前端 (端口 5174)...
start "D4-Frontend" cmd /k "cd /d "%~dp0frontend" && pnpm dev"

echo.
echo ========================================
echo   启动完成！
echo   访问: http://localhost:5174
echo   数据存储在浏览器 localStorage 中
echo ========================================
echo.
echo 关闭窗口即可停止服务
pause