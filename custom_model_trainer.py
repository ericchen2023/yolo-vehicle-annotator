"""
自訂模型訓練器 - YOLOv8 專用車輛檢測模型訓練
基於用戶標註資料訓練專門的車輛檢測模型
支援資料集分割、訓練監控、    # 硬體設定
    device: str = "cpu"  # auto, cpu, cuda
    workers: int = 4估等專業功能
"""

import os
import sys
import yaml
import json
import shutil
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image

try:
    from ultralytics import YOLO
    import torch
    from ultralytics.utils import LOGGER
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False
    print("警告：ultralytics 未安裝，模型訓練功能不可用")

try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    print("警告：matplotlib/seaborn 未安裝，部分視覺化功能不可用")


@dataclass
class TrainingConfig:
    """訓練配置參數"""
    # 基本設定
    model_name: str = "custom_vehicle_model"
    base_model: str = "yolov8n.pt"  # 基礎模型
    
    # 資料集設定
    dataset_name: str = "vehicle_dataset"
    train_ratio: float = 0.7
    val_ratio: float = 0.2
    test_ratio: float = 0.1
    
    # 訓練參數
    epochs: int = 100
    batch_size: int = 16
    image_size: int = 640
    learning_rate: float = 0.01
    
    # 優化參數
    optimizer: str = "AdamW"
    weight_decay: float = 0.0005
    momentum: float = 0.937
    
    # 數據增強
    augmentation: bool = True
    mixup: float = 0.1
    copy_paste: float = 0.3
    
    # 硬體設定
    device: str = "auto"  # auto, cpu, cuda
    workers: int = 8
    
    # 進階設定
    patience: int = 50  # 早停耐心值
    save_period: int = 10  # 儲存週期
    resume: bool = False  # 是否恢復訓練
    
    def to_dict(self) -> Dict:
        """轉換為字典"""
        return {
            'model_name': self.model_name,
            'base_model': self.base_model,
            'dataset_name': self.dataset_name,
            'train_ratio': self.train_ratio,
            'val_ratio': self.val_ratio,
            'test_ratio': self.test_ratio,
            'epochs': self.epochs,
            'batch_size': self.batch_size,
            'image_size': self.image_size,
            'learning_rate': self.learning_rate,
            'optimizer': self.optimizer,
            'weight_decay': self.weight_decay,
            'momentum': self.momentum,
            'augmentation': self.augmentation,
            'mixup': self.mixup,
            'copy_paste': self.copy_paste,
            'device': self.device,
            'workers': self.workers,
            'patience': self.patience,
            'save_period': self.save_period,
            'resume': self.resume
        }

    def get_optimal_device(self) -> str:
        """自動檢測最佳訓練設備"""
        if not ULTRALYTICS_AVAILABLE:
            return "cpu"
        
        try:
            import torch
            if torch.cuda.is_available() and torch.cuda.device_count() > 0:
                device = f"cuda:{torch.cuda.current_device()}"
                print(f"🚀 使用 GPU 訓練：{device}")
                return device
            else:
                print("💻 使用 CPU 訓練（未檢測到可用的 GPU）")
                return "cpu"
        except Exception as e:
            print(f"⚠️ 設備檢測失敗，使用 CPU：{e}")
            return "cpu"


