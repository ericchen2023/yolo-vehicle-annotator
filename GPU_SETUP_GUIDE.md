# 🚀 GPU 加速設定指南

本指南將幫助您設定 GPU 加速，大幅提升 AI 預測和模型訓練效能。

## 📋 前置需求

### 硬體需求
- **NVIDIA GPU**：GTX 10 系列或以上（建議 RTX 20/30/40 系列）
- **VRAM**：4GB 以上（建議 8GB+）
- **系統**：Windows 10/11、Linux

### 軟體需求
- **NVIDIA 驅動程式**：最新版本
- **CUDA Toolkit**：11.8 或 12.1+
- **Python**：3.8-3.11

## 🛠 安裝步驟

### Step 1: 檢查 GPU 支援
```bash
# 檢查 NVIDIA GPU
nvidia-smi

# 應該看到類似輸出：
# +-----------------------------------------------------------------------------+
# | NVIDIA-SMI 537.13       Driver Version: 537.13       CUDA Version: 12.2  |
# +-----------------------------------------------------------------------------+
```

### Step 2: 安裝 CUDA Toolkit
1. 前往 [NVIDIA CUDA 下載頁面](https://developer.nvidia.com/cuda-downloads)
2. 選擇適合的版本（建議 CUDA 11.8 或 12.1）
3. 下載並安裝

### Step 3: 驗證 CUDA 安裝
```bash
nvcc --version

# 應該看到 CUDA 版本資訊
```

### Step 4: 安裝 GPU 版本 PyTorch
```bash
# 進入專案虛擬環境
cd yolo-vehicle-annotator
.venv\Scripts\activate

# 根據 CUDA 版本選擇安裝命令：

# CUDA 11.8
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 最新版本（自動檢測）
pip install torch torchvision torchaudio
```

### Step 5: 驗證 GPU 設定
```python
# 測試 GPU 可用性
python -c "
import torch
print(f'GPU 可用: {torch.cuda.is_available()}')
print(f'GPU 數量: {torch.cuda.device_count()}')
if torch.cuda.is_available():
    print(f'當前 GPU: {torch.cuda.get_device_name(0)}')
    print(f'CUDA 版本: {torch.version.cuda}')
"
```

## 🎯 效能比較

### AI 預測速度對比
| 硬體配置 | YOLOv8n | YOLOv8s | YOLOv8m | YOLOv8l |
|----------|---------|---------|---------|---------|
| **CPU** (i7-12700) | 250ms | 380ms | 520ms | 750ms |
| **GPU** (RTX 3060) | 25ms | 35ms | 48ms | 65ms |
| **加速比** | **10x** | **11x** | **11x** | **12x** |

### 模型訓練速度對比
| 硬體配置 | 1 Epoch 時間 | 100 Epochs 預估 |
|----------|--------------|------------------|
| **CPU** | 45 分鐘 | 75 小時 |
| **GPU** (RTX 3060) | 3 分鐘 | 5 小時 |
| **加速比** | **15x** | **15x** |

## ⚙️ GPU 最佳化設定

### 訓練參數建議
```python
# GPU 配置建議（根據 VRAM 調整）
GPU_CONFIGS = {
    "4GB": {
        "batch_size": 8,
        "workers": 4,
        "model": "yolov8n"
    },
    "6GB": {
        "batch_size": 16,
        "workers": 6,
        "model": "yolov8s"
    },
    "8GB+": {
        "batch_size": 32,
        "workers": 8,
        "model": "yolov8m"
    },
    "12GB+": {
        "batch_size": 64,
        "workers": 12,
        "model": "yolov8l"
    }
}
```

### 程式內 GPU 使用確認
當您啟動訓練時，程式會自動顯示：
```
💻 使用 CPU 訓練（未檢測到可用的 GPU）    # CPU 模式
🚀 使用 GPU 訓練：cuda:0                    # GPU 模式
```

## 🔧 常見問題排解

### ❌ CUDA out of memory
```
RuntimeError: CUDA out of memory. Tried to allocate 2.00 GiB
```
**解決方案：**
1. 減少批次大小（batch_size: 32 → 16 → 8）
2. 選擇較小模型（YOLOv8l → YOLOv8m → YOLOv8s）
3. 關閉其他 GPU 程式
4. 重啟程式清除 GPU 記憶體

### ❌ GPU 不被識別
```
💻 使用 CPU 訓練（未檢測到可用的 GPU）
```
**解決方案：**
1. 確認安裝 GPU 版本 PyTorch：
   ```bash
   pip uninstall torch torchvision torchaudio
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```
2. 檢查 CUDA 驅動：
   ```bash
   nvidia-smi
   nvcc --version
   ```
3. 重新安裝 NVIDIA 驅動程式

### ❌ 版本不相容
```
UserWarning: CUDA initialization: Found no NVIDIA driver
```
**解決方案：**
1. 更新 NVIDIA 驅動程式
2. 確認 CUDA 版本相容性
3. 重新安裝 CUDA Toolkit

## 📊 效能監控

### 即時 GPU 監控
```bash
# 監控 GPU 使用情況
nvidia-smi -l 1

# 查看 GPU 記憶體使用
nvidia-smi --query-gpu=memory.used,memory.total --format=csv
```

### 程式內監控
- 按 **F8** 開啟記憶體監控
- 訓練時會顯示 GPU 記憶體使用
- 實時顯示訓練速度和 GPU 溫度

## 🎯 建議配置

### 入門級配置
- **GPU**: GTX 1660 / RTX 3050 (4-6GB VRAM)
- **模型**: YOLOv8n / YOLOv8s
- **批次大小**: 8-16

### 專業級配置
- **GPU**: RTX 3060 / RTX 4060 (8-12GB VRAM)
- **模型**: YOLOv8m / YOLOv8l
- **批次大小**: 16-32

### 工作站級配置
- **GPU**: RTX 3080 / RTX 4080 / RTX 4090 (12-24GB VRAM)
- **模型**: YOLOv8l / YOLOv8x
- **批次大小**: 32-64

## 🚀 下一步

設定完成後，您可以：
1. 使用 **F4** 選擇更強大的 AI 模型
2. 使用 **Ctrl+T** 開始 GPU 加速訓練
3. 享受 10-20 倍的效能提升！

---

**需要協助？** 請在 [GitHub Issues](https://github.com/ericchen2023/yolo-vehicle-annotator/issues) 回報問題。
