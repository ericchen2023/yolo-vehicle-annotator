"""
AI預測結果對話框 - 顯示和管理AI預測結果
"""

import os
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QCheckBox, QGroupBox,
    QProgressBar, QTextEdit, QSplitter, QWidget, QScrollArea,
    QFrame, QButtonGroup, QRadioButton
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPen, QColor, QBrush

class PredictionResultDialog(QDialog):
    """AI預測結果對話框"""
    
    predictions_accepted = pyqtSignal(list)  # 接受的預測
    predictions_rejected = pyqtSignal(list)  # 拒絕的預測
    
    def __init__(self, image_path, predictions, image_pixmap=None, parent=None):
        super().__init__(parent)
        self.image_path = image_path
        self.predictions = predictions
        self.image_pixmap = image_pixmap
        self.accepted_predictions = []
        self.rejected_predictions = []
        
        # 如果沒有提供image_pixmap，嘗試載入圖片
        if self.image_pixmap is None and os.path.exists(self.image_path):
            try:
                self.image_pixmap = QPixmap(self.image_path)
                if self.image_pixmap.isNull():
                    self.image_pixmap = None
                    print(f"警告: 無法載入圖片 {self.image_path}")
            except Exception as e:
                self.image_pixmap = None
                print(f"載入圖片失敗: {e}")
        
        self.setWindowTitle(f'AI預測結果 - {os.path.basename(image_path)}')
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        self.setup_ui()
        self.load_predictions()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 標題資訊
        title_layout = QHBoxLayout()
        
        title_label = QLabel(f'圖片: {os.path.basename(self.image_path)}')
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_layout.addWidget(title_label)
        
        title_layout.addStretch()
        
        count_label = QLabel(f'找到 {len(self.predictions)} 個車輛')
        count_label.setStyleSheet('color: #0078d4;')
        title_layout.addWidget(count_label)
        
        layout.addLayout(title_layout)
        
        # 主要分割器
        main_splitter = QSplitter(Qt.Horizontal)
        
        # 左側：圖片預覽
        left_panel = self.create_image_preview_panel()
        main_splitter.addWidget(left_panel)
        
        # 右側：預測列表
        right_panel = self.create_predictions_panel()
        main_splitter.addWidget(right_panel)
        
        main_splitter.setSizes([500, 400])
        layout.addWidget(main_splitter)
        
        # 統計資訊
        stats_layout = QHBoxLayout()
        
        self.stats_label = QLabel('統計: 0 接受, 0 拒絕')
        stats_layout.addWidget(self.stats_label)
        
        stats_layout.addStretch()
        
        # 批次操作按鈕
        batch_accept_btn = QPushButton('全部接受')
        batch_accept_btn.clicked.connect(self.accept_all_predictions)
        stats_layout.addWidget(batch_accept_btn)
        
        batch_reject_btn = QPushButton('全部拒絕')
        batch_reject_btn.clicked.connect(self.reject_all_predictions)
        stats_layout.addWidget(batch_reject_btn)
        
        layout.addLayout(stats_layout)
        
        # 底部按鈕
        button_layout = QHBoxLayout()
        
        help_btn = QPushButton('說明')
        help_btn.clicked.connect(self.show_help)
        button_layout.addWidget(help_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        apply_btn = QPushButton('套用選擇')
        apply_btn.clicked.connect(self.apply_selections)
        apply_btn.setDefault(True)
        button_layout.addWidget(apply_btn)
        
        layout.addLayout(button_layout)

    def create_image_preview_panel(self):
        """創建圖片預覽面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 預覽標題
        preview_label = QLabel('預覽圖片')
        preview_font = QFont()
        preview_font.setBold(True)
        preview_label.setFont(preview_font)
        layout.addWidget(preview_label)
        
        # 顯示選項 (先創建checkbox)
        options_group = QGroupBox('顯示選項')
        options_layout = QVBoxLayout(options_group)
        
        self.show_accepted_cb = QCheckBox('顯示已接受的預測')
        self.show_accepted_cb.setChecked(True)
        self.show_accepted_cb.toggled.connect(self.update_image_preview)
        options_layout.addWidget(self.show_accepted_cb)
        
        self.show_rejected_cb = QCheckBox('顯示已拒絕的預測')
        self.show_rejected_cb.setChecked(True)
        self.show_rejected_cb.toggled.connect(self.update_image_preview)
        options_layout.addWidget(self.show_rejected_cb)
        
        self.show_confidence_cb = QCheckBox('顯示信心度')
        self.show_confidence_cb.setChecked(True)
        self.show_confidence_cb.toggled.connect(self.update_image_preview)
        options_layout.addWidget(self.show_confidence_cb)
        
        layout.addWidget(options_group)
        
        # 圖片顯示區域
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            QLabel {
                border: 2px solid #3e3e42;
                border-radius: 4px;
                background-color: #252526;
            }
        """)
        self.image_label.setMinimumSize(400, 300)
        
        # 如果有圖片，顯示預覽 (現在checkbox已經創建了)
        if self.image_pixmap and not self.image_pixmap.isNull():
            self.update_image_preview()
        else:
            # 嘗試直接載入圖片檔案作為備用
            if os.path.exists(self.image_path):
                try:
                    backup_pixmap = QPixmap(self.image_path)
                    if not backup_pixmap.isNull():
                        self.image_pixmap = backup_pixmap
                        self.update_image_preview()
                    else:
                        self.image_label.setText(f'無法載入圖片預覽\n{os.path.basename(self.image_path)}')
                except Exception as e:
                    self.image_label.setText(f'圖片載入失敗\n{os.path.basename(self.image_path)}\n{str(e)}')
            else:
                self.image_label.setText(f'圖片檔案不存在\n{os.path.basename(self.image_path)}')
        
        layout.addWidget(self.image_label)
        
        return panel

    def create_predictions_panel(self):
        """創建預測列表面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 列表標題
        list_label = QLabel('AI預測結果')
        list_font = QFont()
        list_font.setBold(True)
        list_label.setFont(list_font)
        layout.addWidget(list_label)
        
        # 預測列表
        self.predictions_list = QListWidget()
        self.predictions_list.currentItemChanged.connect(self.on_prediction_selected)
        layout.addWidget(self.predictions_list)
        
        # 詳細資訊
        details_group = QGroupBox('預測詳細資訊')
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(120)
        details_layout.addWidget(self.details_text)
        
        layout.addWidget(details_group)
        
        return panel

    def load_predictions(self):
        """載入預測到列表"""
        self.predictions_list.clear()
        
        for i, pred in enumerate(self.predictions):
            item = QListWidgetItem()
            
            # 創建自訂widget
            widget = self.create_prediction_item_widget(i, pred)
            item.setSizeHint(widget.sizeHint())
            
            self.predictions_list.addItem(item)
            self.predictions_list.setItemWidget(item, widget)
        
        self.update_stats()

    def create_prediction_item_widget(self, index, prediction):
        """創建預測項目widget"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 選擇按鈕組
        button_group = QButtonGroup(widget)
        
        accept_rb = QRadioButton('接受')
        accept_rb.setChecked(True)  # 預設接受
        accept_rb.toggled.connect(lambda checked, idx=index: self.on_prediction_decision(idx, 'accept', checked))
        button_group.addButton(accept_rb)
        layout.addWidget(accept_rb)
        
        reject_rb = QRadioButton('拒絕')
        reject_rb.toggled.connect(lambda checked, idx=index: self.on_prediction_decision(idx, 'reject', checked))
        button_group.addButton(reject_rb)
        layout.addWidget(reject_rb)
        
        # 分隔線
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # 預測資訊
        info_layout = QVBoxLayout()
        
        # 第一行：類別和信心度
        class_conf_layout = QHBoxLayout()
        
        class_label = QLabel(f"🚗 {prediction['class_name']}")
        class_label.setStyleSheet('font-weight: bold; color: #0078d4;')
        class_conf_layout.addWidget(class_label)
        
        class_conf_layout.addStretch()
        
        confidence = prediction.get('confidence', 0)
        conf_label = QLabel(f"{confidence:.2%}")
        conf_color = self.get_confidence_color(confidence)
        conf_label.setStyleSheet(f'color: {conf_color}; font-weight: bold;')
        class_conf_layout.addWidget(conf_label)
        
        info_layout.addLayout(class_conf_layout)
        
        # 第二行：位置資訊
        bbox = prediction['bbox']
        pos_label = QLabel(f"位置: ({bbox[0]}, {bbox[1]}) 大小: {bbox[2]}×{bbox[3]}")
        pos_label.setStyleSheet('color: #888888; font-size: 11px;')
        info_layout.addWidget(pos_label)
        
        # 第三行：額外資訊
        extra_info = []
        if prediction.get('optimized', False):
            extra_info.append('🔧 已優化')
        if prediction.get('source') == 'ai_prediction':
            extra_info.append('🤖 AI預測')
        
        if extra_info:
            extra_label = QLabel(' | '.join(extra_info))
            extra_label.setStyleSheet('color: #0078d4; font-size: 10px;')
            info_layout.addWidget(extra_label)
        
        layout.addLayout(info_layout)
        
        # 儲存決策狀態
        widget.prediction_index = index
        widget.accept_button = accept_rb
        widget.reject_button = reject_rb
        
        return widget

    def get_confidence_color(self, confidence):
        """根據信心度獲取顏色"""
        if confidence >= 0.8:
            return '#4CAF50'  # 綠色
        elif confidence >= 0.6:
            return '#FF9800'  # 橙色
        else:
            return '#F44336'  # 紅色

    def on_prediction_decision(self, index, decision, checked):
        """處理預測決策"""
        if not checked:
            return
            
        prediction = self.predictions[index]
        
        if decision == 'accept':
            if prediction in self.rejected_predictions:
                self.rejected_predictions.remove(prediction)
            if prediction not in self.accepted_predictions:
                self.accepted_predictions.append(prediction)
        else:  # reject
            if prediction in self.accepted_predictions:
                self.accepted_predictions.remove(prediction)
            if prediction not in self.rejected_predictions:
                self.rejected_predictions.append(prediction)
        
        self.update_stats()
        self.update_image_preview()

    def on_prediction_selected(self, current, previous):
        """處理預測選擇"""
        if current is None:
            return
            
        # 獲取對應的預測
        row = self.predictions_list.row(current)
        if 0 <= row < len(self.predictions):
            prediction = self.predictions[row]
            self.show_prediction_details(prediction)

    def show_prediction_details(self, prediction):
        """顯示預測詳細資訊"""
        details = []
        details.append(f"車輛類別: {prediction['class_name']}")
        details.append(f"信心度: {prediction.get('confidence', 0):.2%}")
        details.append(f"邊界框: {prediction['bbox']}")
        
        if prediction.get('optimized'):
            details.append("狀態: 已使用邊緣檢測優化")
        
        if 'original_yolo_class' in prediction:
            details.append(f"原始YOLO類別: {prediction['original_yolo_class']}")
        
        details.append(f"來源: {prediction.get('source', 'unknown')}")
        
        self.details_text.setPlainText('\n'.join(details))

    def update_image_preview(self):
        """更新圖片預覽"""
        if not self.image_pixmap:
            return
            
        # 複製原圖
        preview_pixmap = self.image_pixmap.copy()
        painter = QPainter(preview_pixmap)
        
        # 繪製預測框
        for pred in self.predictions:
            should_draw = False
            color = QColor(255, 255, 255)
            
            if pred in self.accepted_predictions and self.show_accepted_cb.isChecked():
                should_draw = True
                color = QColor(76, 175, 80)  # 綠色
            elif pred in self.rejected_predictions and self.show_rejected_cb.isChecked():
                should_draw = True
                color = QColor(244, 67, 54)  # 紅色
            elif (pred not in self.accepted_predictions and 
                  pred not in self.rejected_predictions and 
                  self.show_accepted_cb.isChecked()):  # 預設是接受
                should_draw = True
                color = QColor(33, 150, 243)  # 藍色
            
            if should_draw:
                self.draw_prediction_box(painter, pred, color)
        
        painter.end()
        
        # 縮放圖片以適應顯示區域
        label_size = self.image_label.size()
        scaled_pixmap = preview_pixmap.scaled(
            label_size.width() - 10, 
            label_size.height() - 10,
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        self.image_label.setPixmap(scaled_pixmap)

    def draw_prediction_box(self, painter, prediction, color):
        """繪製預測框"""
        bbox = prediction['bbox']
        x, y, w, h = bbox
        
        # 設定畫筆
        pen = QPen(color, 3)
        painter.setPen(pen)
        
        # 繪製矩形
        painter.drawRect(x, y, w, h)
        
        # 繪製標籤
        if self.show_confidence_cb.isChecked():
            confidence = prediction.get('confidence', 0)
            label_text = f"{prediction['class_name']} {confidence:.1%}"
        else:
            label_text = prediction['class_name']
        
        # 標籤背景
        font_metrics = painter.fontMetrics()
        text_width = font_metrics.horizontalAdvance(label_text)
        text_height = font_metrics.height()
        
        label_rect = painter.boundingRect(x, y - text_height - 5, text_width + 10, text_height + 5, Qt.AlignLeft, label_text)
        painter.fillRect(label_rect, QBrush(color))
        
        # 標籤文字
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.drawText(label_rect, Qt.AlignCenter, label_text)

    def update_stats(self):
        """更新統計資訊"""
        accepted_count = len(self.accepted_predictions)
        rejected_count = len(self.rejected_predictions)
        pending_count = len(self.predictions) - accepted_count - rejected_count
        
        # 預設未決定的都算作接受
        total_accepted = accepted_count + pending_count
        
        self.stats_label.setText(f'統計: {total_accepted} 接受, {rejected_count} 拒絕')

    def accept_all_predictions(self):
        """接受所有預測"""
        self.accepted_predictions = self.predictions.copy()
        self.rejected_predictions.clear()
        
        # 更新UI
        for i in range(self.predictions_list.count()):
            item = self.predictions_list.item(i)
            widget = self.predictions_list.itemWidget(item)
            if widget:
                widget.accept_button.setChecked(True)
        
        self.update_stats()
        self.update_image_preview()

    def reject_all_predictions(self):
        """拒絕所有預測"""
        self.rejected_predictions = self.predictions.copy()
        self.accepted_predictions.clear()
        
        # 更新UI
        for i in range(self.predictions_list.count()):
            item = self.predictions_list.item(i)
            widget = self.predictions_list.itemWidget(item)
            if widget:
                widget.reject_button.setChecked(True)
        
        self.update_stats()
        self.update_image_preview()

    def show_help(self):
        """顯示說明"""
        help_text = """
AI預測結果說明：

🟢 綠色框: 已接受的預測
🔴 紅色框: 已拒絕的預測  
🔵 藍色框: 待決定的預測 (預設接受)

操作說明：
• 點選每個預測的「接受」或「拒絕」選項
• 使用「全部接受」或「全部拒絕」快速操作
• 勾選顯示選項控制預覽圖中顯示的內容
• 點選預測項目查看詳細資訊

信心度顏色：
🟢 >= 80%: 高信心度
🟠 60-80%: 中等信心度  
🔴 < 60%: 低信心度

提示：
• 建議仔細檢查低信心度的預測
• 已優化的預測框可能更準確
        """
        
        from PyQt5.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setWindowTitle('說明')
        msg.setText(help_text)
        msg.setIcon(QMessageBox.Information)
        msg.exec_()

    def apply_selections(self):
        """套用選擇"""
        # 處理未決定的預測 (預設為接受)
        final_accepted = []
        final_rejected = []
        
        for pred in self.predictions:
            if pred in self.rejected_predictions:
                final_rejected.append(pred)
            else:
                # 未明確拒絕的都當作接受
                final_accepted.append(pred)
        
        # 發送信號
        if final_accepted:
            self.predictions_accepted.emit(final_accepted)
        if final_rejected:
            self.predictions_rejected.emit(final_rejected)
        
        self.accept()
