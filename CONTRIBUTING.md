# Contributing to YOLOv8 車輛標註工具

我們歡迎社群貢獻！請閱讀以下指南來了解如何參與專案開發。

## 📋 貢獻方式

### 🐛 回報問題
- 使用 [Issue Templates](https://github.com/ericchen2023/yolo-vehicle-annotator/issues/new/choose)
- 提供詳細的問題描述和重現步驟
- 附上系統資訊和錯誤日誌

### 💡 功能建議
- 在提交功能請求前，請先搜尋現有的 Issues
- 詳細說明功能用途和預期行為
- 考慮功能的實用性和複雜度

### 🔧 程式碼貢獻

#### 開發環境設定
```bash
# 1. Fork 專案並克隆到本地
git clone https://github.com/ericchen2023/yolo-vehicle-annotator.git
cd yolo-vehicle-annotator

# 2. 建立虛擬環境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate     # Windows

# 3. 安裝開發依賴
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. 執行測試確認環境
python test_features.py
```

#### 開發流程
1. **建立分支**：`git checkout -b feature/your-feature-name`
2. **開發功能**：遵循程式碼風格指南
3. **撰寫測試**：確保新功能有對應測試
4. **執行測試**：`python -m pytest tests/`
5. **提交變更**：使用清晰的提交訊息
6. **建立 PR**：詳細描述變更內容

## 📝 程式碼風格

### Python 風格指南
- 遵循 [PEP 8](https://peps.python.org/pep-0008/) 標準
- 使用 4 個空格縮進
- 行長度限制為 88 字元
- 使用有意義的變數和函數名稱

### 註解風格
```python
def process_image(image_path: str, annotations: List[Dict]) -> bool:
    """
    處理圖片並套用標註
    
    Args:
        image_path: 圖片檔案路徑
        annotations: 標註資料清單
        
    Returns:
        bool: 處理是否成功
        
    Raises:
        FileNotFoundError: 當圖片檔案不存在時
        ValueError: 當標註格式無效時
    """
    pass
```

### 提交訊息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

類型說明：
- `feat`: 新功能
- `fix`: 錯誤修復
- `docs`: 文檔更新
- `style`: 程式碼格式調整
- `refactor`: 程式碼重構
- `test`: 測試相關
- `chore`: 維護工作

範例：
```
feat(ai): add batch prediction with progress tracking

- Implement multi-threaded batch processing
- Add progress bar and cancellation support
- Optimize memory usage for large datasets

Closes #123
```

## 🧪 測試指南

### 執行測試
```bash
# 執行所有測試
python test_features.py

# 執行特定模組測試
python -m pytest tests/test_annotator.py

# 執行覆蓋率測試
coverage run -m pytest
coverage report
```

### 測試撰寫
- 為新功能撰寫單元測試
- 測試檔案命名：`test_<module_name>.py`
- 使用有意義的測試名稱
- 包含正常情況和邊界情況測試

範例：
```python
def test_annotator_create_bbox():
    """測試標註器建立邊界框功能"""
    annotator = AnnotatorLabel()
    rect = annotator.create_bbox(100, 100, 200, 200, class_id=1)
    
    assert rect['class_id'] == 1
    assert rect['bbox'] == [100, 100, 200, 200]
    assert 'id' in rect
```

## 📦 發佈流程

### 版本號規則
遵循 [Semantic Versioning](https://semver.org/)：
- `MAJOR.MINOR.PATCH`
- `MAJOR`: 不相容的 API 變更
- `MINOR`: 向後相容的功能新增
- `PATCH`: 向後相容的錯誤修復

### 發佈檢查清單
- [ ] 所有測試通過
- [ ] 更新版本號
- [ ] 更新 CHANGELOG.md
- [ ] 更新 README.md
- [ ] 建立 Release Tag
- [ ] 發佈 Release Notes

## 🔍 程式碼審查

### 提交 Pull Request
1. **清晰標題**：簡潔描述變更內容
2. **詳細描述**：解釋變更原因和實作方式
3. **關聯 Issue**：使用 `Closes #issue-number`
4. **截圖/影片**：如果是 UI 變更，請附上視覺證明
5. **測試證明**：說明如何測試變更

### PR 模板
```markdown
## 變更摘要
簡述這個 PR 的主要變更

## 變更類型
- [ ] 錯誤修復
- [ ] 新功能
- [ ] 重大變更
- [ ] 文檔更新

## 測試
- [ ] 已撰寫/更新單元測試
- [ ] 已執行所有測試且通過
- [ ] 已手動測試功能

## 檢查清單
- [ ] 程式碼遵循專案風格指南
- [ ] 已更新相關文檔
- [ ] 變更向後相容
```

## 🎯 開發優先順序

### 高優先級
- 錯誤修復和安全性問題
- 效能優化
- 使用者體驗改善

### 中優先級  
- 新功能開發
- API 改進
- 文檔完善

### 低優先級
- 程式碼重構
- 工具改進
- 實驗性功能

## 🤝 社群行為準則

### 我們的承諾
- 營造開放且友善的環境
- 尊重不同觀點和經驗
- 接受建設性批評
- 專注於對社群最有利的事情

### 預期行為
- 使用友善和包容的語言
- 尊重不同的觀點和經驗
- 優雅地接受建設性批評
- 專注於對社群最有利的事情
- 對其他社群成員表現同理心

### 不當行為
- 使用性化語言或圖像
- 人身攻擊或政治攻擊
- 公開或私人騷擾
- 未經許可發布他人私人資訊
- 其他在專業環境中不當的行為

## 📞 聯絡方式

- **一般問題**: 建立 [GitHub Issue](https://github.com/ericchen2023/yolo-vehicle-annotator/issues)
- **安全問題**: 發送郵件至 ericchen20050329@gmail.com
- **功能討論**: 使用 [GitHub Discussions](https://github.com/ericchen2023/yolo-vehicle-annotator/discussions)

## 📄 授權

提交貢獻即表示您同意將您的貢獻授權於與專案相同的 [MIT License](LICENSE) 條款下。

---

感謝您對 YOLOv8 車輛標註工具的貢獻！🚗✨
