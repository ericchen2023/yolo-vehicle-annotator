#!/bin/bash

# YOLOv8 Vehicle Annotator - GitHub 部署腳本
# 使用說明：./deploy_to_github.sh [repository-url]

set -e  # 遇到錯誤時停止

echo "🚗 YOLOv8 Vehicle Annotator - GitHub 部署腳本"
echo "=============================================="

# 檢查是否在正確的目錄
if [ ! -f "main.py" ]; then
    echo "❌ 錯誤：請在專案根目錄執行此腳本"
    exit 1
fi

# 檢查 git 是否已安裝
if ! command -v git &> /dev/null; then
    echo "❌ 錯誤：Git 未安裝，請先安裝 Git"
    exit 1
fi

# 獲取倉庫 URL
REPO_URL=""
if [ "$1" != "" ]; then
    REPO_URL="$1"
else
    echo "📝 請輸入您的 GitHub 倉庫 URL (例如: https://github.com/ericchen2023/yolo-vehicle-annotator.git):"
    read -r REPO_URL
fi

if [ "$REPO_URL" = "" ]; then
    echo "❌ 錯誤：倉庫 URL 不能為空"
    exit 1
fi

echo "🔄 準備部署到：$REPO_URL"

# 初始化 Git 倉庫（如果還沒有的話）
if [ ! -d ".git" ]; then
    echo "📦 初始化 Git 倉庫..."
    git init
    git branch -M main
fi

# 添加遠端倉庫
echo "🔗 設定遠端倉庫..."
git remote remove origin 2>/dev/null || true
git remote add origin "$REPO_URL"

# 檢查並創建必要檔案
echo "📋 檢查專案檔案..."

# 檢查重要檔案是否存在
files_to_check=("README.md" "LICENSE" "requirements.txt" ".gitignore" "CONTRIBUTING.md" "CHANGELOG.md")
for file in "${files_to_check[@]}"; do
    if [ ! -f "$file" ]; then
        echo "⚠️  警告：$file 檔案不存在"
    else
        echo "✅ $file"
    fi
done

# 清理不需要的檔案
echo "🧹 清理不需要的檔案..."
rm -rf __pycache__/ .pytest_cache/ *.pyc .coverage htmlcov/
rm -rf .venv/ venv/ env/
rm -rf *.pt models/ 2>/dev/null || true
rm -rf images/ labels/ exports/ test_output/ 2>/dev/null || true
rm -rf config/ .yolo_annotator/ 2>/dev/null || true

# 添加所有檔案
echo "📤 添加檔案到 Git..."
git add .

# 檢查是否有變更
if git diff --cached --quiet; then
    echo "ℹ️  沒有檔案變更，跳過提交"
else
    # 提交變更
    echo "💾 提交變更..."
    COMMIT_MSG="🎉 Initial release: YOLOv8 Vehicle Annotator v2.0

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

    git commit -m "$COMMIT_MSG"
fi

# 推送到 GitHub
echo "🚀 推送到 GitHub..."
git push -u origin main --force

echo ""
echo "🎉 成功部署到 GitHub！"
echo "📍 倉庫地址：$REPO_URL"
echo ""
echo "🔗 建議下一步："
echo "1. 在 GitHub 上設定倉庫描述和標籤"
echo "2. 啟用 Issues 和 Discussions"
echo "3. 設定 GitHub Pages（如需要）"
echo "4. 配置 Branch Protection Rules"
echo "5. 建立第一個 Release (v2.0.0)"
echo ""
echo "📚 文檔已準備就緒："
echo "- README.md: 完整使用說明"
echo "- CONTRIBUTING.md: 貢獻指南"
echo "- CHANGELOG.md: 版本記錄"
echo "- Issue Templates: 問題回報範本"
echo "- GitHub Actions: CI/CD 自動化"
echo ""
echo "✅ 部署完成！"