class DatasetPreparer:
    """資料集準備器"""
    
    def __init__(self, source_dir: str, output_dir: str):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        
    def prepare_yolo_dataset(self, config: TrainingConfig, 
                           progress_callback: Optional[Callable] = None) -> str:
        """準備YOLO格式的訓練資料集"""
        
        print("🔄 準備訓練資料集...")
        
        # 創建資料集目錄結構
        dataset_path = self.output_dir / config.dataset_name
        self._create_dataset_structure(dataset_path)
        
        # 收集圖片和標註檔案
        image_files, label_files = self._collect_files()
        
        if not image_files:
            raise ValueError("未找到任何圖片檔案")
        
        print(f"找到 {len(image_files)} 張圖片")
        
        # 分割資料集
        train_files, val_files, test_files = self._split_dataset(
            image_files, config.train_ratio, config.val_ratio, config.test_ratio
        )
        
        print(f"資料集分割: 訓練={len(train_files)}, 驗證={len(val_files)}, 測試={len(test_files)}")
        
        # 複製檔案到對應目錄
        total_files = len(train_files) + len(val_files) + len(test_files)
        processed = 0
        
        for split_name, file_list in [("train", train_files), ("val", val_files), ("test", test_files)]:
            for img_file in file_list:
                # 複製圖片
                img_dst = dataset_path / "images" / split_name / img_file.name
                shutil.copy2(img_file, img_dst)
                
                # 複製標註檔案
                label_file = self._find_label_file(img_file, label_files)
                if label_file:
                    label_dst = dataset_path / "labels" / split_name / f"{img_file.stem}.txt"
                    shutil.copy2(label_file, label_dst)
                
                processed += 1
                if progress_callback:
                    progress_callback(int(processed / total_files * 100))
        
        # 創建資料集配置檔案
        self._create_dataset_yaml(dataset_path, config)
        
        # 生成統計報告
        self._generate_dataset_statistics(dataset_path)
        
        print(f"✅ 資料集準備完成：{dataset_path}")
        return str(dataset_path / "dataset.yaml")
    
    def _create_dataset_structure(self, dataset_path: Path):
        """創建資料集目錄結構"""
        for split in ["train", "val", "test"]:
            (dataset_path / "images" / split).mkdir(parents=True, exist_ok=True)
            (dataset_path / "labels" / split).mkdir(parents=True, exist_ok=True)
    
    def _collect_files(self) -> Tuple[List[Path], List[Path]]:
        """收集圖片和標註檔案"""
        # 支援的圖片格式
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
        
        image_files = []
        label_files = []
        
        # 從多個可能的來源收集檔案
        search_paths = [
            self.source_dir,
            self.source_dir / "images",
            Path("images"),
            Path("exports") / "yolo",
            Path("labels")
        ]
        
        for search_path in search_paths:
            if search_path.exists():
                # 收集圖片檔案
                for ext in image_extensions:
                    image_files.extend(search_path.glob(f"*{ext}"))
                
                # 收集標註檔案
                label_files.extend(search_path.glob("*.txt"))
        
        # 去除重複
        image_files = list(set(image_files))
        label_files = list(set(label_files))
        
        return image_files, label_files
    
    def _find_label_file(self, image_file: Path, label_files: List[Path]) -> Optional[Path]:
        """為圖片檔案找到對應的標註檔案"""
        image_stem = image_file.stem
        
        for label_file in label_files:
            if label_file.stem == image_stem:
                return label_file
        
        return None
    
    def _split_dataset(self, files: List[Path], train_ratio: float, 
                      val_ratio: float, test_ratio: float) -> Tuple[List[Path], List[Path], List[Path]]:
        """分割資料集"""
        # 檢查比例
        total_ratio = train_ratio + val_ratio + test_ratio
        if abs(total_ratio - 1.0) > 0.01:
            raise ValueError(f"資料集比例總和應為1.0，當前為{total_ratio}")
        
        # 隨機打亂
        files = files.copy()
        random.shuffle(files)
        
        total_files = len(files)
        train_count = int(total_files * train_ratio)
        val_count = int(total_files * val_ratio)
        
        train_files = files[:train_count]
        val_files = files[train_count:train_count + val_count]
        test_files = files[train_count + val_count:]
        
        return train_files, val_files, test_files
    
    def _create_dataset_yaml(self, dataset_path: Path, config: TrainingConfig):
        """創建資料集YAML配置檔案"""
        
        # 載入車種類別
        classes = self._load_vehicle_classes()
        
        yaml_content = {
            'path': str(dataset_path.absolute()),
            'train': 'images/train',
            'val': 'images/val',
            'test': 'images/test',
            'nc': len(classes),
            'names': {i: name for i, name in enumerate(classes)}
        }
        
        yaml_file = dataset_path / "dataset.yaml"
        with open(yaml_file, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_content, f, default_flow_style=False, allow_unicode=True)
        
        print(f"📄 資料集配置檔案：{yaml_file}")
        print(f"🏷️ 車種類別 ({len(classes)}): {', '.join(classes)}")
    
    def _load_vehicle_classes(self) -> List[str]:
        """載入車種類別"""
        # 嘗試從 vehicle_classes.json 載入
        try:
            from vehicle_class_manager import VehicleClassManager
            manager = VehicleClassManager()
            classes = manager.get_all_classes(enabled_only=True)
            return [cls.name for cls in classes]
        except:
            pass
        
        # 備用：從 classes.txt 載入
        classes_files = [
            Path("classes.txt"),
            Path("exports/yolo/classes.txt"),
            self.source_dir / "classes.txt"
        ]
        
        for classes_file in classes_files:
            if classes_file.exists():
                with open(classes_file, 'r', encoding='utf-8') as f:
                    return [line.strip() for line in f if line.strip()]
        
        # 預設類別
        return ["機車", "汽車", "卡車", "公車"]
    
    def _generate_dataset_statistics(self, dataset_path: Path):
        """生成資料集統計資訊"""
        stats = {
            'created_at': datetime.now().isoformat(),
            'dataset_path': str(dataset_path),
            'splits': {}
        }
        
        for split in ["train", "val", "test"]:
            images_dir = dataset_path / "images" / split
            labels_dir = dataset_path / "labels" / split
            
            image_count = len(list(images_dir.glob("*")))
            label_count = len(list(labels_dir.glob("*.txt")))
            
            # 統計標註數量
            total_annotations = 0
            class_counts = {}
            
            for label_file in labels_dir.glob("*.txt"):
                with open(label_file, 'r') as f:
                    lines = f.readlines()
                    total_annotations += len(lines)
                    
                    for line in lines:
                        parts = line.strip().split()
                        if parts:
                            class_id = int(parts[0])
                            class_counts[class_id] = class_counts.get(class_id, 0) + 1
            
            stats['splits'][split] = {
                'images': image_count,
                'labels': label_count,
                'annotations': total_annotations,
                'class_distribution': class_counts
            }
        
        # 儲存統計資訊
        stats_file = dataset_path / "dataset_statistics.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"📊 資料集統計：{stats_file}")


