"""
自訂模型訓練對話框
提供專業的GUI界面進行模型訓練設定和監控
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox,
    QProgressBar, QTextEdit, QTabWidget, QWidget, QFormLayout,
    QGroupBox, QFileDialog, QMessageBox, QSplitter, QTableWidget,
    QTableWidgetItem, QHeaderView, QSlider, QFrame
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap, QPainter, QColor

try:
    from custom_model_trainer import TrainingConfig, DatasetPreparer, ModelTrainer, TrainingVisualizer
    TRAINER_AVAILABLE = True
except ImportError:
    TRAINER_AVAILABLE = False


class TrainingThread(QThread):
    """訓練執行緒"""
    progress_updated = pyqtSignal(int)
    log_updated = pyqtSignal(str)
    training_completed = pyqtSignal(str)  # 模型路徑
    training_failed = pyqtSignal(str)     # 錯誤訊息
    
    def __init__(self, dataset_yaml: str, config: TrainingConfig):
        super().__init__()
        self.dataset_yaml = dataset_yaml
        self.config = config
        self.trainer = ModelTrainer()
        
    def run(self):
        """執行訓練"""
        try:
            def progress_callback(progress):
                self.progress_updated.emit(progress)
            
            def log_callback(message):
                self.log_updated.emit(message)
            
            # 開始訓練
            model_path = self.trainer.train_model(
                self.dataset_yaml, 
                self.config,
                progress_callback=progress_callback,
                log_callback=log_callback
            )
            
            self.training_completed.emit(model_path)
            
        except Exception as e:
            self.training_failed.emit(str(e))


class ModelTrainingDialog(QDialog):
    """模型訓練對話框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('🤖 自訂模型訓練')
        self.setFixedSize(1000, 700)
        
        self.config = TrainingConfig()
        self.training_thread = None
        self.dataset_yaml = None
        
        self.setup_ui()
        self.setup_style()
        
    def setup_ui(self):
        """設置用戶介面"""
        layout = QVBoxLayout(self)
        
        # 標題
        title_label = QLabel('🤖 YOLOv8 自訂車輛檢測模型訓練')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # 分頁介面
        tab_widget = QTabWidget()
        
        # 資料集設定分頁
        dataset_tab = self.create_dataset_tab()
        tab_widget.addTab(dataset_tab, "📁 資料集設定")
        
        # 訓練參數分頁
        training_tab = self.create_training_tab()
        tab_widget.addTab(training_tab, "⚙️ 訓練參數")
        
        # 進階設定分頁
        advanced_tab = self.create_advanced_tab()
        tab_widget.addTab(advanced_tab, "🔧 進階設定")
        
        # 訓練監控分頁
        monitor_tab = self.create_monitor_tab()
        tab_widget.addTab(monitor_tab, "📊 訓練監控")
        
        layout.addWidget(tab_widget)
        
        # 底部控制按鈕
        button_layout = QHBoxLayout()
        
        self.prepare_btn = QPushButton('📁 準備資料集')
        self.prepare_btn.clicked.connect(self.prepare_dataset)
        button_layout.addWidget(self.prepare_btn)
        
        self.start_btn = QPushButton('🚀 開始訓練')
        self.start_btn.clicked.connect(self.start_training)
        self.start_btn.setEnabled(False)
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton('⏹️ 停止訓練')
        self.stop_btn.clicked.connect(self.stop_training)
        self.stop_btn.setEnabled(False)
        button_layout.addWidget(self.stop_btn)
        
        button_layout.addStretch()
        
        self.close_btn = QPushButton('❌ 關閉')
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    
    def create_dataset_tab(self) -> QWidget:
        """創建資料集設定分頁"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 資料集資訊
        info_group = QGroupBox("📊 資料集資訊")
        info_layout = QFormLayout(info_group)
        
        self.dataset_name_edit = QLineEdit(self.config.dataset_name)
        self.dataset_name_edit.textChanged.connect(self.update_config)
        info_layout.addRow("資料集名稱:", self.dataset_name_edit)
        
        # 資料集分割比例
        split_group = QGroupBox("✂️ 資料集分割")
        split_layout = QFormLayout(split_group)
        
        self.train_ratio_spin = QDoubleSpinBox()
        self.train_ratio_spin.setRange(0.1, 0.9)
        self.train_ratio_spin.setSingleStep(0.1)
        self.train_ratio_spin.setValue(self.config.train_ratio)
        self.train_ratio_spin.valueChanged.connect(self.update_split_ratios)
        split_layout.addRow("訓練集比例:", self.train_ratio_spin)
        
        self.val_ratio_spin = QDoubleSpinBox()
        self.val_ratio_spin.setRange(0.1, 0.9)
        self.val_ratio_spin.setSingleStep(0.1)
        self.val_ratio_spin.setValue(self.config.val_ratio)
        self.val_ratio_spin.valueChanged.connect(self.update_split_ratios)
        split_layout.addRow("驗證集比例:", self.val_ratio_spin)
        
        self.test_ratio_spin = QDoubleSpinBox()
        self.test_ratio_spin.setRange(0.1, 0.9)
        self.test_ratio_spin.setSingleStep(0.1)
        self.test_ratio_spin.setValue(self.config.test_ratio)
        self.test_ratio_spin.valueChanged.connect(self.update_split_ratios)
        split_layout.addRow("測試集比例:", self.test_ratio_spin)
        
        # 資料集統計
        self.dataset_stats_text = QTextEdit()
        self.dataset_stats_text.setReadOnly(True)
        self.dataset_stats_text.setMaximumHeight(150)
        self.dataset_stats_text.setPlainText("準備資料集後顯示統計資訊...")
        
        layout.addWidget(info_group)
        layout.addWidget(split_group)
        layout.addWidget(QLabel("📈 資料集統計:"))
        layout.addWidget(self.dataset_stats_text)
        layout.addStretch()
        
        return widget
    
    def create_training_tab(self) -> QWidget:
        """創建訓練參數分頁"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 基本訓練參數
        basic_group = QGroupBox("🎯 基本訓練參數")
        basic_layout = QFormLayout(basic_group)
        
        self.model_name_edit = QLineEdit(self.config.model_name)
        self.model_name_edit.textChanged.connect(self.update_config)
        basic_layout.addRow("模型名稱:", self.model_name_edit)
        
        self.base_model_combo = QComboBox()
        self.base_model_combo.addItems([
            "yolov8n.pt", "yolov8s.pt", "yolov8m.pt", "yolov8l.pt", "yolov8x.pt"
        ])
        self.base_model_combo.setCurrentText(self.config.base_model)
        self.base_model_combo.currentTextChanged.connect(self.update_config)
        basic_layout.addRow("基礎模型:", self.base_model_combo)
        
        self.epochs_spin = QSpinBox()
        self.epochs_spin.setRange(1, 1000)
        self.epochs_spin.setValue(self.config.epochs)
        self.epochs_spin.valueChanged.connect(self.update_config)
        basic_layout.addRow("訓練週期 (Epochs):", self.epochs_spin)
        
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(1, 128)
        self.batch_size_spin.setValue(self.config.batch_size)
        self.batch_size_spin.valueChanged.connect(self.update_config)
        basic_layout.addRow("批次大小 (Batch Size):", self.batch_size_spin)
        
        self.image_size_combo = QComboBox()
        self.image_size_combo.addItems(["320", "416", "512", "640", "768", "896", "1024"])
        self.image_size_combo.setCurrentText(str(self.config.image_size))
        self.image_size_combo.currentTextChanged.connect(self.update_config)
        basic_layout.addRow("圖片尺寸:", self.image_size_combo)
        
        # 優化器參數
        optimizer_group = QGroupBox("🔧 優化器參數")
        optimizer_layout = QFormLayout(optimizer_group)
        
        self.learning_rate_spin = QDoubleSpinBox()
        self.learning_rate_spin.setRange(0.0001, 1.0)
        self.learning_rate_spin.setDecimals(4)
        self.learning_rate_spin.setSingleStep(0.001)
        self.learning_rate_spin.setValue(self.config.learning_rate)
        self.learning_rate_spin.valueChanged.connect(self.update_config)
        optimizer_layout.addRow("學習率:", self.learning_rate_spin)
        
        self.optimizer_combo = QComboBox()
        self.optimizer_combo.addItems(["AdamW", "Adam", "SGD", "RMSprop"])
        self.optimizer_combo.setCurrentText(self.config.optimizer)
        self.optimizer_combo.currentTextChanged.connect(self.update_config)
        optimizer_layout.addRow("優化器:", self.optimizer_combo)
        
        self.weight_decay_spin = QDoubleSpinBox()
        self.weight_decay_spin.setRange(0.0, 0.01)
        self.weight_decay_spin.setDecimals(4)
        self.weight_decay_spin.setSingleStep(0.0001)
        self.weight_decay_spin.setValue(self.config.weight_decay)
        self.weight_decay_spin.valueChanged.connect(self.update_config)
        optimizer_layout.addRow("權重衰減:", self.weight_decay_spin)
        
        layout.addWidget(basic_group)
        layout.addWidget(optimizer_group)
        layout.addStretch()
        
        return widget
    
    def create_advanced_tab(self) -> QWidget:
        """創建進階設定分頁"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 數據增強
        augmentation_group = QGroupBox("🎨 數據增強")
        augmentation_layout = QFormLayout(augmentation_group)
        
        self.augmentation_cb = QCheckBox()
        self.augmentation_cb.setChecked(self.config.augmentation)
        self.augmentation_cb.stateChanged.connect(self.update_config)
        augmentation_layout.addRow("啟用數據增強:", self.augmentation_cb)
        
        self.mixup_spin = QDoubleSpinBox()
        self.mixup_spin.setRange(0.0, 1.0)
        self.mixup_spin.setDecimals(2)
        self.mixup_spin.setSingleStep(0.1)
        self.mixup_spin.setValue(self.config.mixup)
        self.mixup_spin.valueChanged.connect(self.update_config)
        augmentation_layout.addRow("Mixup 強度:", self.mixup_spin)
        
        self.copy_paste_spin = QDoubleSpinBox()
        self.copy_paste_spin.setRange(0.0, 1.0)
        self.copy_paste_spin.setDecimals(2)
        self.copy_paste_spin.setSingleStep(0.1)
        self.copy_paste_spin.setValue(self.config.copy_paste)
        self.copy_paste_spin.valueChanged.connect(self.update_config)
        augmentation_layout.addRow("Copy-Paste 強度:", self.copy_paste_spin)
        
        # 硬體設定
        hardware_group = QGroupBox("💻 硬體設定")
        hardware_layout = QFormLayout(hardware_group)
        
        self.device_combo = QComboBox()
        self.device_combo.addItems(["auto", "cpu", "cuda", "mps"])
        self.device_combo.setCurrentText(self.config.device)
        self.device_combo.currentTextChanged.connect(self.update_config)
        hardware_layout.addRow("運算設備:", self.device_combo)
        
        self.workers_spin = QSpinBox()
        self.workers_spin.setRange(0, 32)
        self.workers_spin.setValue(self.config.workers)
        self.workers_spin.valueChanged.connect(self.update_config)
        hardware_layout.addRow("資料載入執行緒:", self.workers_spin)
        
        # 訓練控制
        control_group = QGroupBox("🎮 訓練控制")
        control_layout = QFormLayout(control_group)
        
        self.patience_spin = QSpinBox()
        self.patience_spin.setRange(5, 200)
        self.patience_spin.setValue(self.config.patience)
        self.patience_spin.valueChanged.connect(self.update_config)
        control_layout.addRow("早停耐心值:", self.patience_spin)
        
        self.save_period_spin = QSpinBox()
        self.save_period_spin.setRange(1, 100)
        self.save_period_spin.setValue(self.config.save_period)
        self.save_period_spin.valueChanged.connect(self.update_config)
        control_layout.addRow("儲存週期:", self.save_period_spin)
        
        layout.addWidget(augmentation_group)
        layout.addWidget(hardware_group)
        layout.addWidget(control_group)
        layout.addStretch()
        
        return widget
    
    def create_monitor_tab(self) -> QWidget:
        """創建訓練監控分頁"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 進度顯示
        progress_group = QGroupBox("📊 訓練進度")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("等待開始訓練...")
        self.status_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.status_label)
        
        # 訓練日誌
        log_group = QGroupBox("📝 訓練日誌")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 12px;
            }
        """)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(progress_group)
        layout.addWidget(log_group)
        
        return widget
    
    def setup_style(self):
        """設置樣式"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
                color: #2c3e50;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin: 8px 0px;
                padding-top: 12px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 16px;
                padding: 4px 8px;
                background-color: white;
                border-radius: 4px;
            }
            
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 120px;
            }
            
            QPushButton:hover {
                background-color: #2980b9;
            }
            
            QPushButton:pressed {
                background-color: #21618c;
            }
            
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
    
    def update_config(self):
        """更新訓練配置"""
        self.config.model_name = self.model_name_edit.text()
        self.config.dataset_name = self.dataset_name_edit.text()
        self.config.base_model = self.base_model_combo.currentText()
        self.config.epochs = self.epochs_spin.value()
        self.config.batch_size = self.batch_size_spin.value()
        self.config.image_size = int(self.image_size_combo.currentText())
        self.config.learning_rate = self.learning_rate_spin.value()
        self.config.optimizer = self.optimizer_combo.currentText()
        self.config.weight_decay = self.weight_decay_spin.value()
        self.config.augmentation = self.augmentation_cb.isChecked()
        self.config.mixup = self.mixup_spin.value()
        self.config.copy_paste = self.copy_paste_spin.value()
        self.config.device = self.device_combo.currentText()
        self.config.workers = self.workers_spin.value()
        self.config.patience = self.patience_spin.value()
        self.config.save_period = self.save_period_spin.value()
    
    def update_split_ratios(self):
        """更新資料集分割比例"""
        train_ratio = self.train_ratio_spin.value()
        val_ratio = self.val_ratio_spin.value()
        test_ratio = self.test_ratio_spin.value()
        
        total = train_ratio + val_ratio + test_ratio
        if abs(total - 1.0) > 0.01:
            # 自動調整比例
            train_ratio = train_ratio / total
            val_ratio = val_ratio / total
            test_ratio = test_ratio / total
            
            self.train_ratio_spin.blockSignals(True)
            self.val_ratio_spin.blockSignals(True)
            self.test_ratio_spin.blockSignals(True)
            
            self.train_ratio_spin.setValue(train_ratio)
            self.val_ratio_spin.setValue(val_ratio)
            self.test_ratio_spin.setValue(test_ratio)
            
            self.train_ratio_spin.blockSignals(False)
            self.val_ratio_spin.blockSignals(False)
            self.test_ratio_spin.blockSignals(False)
        
        self.config.train_ratio = train_ratio
        self.config.val_ratio = val_ratio
        self.config.test_ratio = test_ratio
    
    def prepare_dataset(self):
        """準備資料集"""
        if not TRAINER_AVAILABLE:
            QMessageBox.critical(
                self, "功能不可用",
                "訓練模組未正確載入，請檢查 ultralytics 是否已安裝。"
            )
            return
        
        try:
            self.prepare_btn.setEnabled(False)
            self.status_label.setText("正在準備資料集...")
            
            # 創建資料集準備器
            preparer = DatasetPreparer(source_dir=".", output_dir="datasets")
            
            # 更新配置
            self.update_config()
            
            # 準備資料集
            self.dataset_yaml = preparer.prepare_yolo_dataset(self.config)
            
            # 載入統計資訊
            self.load_dataset_statistics()
            
            self.start_btn.setEnabled(True)
            self.status_label.setText("資料集準備完成，可以開始訓練")
            
            QMessageBox.information(
                self, "資料集準備完成",
                f"資料集已成功準備！\n配置檔案：{self.dataset_yaml}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, "資料集準備失敗",
                f"準備資料集時發生錯誤：\n{str(e)}"
            )
        finally:
            self.prepare_btn.setEnabled(True)
    
    def load_dataset_statistics(self):
        """載入資料集統計資訊"""
        if not self.dataset_yaml:
            return
        
        dataset_dir = Path(self.dataset_yaml).parent
        stats_file = dataset_dir / "dataset_statistics.json"
        
        if stats_file.exists():
            try:
                with open(stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
                
                stats_text = "📊 資料集統計資訊:\n\n"
                
                for split, data in stats['splits'].items():
                    stats_text += f"{split.upper()}:\n"
                    stats_text += f"  圖片: {data['images']} 張\n"
                    stats_text += f"  標註: {data['annotations']} 個\n"
                    
                    if data['class_distribution']:
                        stats_text += f"  類別分布: {data['class_distribution']}\n"
                    
                    stats_text += "\n"
                
                self.dataset_stats_text.setPlainText(stats_text)
                
            except Exception as e:
                self.dataset_stats_text.setPlainText(f"載入統計資訊失敗：{e}")
    
    def start_training(self):
        """開始訓練"""
        if not self.dataset_yaml:
            QMessageBox.warning(self, "未準備資料集", "請先準備資料集")
            return
        
        # 確認對話框
        reply = QMessageBox.question(
            self, "確認開始訓練",
            f"即將開始訓練模型 '{self.config.model_name}':\n\n"
            f"• 基礎模型: {self.config.base_model}\n"
            f"• 訓練週期: {self.config.epochs}\n"
            f"• 批次大小: {self.config.batch_size}\n"
            f"• 圖片尺寸: {self.config.image_size}\n\n"
            f"訓練可能需要很長時間，確定要開始嗎？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # 開始訓練
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.prepare_btn.setEnabled(False)
        
        # 清空日誌
        self.log_text.clear()
        self.progress_bar.setValue(0)
        
        # 更新配置
        self.update_config()
        
        # 創建訓練執行緒
        self.training_thread = TrainingThread(self.dataset_yaml, self.config)
        self.training_thread.progress_updated.connect(self.update_progress)
        self.training_thread.log_updated.connect(self.update_log)
        self.training_thread.training_completed.connect(self.on_training_completed)
        self.training_thread.training_failed.connect(self.on_training_failed)
        
        # 開始訓練
        self.training_thread.start()
        
        self.status_label.setText("訓練進行中...")
        self.log_text.append("🚀 開始模型訓練...")
    
    def stop_training(self):
        """停止訓練"""
        if self.training_thread and self.training_thread.isRunning():
            reply = QMessageBox.question(
                self, "確認停止訓練",
                "確定要停止訓練嗎？未完成的訓練進度將會丟失。",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.training_thread.terminate()
                self.training_thread.wait()
                
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
                self.prepare_btn.setEnabled(True)
                
                self.status_label.setText("訓練已停止")
                self.log_text.append("⏹️ 訓練已被用戶停止")
    
    def update_progress(self, progress: int):
        """更新進度"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(f"訓練進度: {progress}%")
    
    def update_log(self, message: str):
        """更新日誌"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # 自動滾動到最後
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.End)
        self.log_text.setTextCursor(cursor)
    
    def on_training_completed(self, model_path: str):
        """訓練完成"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.prepare_btn.setEnabled(True)
        
        self.progress_bar.setValue(100)
        self.status_label.setText("訓練完成！")
        
        QMessageBox.information(
            self, "訓練完成",
            f"🎉 模型訓練成功完成！\n\n"
            f"模型已儲存至：{model_path}\n\n"
            f"您現在可以在主程式中使用這個自訂模型進行車輛檢測。"
        )
    
    def on_training_failed(self, error_message: str):
        """訓練失敗"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.prepare_btn.setEnabled(True)
        
        self.status_label.setText("訓練失敗")
        
        QMessageBox.critical(
            self, "訓練失敗",
            f"❌ 模型訓練失敗：\n\n{error_message}"
        )


# 測試程式
if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    dialog = ModelTrainingDialog()
    dialog.show()
    
    sys.exit(app.exec_())
