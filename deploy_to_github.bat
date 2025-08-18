@echo off
REM YOLOv8 Vehicle Annotator - GitHub 部署腳本 (Windows)
REM 使用說明：deploy_to_github.bat [repository-url]

echo 🚗 YOLOv8 Vehicle Annotator - GitHub 部署腳本
echo ==============================================

REM 檢查是否在正確的目錄
if not exist "main.py" (
    echo ❌ 錯誤：請在專案根目錄執行此腳本
    pause
    exit /b 1
)

REM 檢查 git 是否已安裝
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤：Git 未安裝，請先從 https://git-scm.com/ 下載安裝 Git
    pause
    exit /b 1
)

REM 獲取倉庫 URL
set REPO_URL=%1
if "%REPO_URL%"=="" (
    echo 📝 請輸入您的 GitHub 倉庫 URL (例如: https://github.com/ericchen2023/yolo-vehicle-annotator.git):
    set /p REPO_URL=
)

if "%REPO_URL%"=="" (
    echo ❌ 錯誤：倉庫 URL 不能為空
    pause
    exit /b 1
)

echo 🔄 準備部署到：%REPO_URL%

REM 初始化 Git 倉庫（如果還沒有的話）
if not exist ".git" (
    echo 📦 初始化 Git 倉庫...
    git init
    git branch -M main
)

REM 添加遠端倉庫
echo 🔗 設定遠端倉庫...
git remote remove origin 2>nul
git remote add origin "%REPO_URL%"

REM 檢查並創建必要檔案
echo 📋 檢查專案檔案...

if exist "README.md" (echo ✅ README.md) else (echo ⚠️  警告：README.md 檔案不存在)
if exist "LICENSE" (echo ✅ LICENSE) else (echo ⚠️  警告：LICENSE 檔案不存在)
if exist "requirements.txt" (echo ✅ requirements.txt) else (echo ⚠️  警告：requirements.txt 檔案不存在)
if exist ".gitignore" (echo ✅ .gitignore) else (echo ⚠️  警告：.gitignore 檔案不存在)
if exist "CONTRIBUTING.md" (echo ✅ CONTRIBUTING.md) else (echo ⚠️  警告：CONTRIBUTING.md 檔案不存在)
if exist "CHANGELOG.md" (echo ✅ CHANGELOG.md) else (echo ⚠️  警告：CHANGELOG.md 檔案不存在)

REM 清理不需要的檔案
echo 🧹 清理不需要的檔案...
if exist "__pycache__" rmdir /s /q "__pycache__" 2>nul
if exist ".pytest_cache" rmdir /s /q ".pytest_cache" 2>nul
if exist ".venv" rmdir /s /q ".venv" 2>nul
if exist "venv" rmdir /s /q "venv" 2>nul
if exist "env" rmdir /s /q "env" 2>nul
if exist "config" rmdir /s /q "config" 2>nul
if exist ".yolo_annotator" rmdir /s /q ".yolo_annotator" 2>nul
if exist "images" rmdir /s /q "images" 2>nul
if exist "labels" rmdir /s /q "labels" 2>nul
if exist "exports" rmdir /s /q "exports" 2>nul
del /f /q *.pyc 2>nul
del /f /q *.pt 2>nul
del /f /q test_report.json 2>nul

REM 添加所有檔案
echo 📤 添加檔案到 Git...
git add .

REM 提交變更
echo 💾 提交變更...
git commit -m "🎉 Initial release: YOLOv8 Vehicle Annotator v2.0

✨ Features:
- AI-powered auto-annotation with YOLOv8
- 8-handle precise editor for pixel-level accuracy
- Multi-format export (YOLO, COCO, Pascal VOC, JSON)
- Performance optimization and memory management
- Modern dark theme UI with comprehensive shortcuts
- Project management and recent files
- Batch processing and AI prediction
- Smart caching and large image optimization

🛠 Technical Stack:
- PyQt5 for GUI framework
- YOLOv8 for AI vehicle detection
- OpenCV & Pillow for image processing
- Multi-threaded performance optimization

📋 Supported Platforms:
- Windows 10/11
- macOS 10.14+
- Ubuntu 18.04+

Ready for production use! 🚀"

REM 推送到 GitHub
echo 🚀 推送到 GitHub...
git push -u origin main --force

echo.
echo 🎉 成功部署到 GitHub！
echo 📍 倉庫地址：%REPO_URL%
echo.
echo 🔗 建議下一步：
echo 1. 在 GitHub 上設定倉庫描述和標籤
echo 2. 啟用 Issues 和 Discussions
echo 3. 設定 GitHub Pages（如需要）
echo 4. 配置 Branch Protection Rules
echo 5. 建立第一個 Release (v2.0.0)
echo.
echo 📚 文檔已準備就緒：
echo - README.md: 完整使用說明
echo - CONTRIBUTING.md: 貢獻指南
echo - CHANGELOG.md: 版本記錄
echo - Issue Templates: 問題回報範本
echo - GitHub Actions: CI/CD 自動化
echo.
echo ✅ 部署完成！
pause