class ModelTrainer:
    """模型訓練器"""
    
    def __init__(self, output_dir: str = "training_runs"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.current_run_dir = None
        self.model = None
        self.training_config = None
        
    def train_model(self, dataset_yaml: str, config: TrainingConfig,
                   progress_callback: Optional[Callable] = None,
                   log_callback: Optional[Callable] = None) -> str:
        """訓練自訂模型"""
        
        if not ULTRALYTICS_AVAILABLE:
            raise RuntimeError("ultralytics 未安裝，無法進行模型訓練")
        
        print("🚀 開始模型訓練...")
        
        # 創建訓練執行目錄
        self.current_run_dir = self._create_run_directory(config.model_name)
        
        # 儲存訓練配置
        self._save_training_config(config)
        
        # 初始化模型
        model_path = self._download_base_model(config.base_model)
        self.model = YOLO(model_path)
        
        # 設定訓練參數
        train_args = self._prepare_training_args(dataset_yaml, config)
        
        # 設定回調函數
        if progress_callback or log_callback:
            self._setup_callbacks(progress_callback, log_callback)
        
        try:
            # 開始訓練
            print(f"📚 載入資料集：{dataset_yaml}")
            print(f"🎯 訓練參數：{config.epochs} epochs, batch_size={config.batch_size}")
            
            results = self.model.train(**train_args)
            
            # 儲存最終模型
            final_model_path = self._save_final_model(config.model_name)
            
            # 生成訓練報告
            self._generate_training_report(results, config)
            
            print(f"✅ 訓練完成！模型儲存於：{final_model_path}")
            return final_model_path
            
        except Exception as e:
            print(f"❌ 訓練失敗：{str(e)}")
            raise
    
    def evaluate_model(self, model_path: str, dataset_yaml: str) -> Dict:
        """評估模型效能"""
        
        print("📊 評估模型效能...")
        
        if not ULTRALYTICS_AVAILABLE:
            raise RuntimeError("ultralytics 未安裝，無法進行模型評估")
        
        # 載入模型
        model = YOLO(model_path)
        
        # 在驗證集上評估
        results = model.val(data=dataset_yaml, split='val', save=True)
        
        # 提取評估指標
        metrics = {
            'mAP50': float(results.box.map50),
            'mAP50-95': float(results.box.map),
            'precision': float(results.box.mp),
            'recall': float(results.box.mr),
            'f1_score': 2 * (float(results.box.mp) * float(results.box.mr)) / 
                       (float(results.box.mp) + float(results.box.mr) + 1e-16)
        }
        
        # 按類別的詳細指標
        if hasattr(results.box, 'ap_class_index') and hasattr(results.box, 'ap'):
            class_metrics = {}
            for i, class_idx in enumerate(results.box.ap_class_index):
                class_metrics[int(class_idx)] = {
                    'ap50': float(results.box.ap50[i]),
                    'ap': float(results.box.ap[i])
                }
            metrics['class_metrics'] = class_metrics
        
        print(f"📈 評估結果：mAP50={metrics['mAP50']:.3f}, mAP50-95={metrics['mAP50-95']:.3f}")
        
        return metrics
    
    def _create_run_directory(self, model_name: str) -> Path:
        """創建訓練執行目錄"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_name = f"{model_name}_{timestamp}"
        run_dir = self.output_dir / run_name
        run_dir.mkdir(exist_ok=True)
        
        print(f"📁 訓練目錄：{run_dir}")
        return run_dir
    
    def _save_training_config(self, config: TrainingConfig):
        """儲存訓練配置"""
        config_file = self.current_run_dir / "training_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config.to_dict(), f, indent=2, ensure_ascii=False)
    
    def _download_base_model(self, base_model: str) -> str:
        """下載基礎模型"""
        print(f"📥 準備基礎模型：{base_model}")
        
        # 如果是本地檔案，直接返回路徑
        if os.path.exists(base_model):
            return base_model
        
        # 下載預訓練模型
        try:
            model = YOLO(base_model)
            return base_model
        except Exception as e:
            print(f"下載基礎模型失敗：{e}")
            # 備用模型
            fallback_models = ["yolov8n.pt", "yolov8s.pt", "yolov8m.pt"]
            for fallback in fallback_models:
                try:
                    model = YOLO(fallback)
                    print(f"使用備用模型：{fallback}")
                    return fallback
                except:
                    continue
            
            raise RuntimeError("無法下載任何基礎模型")
    
    def _prepare_training_args(self, dataset_yaml: str, config: TrainingConfig) -> Dict:
        """準備訓練參數"""
        # 自動檢測最佳設備
        optimal_device = config.get_optimal_device()
        
        args = {
            'data': dataset_yaml,
            'epochs': config.epochs,
            'batch': config.batch_size,
            'imgsz': config.image_size,
            'lr0': config.learning_rate,
            'optimizer': config.optimizer,
            'weight_decay': config.weight_decay,
            'momentum': config.momentum,
            'device': optimal_device,  # 使用自動檢測的設備
            'workers': config.workers,
            'patience': config.patience,
            'save_period': config.save_period,
            'project': str(self.output_dir),
            'name': self.current_run_dir.name,
            'exist_ok': True,
            'save': True,
            'plots': True,
            'val': True
        }
        
        # 數據增強設定
        if config.augmentation:
            args.update({
                'mixup': config.mixup,
                'copy_paste': config.copy_paste,
                'degrees': 0.0,  # 旋轉角度
                'translate': 0.1,  # 平移
                'scale': 0.5,  # 縮放
                'shear': 0.0,  # 剪切
                'perspective': 0.0,  # 透視
                'flipud': 0.0,  # 垂直翻轉
                'fliplr': 0.5,  # 水平翻轉
                'mosaic': 1.0,  # 馬賽克增強
                'hsv_h': 0.015,  # 色調
                'hsv_s': 0.7,  # 飽和度
                'hsv_v': 0.4  # 亮度
            })
        
        return args
    
    def _setup_callbacks(self, progress_callback: Optional[Callable], 
                        log_callback: Optional[Callable]):
        """設定回調函數"""
        
        def on_train_epoch_end(trainer):
            """訓練epoch結束回調"""
            if progress_callback:
                progress = int((trainer.epoch + 1) / trainer.epochs * 100)
                progress_callback(progress)
            
            if log_callback:
                metrics = trainer.metrics if hasattr(trainer, 'metrics') else {}
                log_message = f"Epoch {trainer.epoch + 1}/{trainer.epochs}"
                if metrics:
                    # 確保 loss 是數值類型
                    loss_value = metrics.get('loss', 'N/A')
                    if isinstance(loss_value, (int, float)):
                        log_message += f" - Loss: {loss_value:.4f}"
                    else:
                        log_message += f" - Loss: {loss_value}"
                log_callback(log_message)
        
        # 註冊回調
        if hasattr(self.model, 'add_callback'):
            self.model.add_callback('on_train_epoch_end', on_train_epoch_end)
    
    def _save_final_model(self, model_name: str) -> str:
        """儲存最終模型"""
        # 找到最佳權重
        weights_dir = self.current_run_dir / "weights"
        best_weights = weights_dir / "best.pt"
        last_weights = weights_dir / "last.pt"
        
        # 選擇最佳權重檔案
        if best_weights.exists():
            source_weights = best_weights
        elif last_weights.exists():
            source_weights = last_weights
        else:
            raise FileNotFoundError("找不到訓練後的權重檔案")
        
        # 複製到專案根目錄
        final_model_path = f"{model_name}.pt"
        shutil.copy2(source_weights, final_model_path)
        
        return final_model_path
    
    def _generate_training_report(self, results, config: TrainingConfig):
        """生成訓練報告"""
        report = {
            'training_completed_at': datetime.now().isoformat(),
            'model_name': config.model_name,
            'base_model': config.base_model,
            'training_config': config.to_dict(),
            'final_metrics': {},
            'training_duration': None
        }
        
        # 提取最終指標
        if hasattr(results, 'metrics'):
            report['final_metrics'] = results.metrics
        
        # 儲存報告
        report_file = self.current_run_dir / "training_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📋 訓練報告：{report_file}")


class TrainingVisualizer:
    """訓練視覺化工具"""
    
    def __init__(self, run_dir: str):
        self.run_dir = Path(run_dir)
        
    def plot_training_curves(self, save_path: Optional[str] = None):
        """繪製訓練曲線"""
        if not PLOTTING_AVAILABLE:
            print("matplotlib 未安裝，無法生成訓練曲線")
            return
        
        # 讀取訓練結果
        results_csv = self.run_dir / "results.csv"
        if not results_csv.exists():
            print("找不到訓練結果檔案")
            return
        
        import pandas as pd
        
        # 讀取資料
        df = pd.read_csv(results_csv)
        df.columns = df.columns.str.strip()  # 清理欄位名稱
        
        # 創建圖表
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('YOLOv8 Training Results', fontsize=16)
        
        # Loss 曲線
        axes[0, 0].plot(df['epoch'], df['train/box_loss'], label='Box Loss', linewidth=2)
        axes[0, 0].plot(df['epoch'], df['train/cls_loss'], label='Class Loss', linewidth=2)
        axes[0, 0].plot(df['epoch'], df['train/dfl_loss'], label='DFL Loss', linewidth=2)
        axes[0, 0].set_title('Training Losses')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Loss')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # mAP 曲線
        if 'metrics/mAP50(B)' in df.columns:
            axes[0, 1].plot(df['epoch'], df['metrics/mAP50(B)'], label='mAP@0.5', linewidth=2, color='green')
            axes[0, 1].plot(df['epoch'], df['metrics/mAP50-95(B)'], label='mAP@0.5:0.95', linewidth=2, color='blue')
            axes[0, 1].set_title('Validation mAP')
            axes[0, 1].set_xlabel('Epoch')
            axes[0, 1].set_ylabel('mAP')
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3)
        
        # Precision & Recall
        if 'metrics/precision(B)' in df.columns:
            axes[1, 0].plot(df['epoch'], df['metrics/precision(B)'], label='Precision', linewidth=2, color='red')
            axes[1, 0].plot(df['epoch'], df['metrics/recall(B)'], label='Recall', linewidth=2, color='orange')
            axes[1, 0].set_title('Precision & Recall')
            axes[1, 0].set_xlabel('Epoch')
            axes[1, 0].set_ylabel('Score')
            axes[1, 0].legend()
            axes[1, 0].grid(True, alpha=0.3)
        
        # Learning Rate
        if 'lr/pg0' in df.columns:
            axes[1, 1].plot(df['epoch'], df['lr/pg0'], label='Learning Rate', linewidth=2, color='purple')
            axes[1, 1].set_title('Learning Rate Schedule')
            axes[1, 1].set_xlabel('Epoch')
            axes[1, 1].set_ylabel('Learning Rate')
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 儲存圖表
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 訓練曲線已儲存：{save_path}")
        else:
            plt.savefig(self.run_dir / "training_curves.png", dpi=300, bbox_inches='tight')
            print(f"📊 訓練曲線：{self.run_dir / 'training_curves.png'}")
        
        plt.close()
    
    def plot_confusion_matrix(self, class_names: List[str], save_path: Optional[str] = None):
        """繪製混淆矩陣"""
        if not PLOTTING_AVAILABLE:
            print("matplotlib 未安裝，無法生成混淆矩陣")
            return
        
        # 查找混淆矩陣檔案
        confusion_matrix_file = self.run_dir / "confusion_matrix_normalized.png"
        
        if confusion_matrix_file.exists():
            print(f"📈 混淆矩陣：{confusion_matrix_file}")
        else:
            print("找不到混淆矩陣檔案")


# 使用範例
if __name__ == "__main__":
    # 檢查依賴
    if not ULTRALYTICS_AVAILABLE:
        print("❌ 請先安裝 ultralytics：pip install ultralytics")
        sys.exit(1)
    
    # 訓練配置
    config = TrainingConfig(
        model_name="custom_vehicle_detector",
        base_model="yolov8n.pt",
        epochs=50,
        batch_size=8,
        image_size=640
    )
    
    print("🚗 自訂車輛檢測模型訓練")
    print("=" * 50)
    
    try:
        # 準備資料集
        preparer = DatasetPreparer(source_dir=".", output_dir="datasets")
        dataset_yaml = preparer.prepare_yolo_dataset(config)
        
        # 訓練模型
        trainer = ModelTrainer(output_dir="training_runs")
        model_path = trainer.train_model(dataset_yaml, config)
        
        # 評估模型
        metrics = trainer.evaluate_model(model_path, dataset_yaml)
        print(f"📊 最終評估結果：{metrics}")
        
        # 生成視覺化
        visualizer = TrainingVisualizer(trainer.current_run_dir)
        visualizer.plot_training_curves()
        
        print("✅ 自訂模型訓練完成！")
        
    except Exception as e:
        print(f"❌ 訓練失敗：{e}")
        import traceback
        traceback.print_exc()
