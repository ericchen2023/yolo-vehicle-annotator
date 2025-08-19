"""
車種類別管理器
提供自定義車種功能，包括新增、編輯、刪除車種類別
"""

import json
import os
from typing import List, Dict, Tuple, Optional
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QLineEdit, QColorDialog,
    QInputDialog, QMessageBox, QGroupBox, QFormLayout,
    QSpinBox, QCheckBox, QTextEdit, QTabWidget, QWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox,
    QDialogButtonBox, QFrame, QSplitter, QFileDialog, QApplication
)
from PyQt5.QtGui import QColor, QPixmap, QPainter, QIcon
from PyQt5.QtCore import Qt, pyqtSignal


# 導入樣式表
try:
    from styles import get_main_style
    STYLE_AVAILABLE = True
except ImportError:
    STYLE_AVAILABLE = False
    print("樣式表模組不可用，使用預設樣式")


class VehicleClass:
    """車種類別資料結構"""
    
    def __init__(self, class_id: int, name: str, color: QColor = None, 
                 description: str = "", enabled: bool = True, 
                 shortcut_key: str = "", emoji: str = "🚗"):
        self.class_id = class_id
        self.name = name
        self.color = color or self._get_default_color(class_id)
        self.description = description
        self.enabled = enabled
        self.shortcut_key = shortcut_key
        self.emoji = emoji
    
    def _get_default_color(self, class_id: int) -> QColor:
        """根據 ID 生成預設顏色"""
        default_colors = [
            QColor(255, 75, 75),    # 紅色
            QColor(75, 255, 75),    # 綠色
            QColor(75, 150, 255),   # 藍色
            QColor(255, 215, 0),    # 金黃色
            QColor(255, 165, 0),    # 橙色
            QColor(147, 112, 219),  # 紫色
            QColor(255, 192, 203),  # 粉紅色
            QColor(0, 255, 255),    # 青色
            QColor(255, 255, 0),    # 黃色
            QColor(255, 20, 147),   # 深粉紅
        ]
        return default_colors[class_id % len(default_colors)]
    
    def to_dict(self) -> Dict:
        """轉換為字典格式"""
        return {
            'class_id': self.class_id,
            'name': self.name,
            'color': {
                'r': self.color.red(),
                'g': self.color.green(),
                'b': self.color.blue(),
                'a': self.color.alpha()
            },
            'description': self.description,
            'enabled': self.enabled,
            'shortcut_key': self.shortcut_key,
            'emoji': self.emoji
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'VehicleClass':
        """從字典創建物件"""
        color_data = data.get('color', {})
        color = QColor(
            color_data.get('r', 255),
            color_data.get('g', 75),
            color_data.get('b', 75),
            color_data.get('a', 255)
        )
        
        return cls(
            class_id=data['class_id'],
            name=data['name'],
            color=color,
            description=data.get('description', ''),
            enabled=data.get('enabled', True),
            shortcut_key=data.get('shortcut_key', ''),
            emoji=data.get('emoji', '🚗')
        )


class VehicleClassManager:
    """車種類別管理器"""
    
    def __init__(self, config_file: str = "vehicle_classes.json"):
        self.config_file = config_file
        self.classes = {}  # {class_id: VehicleClass}
        self.next_id = 0
        self.load_classes()
    
    def load_classes(self):
        """載入車種類別配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.classes = {}
                for class_data in data.get('classes', []):
                    vehicle_class = VehicleClass.from_dict(class_data)
                    self.classes[vehicle_class.class_id] = vehicle_class
                
                self.next_id = data.get('next_id', len(self.classes))
                
            except Exception as e:
                print(f"載入車種配置失敗: {e}")
                self._load_default_classes()
        else:
            self._load_default_classes()
        
        # 確保 next_id 正確
        if self.classes:
            self.next_id = max(self.classes.keys()) + 1
    
    def _load_default_classes(self):
        """載入預設車種類別"""
        default_classes = [
            {'name': '機車', 'emoji': '🏍', 'shortcut_key': '1', 'description': '兩輪機車'},
            {'name': '汽車', 'emoji': '🚗', 'shortcut_key': '2', 'description': '一般乘用車'},
            {'name': '卡車', 'emoji': '🚛', 'shortcut_key': '3', 'description': '貨運卡車'},
            {'name': '公車', 'emoji': '🚌', 'shortcut_key': '4', 'description': '公共交通巴士'},
        ]
        
        self.classes = {}
        for i, cls_data in enumerate(default_classes):
            vehicle_class = VehicleClass(
                class_id=i,
                name=cls_data['name'],
                emoji=cls_data['emoji'],
                shortcut_key=cls_data['shortcut_key'],
                description=cls_data['description']
            )
            self.classes[i] = vehicle_class
        
        self.next_id = len(default_classes)
        self.save_classes()
    
    def save_classes(self):
        """儲存車種類別配置"""
        try:
            data = {
                'classes': [cls.to_dict() for cls in self.classes.values()],
                'next_id': self.next_id,
                'version': '1.0'
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"儲存車種配置失敗: {e}")
            raise
    
    def add_class(self, name: str, color: QColor = None, description: str = "", 
                  shortcut_key: str = "", emoji: str = "🚗") -> int:
        """新增車種類別"""
        if not name.strip():
            raise ValueError("車種名稱不能為空")
        
        # 檢查名稱是否重複
        for cls in self.classes.values():
            if cls.name == name:
                raise ValueError(f"車種名稱 '{name}' 已存在")
        
        # 檢查快捷鍵是否重複
        if shortcut_key:
            for cls in self.classes.values():
                if cls.shortcut_key == shortcut_key:
                    raise ValueError(f"快捷鍵 '{shortcut_key}' 已被使用")
        
        class_id = self.next_id
        vehicle_class = VehicleClass(
            class_id=class_id,
            name=name,
            color=color,
            description=description,
            shortcut_key=shortcut_key,
            emoji=emoji
        )
        
        self.classes[class_id] = vehicle_class
        self.next_id += 1
        self.save_classes()
        
        return class_id
    
    def update_class(self, class_id: int, name: str = None, color: QColor = None,
                     description: str = None, enabled: bool = None,
                     shortcut_key: str = None, emoji: str = None):
        """更新車種類別"""
        if class_id not in self.classes:
            raise ValueError(f"車種 ID {class_id} 不存在")
        
        vehicle_class = self.classes[class_id]
        
        if name is not None:
            if not name.strip():
                raise ValueError("車種名稱不能為空")
            # 檢查名稱是否與其他類別重複
            for cid, cls in self.classes.items():
                if cid != class_id and cls.name == name:
                    raise ValueError(f"車種名稱 '{name}' 已存在")
            vehicle_class.name = name
        
        if color is not None:
            vehicle_class.color = color
        
        if description is not None:
            vehicle_class.description = description
        
        if enabled is not None:
            vehicle_class.enabled = enabled
        
        if shortcut_key is not None:
            # 檢查快捷鍵是否與其他類別重複
            if shortcut_key:
                for cid, cls in self.classes.items():
                    if cid != class_id and cls.shortcut_key == shortcut_key:
                        raise ValueError(f"快捷鍵 '{shortcut_key}' 已被使用")
            vehicle_class.shortcut_key = shortcut_key
        
        if emoji is not None:
            vehicle_class.emoji = emoji
        
        self.save_classes()
    
    def delete_class(self, class_id: int):
        """刪除車種類別"""
        if class_id not in self.classes:
            raise ValueError(f"車種 ID {class_id} 不存在")
        
        del self.classes[class_id]
        self.save_classes()
    
    def get_class(self, class_id: int) -> Optional[VehicleClass]:
        """取得車種類別"""
        return self.classes.get(class_id)
    
    def get_all_classes(self, enabled_only: bool = False) -> List[VehicleClass]:
        """取得所有車種類別"""
        classes = list(self.classes.values())
        if enabled_only:
            classes = [cls for cls in classes if cls.enabled]
        return sorted(classes, key=lambda x: x.class_id)
    
    def get_class_by_name(self, name: str) -> Optional[VehicleClass]:
        """根據名稱取得車種類別"""
        for cls in self.classes.values():
            if cls.name == name:
                return cls
        return None
    
    def get_classes_for_combo(self, enabled_only: bool = True) -> List[Tuple[str, int]]:
        """取得適用於下拉選單的車種清單"""
        classes = self.get_all_classes(enabled_only)
        return [(cls.name, cls.class_id) for cls in classes]
    
    def get_class_colors(self) -> Dict[int, QColor]:
        """取得所有車種的顏色映射"""
        return {class_id: cls.color for class_id, cls in self.classes.items()}
    
    def export_classes_txt(self, filename: str = "classes.txt"):
        """匯出車種清單到文字檔案（YOLO格式）"""
        try:
            classes = self.get_all_classes(enabled_only=True)
            with open(filename, 'w', encoding='utf-8') as f:
                for cls in classes:
                    f.write(f"{cls.name}\n")
            return True
        except Exception as e:
            print(f"匯出車種清單失敗: {e}")
            return False
    
    def import_classes_txt(self, filename: str) -> bool:
        """從文字檔案匯入車種清單"""
        try:
            if not os.path.exists(filename):
                return False
            
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 清除現有類別
            self.classes = {}
            self.next_id = 0
            
            # 導入新類別
            for i, line in enumerate(lines):
                name = line.strip()
                if name:
                    # 生成預設表情符號
                    emoji_map = {
                        '機車': '🏍', '摩托車': '🏍',
                        '汽車': '🚗', '小客車': '🚗', '轎車': '🚗',
                        '卡車': '🚛', '貨車': '🚛', '載貨車': '🚛',
                        '公車': '🚌', '巴士': '🚌', '客運': '🚌',
                        '計程車': '🚕', '的士': '🚕',
                        '警車': '🚓',
                        '救護車': '🚑',
                        '消防車': '🚒',
                        '腳踏車': '🚲', '自行車': '🚲',
                        '三輪車': '🛺'
                    }
                    emoji = emoji_map.get(name, '🚗')
                    
                    vehicle_class = VehicleClass(
                        class_id=i,
                        name=name,
                        emoji=emoji,
                        shortcut_key=str(i+1) if i < 9 else ""
                    )
                    self.classes[i] = vehicle_class
            
            self.next_id = len(self.classes)
            self.save_classes()
            return True
            
        except Exception as e:
            print(f"匯入車種清單失敗: {e}")
            return False


class VehicleClassManagerDialog(QDialog):
    """車種管理對話框"""
    
    classes_updated = pyqtSignal()  # 車種更新信號
    
    def __init__(self, class_manager: VehicleClassManager, parent=None):
        super().__init__(parent)
        self.class_manager = class_manager
        self.setWindowTitle('車種類別管理')
        self.setFixedSize(900, 700)
        
        # 設定美觀的現代化樣式
        if STYLE_AVAILABLE:
            self.setStyleSheet(get_main_style())
        else:
            # 備用樣式
            self.setStyleSheet("""
                QDialog {
                    background-color: #f8f9fa;
                    color: #495057;
                    font-family: 'Segoe UI', Arial, sans-serif;
                }
                
                QPushButton {
                    background-color: #339af0;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: 500;
                }
                
                QPushButton:hover {
                    background-color: #228be6;
                }
                
                QTableWidget {
                    background-color: white;
                    border: 1px solid #dee2e6;
                    border-radius: 6px;
                }
            """)
        
        self.setup_ui()
        self.load_classes_list()
    
    def setup_ui(self):
        """設定使用者介面"""
        layout = QVBoxLayout(self)
        
        # 創建分頁介面
        tab_widget = QTabWidget()
        
        # 車種管理分頁
        manage_tab = self.create_manage_tab()
        tab_widget.addTab(manage_tab, "🚗 車種管理")
        
        # 匯入匯出分頁
        import_export_tab = self.create_import_export_tab()
        tab_widget.addTab(import_export_tab, "📁 匯入匯出")
        
        # 預設模板分頁
        templates_tab = self.create_templates_tab()
        tab_widget.addTab(templates_tab, "📋 預設模板")
        
        layout.addWidget(tab_widget)
        
        # 底部按鈕
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_changes)
        layout.addWidget(button_box)
    
    def create_manage_tab(self) -> QWidget:
        """創建車種管理分頁"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        # 左側：車種清單
        left_panel = QGroupBox("車種清單")
        left_layout = QVBoxLayout(left_panel)
        
        # 車種表格
        self.class_table = QTableWidget()
        self.class_table.setColumnCount(6)
        self.class_table.setHorizontalHeaderLabels([
            "ID", "表情", "名稱", "快捷鍵", "顏色", "啟用"
        ])
        
        # 設定欄寬
        header = self.class_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # ID
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # 表情
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # 名稱
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # 快捷鍵
        header.setSectionResizeMode(4, QHeaderView.Fixed)  # 顏色
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # 啟用
        
        self.class_table.setColumnWidth(0, 50)   # ID
        self.class_table.setColumnWidth(1, 60)   # 表情
        self.class_table.setColumnWidth(3, 80)   # 快捷鍵
        self.class_table.setColumnWidth(4, 80)   # 顏色
        self.class_table.setColumnWidth(5, 60)   # 啟用
        
        self.class_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.class_table.itemSelectionChanged.connect(self.on_class_selected)
        
        left_layout.addWidget(self.class_table)
        
        # 清單操作按鈕
        list_buttons = QHBoxLayout()
        
        self.add_btn = QPushButton("➕ 新增")
        self.add_btn.clicked.connect(self.add_new_class)
        list_buttons.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("✏️ 編輯")
        self.edit_btn.clicked.connect(self.edit_selected_class)
        self.edit_btn.setEnabled(False)
        list_buttons.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("🗑️ 刪除")
        self.delete_btn.clicked.connect(self.delete_selected_class)
        self.delete_btn.setEnabled(False)
        list_buttons.addWidget(self.delete_btn)
        
        list_buttons.addStretch()
        
        self.move_up_btn = QPushButton("⬆️")
        self.move_up_btn.clicked.connect(self.move_class_up)
        self.move_up_btn.setEnabled(False)
        list_buttons.addWidget(self.move_up_btn)
        
        self.move_down_btn = QPushButton("⬇️")
        self.move_down_btn.clicked.connect(self.move_class_down)
        self.move_down_btn.setEnabled(False)
        list_buttons.addWidget(self.move_down_btn)
        
        left_layout.addLayout(list_buttons)
        
        # 右側：詳細設定
        right_panel = QGroupBox("車種詳細設定")
        right_layout = QFormLayout(right_panel)
        
        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(self.on_detail_changed)
        right_layout.addRow("車種名稱:", self.name_edit)
        
        self.emoji_edit = QLineEdit()
        self.emoji_edit.setMaxLength(2)
        self.emoji_edit.textChanged.connect(self.on_detail_changed)
        right_layout.addRow("表情符號:", self.emoji_edit)
        
        self.shortcut_edit = QLineEdit()
        self.shortcut_edit.setMaxLength(1)
        self.shortcut_edit.textChanged.connect(self.on_detail_changed)
        right_layout.addRow("快捷鍵:", self.shortcut_edit)
        
        # 顏色選擇
        color_layout = QHBoxLayout()
        self.color_label = QLabel("    ")
        self.color_label.setStyleSheet("background-color: red; border: 1px solid black;")
        self.color_label.setFixedSize(30, 20)
        
        self.color_btn = QPushButton("選擇顏色")
        self.color_btn.clicked.connect(self.choose_color)
        
        color_layout.addWidget(self.color_label)
        color_layout.addWidget(self.color_btn)
        color_layout.addStretch()
        
        right_layout.addRow("標註顏色:", color_layout)
        
        self.enabled_cb = QCheckBox("啟用此車種")
        self.enabled_cb.stateChanged.connect(self.on_detail_changed)
        right_layout.addRow("", self.enabled_cb)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        self.description_edit.textChanged.connect(self.on_detail_changed)
        right_layout.addRow("描述:", self.description_edit)
        
        # 將左右面板加入到分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([500, 400])
        
        layout.addWidget(splitter)
        
        # 追蹤是否有變更
        self.current_class_id = None
        self.details_changed = False
        
        return widget
    
    def create_import_export_tab(self) -> QWidget:
        """創建匯入匯出分頁"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 匯出區域
        export_group = QGroupBox("匯出車種設定")
        export_layout = QVBoxLayout(export_group)
        
        export_info = QLabel(
            "匯出車種設定到不同格式的檔案，以便在其他專案中使用或備份。"
        )
        export_info.setWordWrap(True)
        export_layout.addWidget(export_info)
        
        export_buttons = QHBoxLayout()
        
        export_json_btn = QPushButton("📄 匯出 JSON 設定檔")
        export_json_btn.clicked.connect(self.export_json_config)
        export_buttons.addWidget(export_json_btn)
        
        export_txt_btn = QPushButton("📝 匯出 YOLO 類別檔")
        export_txt_btn.clicked.connect(self.export_txt_classes)
        export_buttons.addWidget(export_txt_btn)
        
        export_layout.addLayout(export_buttons)
        
        layout.addWidget(export_group)
        
        # 匯入區域
        import_group = QGroupBox("匯入車種設定")
        import_layout = QVBoxLayout(import_group)
        
        import_info = QLabel(
            "從其他檔案匯入車種設定。注意：匯入會覆蓋現有設定。"
        )
        import_info.setWordWrap(True)
        import_info.setStyleSheet("color: orange;")
        import_layout.addWidget(import_info)
        
        import_buttons = QHBoxLayout()
        
        import_json_btn = QPushButton("📁 匯入 JSON 設定檔")
        import_json_btn.clicked.connect(self.import_json_config)
        import_buttons.addWidget(import_json_btn)
        
        import_txt_btn = QPushButton("📂 匯入 YOLO 類別檔")
        import_txt_btn.clicked.connect(self.import_txt_classes)
        import_buttons.addWidget(import_txt_btn)
        
        import_layout.addLayout(import_buttons)
        
        layout.addWidget(import_group)
        
        layout.addStretch()
        
        return widget
    
    def create_templates_tab(self) -> QWidget:
        """創建預設模板分頁"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        info_label = QLabel(
            "選擇預設的車種模板，快速設定常用的車種分類。"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 模板選項
        templates_group = QGroupBox("選擇模板")
        templates_layout = QVBoxLayout(templates_group)
        
        # 基本車種模板
        basic_btn = QPushButton("🚗 基本車種 (機車、汽車、卡車、公車)")
        basic_btn.clicked.connect(lambda: self.apply_template("basic"))
        templates_layout.addWidget(basic_btn)
        
        # 詳細車種模板
        detailed_btn = QPushButton("🚛 詳細車種 (包含特殊車輛)")
        detailed_btn.clicked.connect(lambda: self.apply_template("detailed"))
        templates_layout.addWidget(detailed_btn)
        
        # 交通工具模板
        transport_btn = QPushButton("🚲 所有交通工具 (包含非機動車)")
        transport_btn.clicked.connect(lambda: self.apply_template("transport"))
        templates_layout.addWidget(transport_btn)
        
        # 商用車模板
        commercial_btn = QPushButton("🚚 商用車專用")
        commercial_btn.clicked.connect(lambda: self.apply_template("commercial"))
        templates_layout.addWidget(commercial_btn)
        
        layout.addWidget(templates_group)
        
        # 預設模板說明
        template_info = QTextEdit()
        template_info.setReadOnly(True)
        template_info.setMaximumHeight(200)
        template_info.setText("""
模板說明：

🚗 基本車種：
• 機車、汽車、卡車、公車 (4類)
• 適合一般道路交通監控

🚛 詳細車種：
• 基本車種 + 計程車、警車、救護車、消防車 (8類)
• 適合城市交通分析

🚲 所有交通工具：
• 包含腳踏車、電動車、三輪車等 (12類)
• 適合完整的交通調查

🚚 商用車專用：
• 各種貨車、聯結車、工程車 (6類)
• 適合物流或工業區監控
        """)
        layout.addWidget(template_info)
        
        layout.addStretch()
        
        return widget
    
    def load_classes_list(self):
        """載入車種清單到表格"""
        classes = self.class_manager.get_all_classes()
        self.class_table.setRowCount(len(classes))
        
        for row, vehicle_class in enumerate(classes):
            # ID
            id_item = QTableWidgetItem(str(vehicle_class.class_id))
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            self.class_table.setItem(row, 0, id_item)
            
            # 表情符號
            emoji_item = QTableWidgetItem(vehicle_class.emoji)
            self.class_table.setItem(row, 1, emoji_item)
            
            # 名稱
            name_item = QTableWidgetItem(vehicle_class.name)
            self.class_table.setItem(row, 2, name_item)
            
            # 快捷鍵
            shortcut_item = QTableWidgetItem(vehicle_class.shortcut_key)
            self.class_table.setItem(row, 3, shortcut_item)
            
            # 顏色
            color_item = QTableWidgetItem("■")
            color_item.setBackground(vehicle_class.color)
            color_item.setFlags(color_item.flags() & ~Qt.ItemIsEditable)
            self.class_table.setItem(row, 4, color_item)
            
            # 啟用狀態
            enabled_item = QTableWidgetItem("✓" if vehicle_class.enabled else "✗")
            enabled_item.setFlags(enabled_item.flags() & ~Qt.ItemIsEditable)
            self.class_table.setItem(row, 5, enabled_item)
            
            # 儲存類別 ID 到行資料
            self.class_table.item(row, 0).setData(Qt.UserRole, vehicle_class.class_id)
    
    def on_class_selected(self):
        """車種選擇變更"""
        current_row = self.class_table.currentRow()
        has_selection = current_row >= 0
        
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
        self.move_up_btn.setEnabled(has_selection and current_row > 0)
        self.move_down_btn.setEnabled(has_selection and current_row < self.class_table.rowCount() - 1)
        
        if has_selection:
            class_id = self.class_table.item(current_row, 0).data(Qt.UserRole)
            self.load_class_details(class_id)
        else:
            self.clear_class_details()
    
    def load_class_details(self, class_id: int):
        """載入車種詳細資訊"""
        vehicle_class = self.class_manager.get_class(class_id)
        if not vehicle_class:
            return
        
        self.current_class_id = class_id
        self.details_changed = False
        
        # 阻止信號避免觸發變更事件
        self.block_detail_signals(True)
        
        self.name_edit.setText(vehicle_class.name)
        self.emoji_edit.setText(vehicle_class.emoji)
        self.shortcut_edit.setText(vehicle_class.shortcut_key)
        self.enabled_cb.setChecked(vehicle_class.enabled)
        self.description_edit.setPlainText(vehicle_class.description)
        
        # 更新顏色顯示
        color_style = f"background-color: {vehicle_class.color.name()}; border: 1px solid black;"
        self.color_label.setStyleSheet(color_style)
        self.color_label.setProperty("color", vehicle_class.color)
        
        self.block_detail_signals(False)
    
    def clear_class_details(self):
        """清空車種詳細資訊"""
        self.current_class_id = None
        self.details_changed = False
        
        self.block_detail_signals(True)
        
        self.name_edit.clear()
        self.emoji_edit.clear()
        self.shortcut_edit.clear()
        self.enabled_cb.setChecked(False)
        self.description_edit.clear()
        self.color_label.setStyleSheet("background-color: red; border: 1px solid black;")
        
        self.block_detail_signals(False)
    
    def block_detail_signals(self, block: bool):
        """阻止詳細資訊的信號"""
        self.name_edit.blockSignals(block)
        self.emoji_edit.blockSignals(block)
        self.shortcut_edit.blockSignals(block)
        self.enabled_cb.blockSignals(block)
        self.description_edit.blockSignals(block)
    
    def on_detail_changed(self):
        """詳細資訊變更"""
        if self.current_class_id is not None:
            self.details_changed = True
    
    def choose_color(self):
        """選擇顏色"""
        current_color = self.color_label.property("color") or QColor(255, 75, 75)
        color = QColorDialog.getColor(current_color, self, "選擇標註顏色")
        
        if color.isValid():
            color_style = f"background-color: {color.name()}; border: 1px solid black;"
            self.color_label.setStyleSheet(color_style)
            self.color_label.setProperty("color", color)
            self.on_detail_changed()
    
    def add_new_class(self):
        """新增車種"""
        dialog = AddClassDialog(self.class_manager, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_classes_list()
            self.classes_updated.emit()
    
    def edit_selected_class(self):
        """編輯選中的車種"""
        if self.current_class_id is not None:
            self.save_current_details()
    
    def save_current_details(self):
        """儲存當前的詳細資訊"""
        if self.current_class_id is None or not self.details_changed:
            return
        
        try:
            color = self.color_label.property("color") or QColor(255, 75, 75)
            
            self.class_manager.update_class(
                class_id=self.current_class_id,
                name=self.name_edit.text().strip(),
                emoji=self.emoji_edit.text(),
                shortcut_key=self.shortcut_edit.text(),
                color=color,
                enabled=self.enabled_cb.isChecked(),
                description=self.description_edit.toPlainText()
            )
            
            self.details_changed = False
            self.load_classes_list()
            self.classes_updated.emit()
            
        except ValueError as e:
            QMessageBox.warning(self, "更新失敗", str(e))
    
    def delete_selected_class(self):
        """刪除選中的車種"""
        if self.current_class_id is None:
            return
        
        vehicle_class = self.class_manager.get_class(self.current_class_id)
        if not vehicle_class:
            return
        
        reply = QMessageBox.question(
            self, "確認刪除",
            f"確定要刪除車種 '{vehicle_class.name}' 嗎？\n\n"
            "警告：這將影響已有的標註資料！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.class_manager.delete_class(self.current_class_id)
                self.load_classes_list()
                self.clear_class_details()
                self.classes_updated.emit()
                
            except ValueError as e:
                QMessageBox.critical(self, "刪除失敗", str(e))
    
    def move_class_up(self):
        """向上移動車種"""
        # 這個功能需要重新排序 ID，較複雜，暫時留空
        QMessageBox.information(self, "功能開發中", "排序功能正在開發中...")
    
    def move_class_down(self):
        """向下移動車種"""
        # 這個功能需要重新排序 ID，較複雜，暫時留空
        QMessageBox.information(self, "功能開發中", "排序功能正在開發中...")
    
    def export_json_config(self):
        """匯出 JSON 設定檔"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "匯出車種設定", "vehicle_classes.json",
            "JSON 檔案 (*.json);;所有檔案 (*)"
        )
        
        if filename:
            try:
                # 直接複製配置檔案
                import shutil
                shutil.copy2(self.class_manager.config_file, filename)
                QMessageBox.information(self, "匯出成功", f"車種設定已匯出至：\n{filename}")
                
            except Exception as e:
                QMessageBox.critical(self, "匯出失敗", f"匯出過程發生錯誤：\n{str(e)}")
    
    def export_txt_classes(self):
        """匯出 YOLO 類別檔"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "匯出類別清單", "classes.txt",
            "文字檔案 (*.txt);;所有檔案 (*)"
        )
        
        if filename:
            if self.class_manager.export_classes_txt(filename):
                QMessageBox.information(self, "匯出成功", f"類別清單已匯出至：\n{filename}")
            else:
                QMessageBox.critical(self, "匯出失敗", "匯出類別清單時發生錯誤")
    
    def import_json_config(self):
        """匯入 JSON 設定檔"""
        reply = QMessageBox.warning(
            self, "確認匯入",
            "匯入設定檔將覆蓋現有的車種設定！\n\n是否繼續？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        filename, _ = QFileDialog.getOpenFileName(
            self, "匯入車種設定", "",
            "JSON 檔案 (*.json);;所有檔案 (*)"
        )
        
        if filename:
            try:
                # 備份現有設定
                backup_file = self.class_manager.config_file + ".backup"
                import shutil
                shutil.copy2(self.class_manager.config_file, backup_file)
                
                # 替換設定檔
                shutil.copy2(filename, self.class_manager.config_file)
                
                # 重新載入
                self.class_manager.load_classes()
                self.load_classes_list()
                self.clear_class_details()
                self.classes_updated.emit()
                
                QMessageBox.information(
                    self, "匯入成功", 
                    f"車種設定已匯入成功！\n\n原設定已備份至：\n{backup_file}"
                )
                
            except Exception as e:
                QMessageBox.critical(self, "匯入失敗", f"匯入過程發生錯誤：\n{str(e)}")
    
    def import_txt_classes(self):
        """匯入 YOLO 類別檔"""
        reply = QMessageBox.warning(
            self, "確認匯入",
            "匯入類別檔將覆蓋現有的車種設定！\n\n是否繼續？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        filename, _ = QFileDialog.getOpenFileName(
            self, "匯入類別清單", "",
            "文字檔案 (*.txt);;所有檔案 (*)"
        )
        
        if filename:
            if self.class_manager.import_classes_txt(filename):
                self.load_classes_list()
                self.clear_class_details()
                self.classes_updated.emit()
                QMessageBox.information(self, "匯入成功", "類別清單已匯入成功！")
            else:
                QMessageBox.critical(self, "匯入失敗", "匯入類別清單時發生錯誤")
    
    def apply_template(self, template_name: str):
        """應用預設模板"""
        reply = QMessageBox.question(
            self, "確認套用模板",
            f"套用模板將覆蓋現有的車種設定！\n\n是否繼續？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        templates = {
            "basic": [
                {'name': '機車', 'emoji': '🏍', 'shortcut_key': '1'},
                {'name': '汽車', 'emoji': '🚗', 'shortcut_key': '2'},
                {'name': '卡車', 'emoji': '🚛', 'shortcut_key': '3'},
                {'name': '公車', 'emoji': '🚌', 'shortcut_key': '4'},
            ],
            "detailed": [
                {'name': '機車', 'emoji': '🏍', 'shortcut_key': '1'},
                {'name': '汽車', 'emoji': '🚗', 'shortcut_key': '2'},
                {'name': '卡車', 'emoji': '🚛', 'shortcut_key': '3'},
                {'name': '公車', 'emoji': '🚌', 'shortcut_key': '4'},
                {'name': '計程車', 'emoji': '🚕', 'shortcut_key': '5'},
                {'name': '警車', 'emoji': '🚓', 'shortcut_key': '6'},
                {'name': '救護車', 'emoji': '🚑', 'shortcut_key': '7'},
                {'name': '消防車', 'emoji': '🚒', 'shortcut_key': '8'},
            ],
            "transport": [
                {'name': '機車', 'emoji': '🏍', 'shortcut_key': '1'},
                {'name': '汽車', 'emoji': '🚗', 'shortcut_key': '2'},
                {'name': '卡車', 'emoji': '🚛', 'shortcut_key': '3'},
                {'name': '公車', 'emoji': '🚌', 'shortcut_key': '4'},
                {'name': '腳踏車', 'emoji': '🚲', 'shortcut_key': '5'},
                {'name': '電動車', 'emoji': '🔋', 'shortcut_key': '6'},
                {'name': '三輪車', 'emoji': '🛺', 'shortcut_key': '7'},
                {'name': '計程車', 'emoji': '🚕', 'shortcut_key': '8'},
            ],
            "commercial": [
                {'name': '小貨車', 'emoji': '🚚', 'shortcut_key': '1'},
                {'name': '中型貨車', 'emoji': '🚛', 'shortcut_key': '2'},
                {'name': '大型貨車', 'emoji': '🚛', 'shortcut_key': '3'},
                {'name': '聯結車', 'emoji': '🚛', 'shortcut_key': '4'},
                {'name': '工程車', 'emoji': '🚜', 'shortcut_key': '5'},
                {'name': '混凝土車', 'emoji': '🚚', 'shortcut_key': '6'},
            ]
        }
        
        template_classes = templates.get(template_name, [])
        if not template_classes:
            return
        
        try:
            # 清除現有類別
            self.class_manager.classes = {}
            self.class_manager.next_id = 0
            
            # 添加模板類別
            for i, cls_data in enumerate(template_classes):
                vehicle_class = VehicleClass(
                    class_id=i,
                    name=cls_data['name'],
                    emoji=cls_data['emoji'],
                    shortcut_key=cls_data['shortcut_key']
                )
                self.class_manager.classes[i] = vehicle_class
            
            self.class_manager.next_id = len(template_classes)
            self.class_manager.save_classes()
            
            self.load_classes_list()
            self.clear_class_details()
            self.classes_updated.emit()
            
            QMessageBox.information(self, "套用成功", f"已成功套用 {template_name} 模板！")
            
        except Exception as e:
            QMessageBox.critical(self, "套用失敗", f"套用模板時發生錯誤：\n{str(e)}")
    
    def apply_changes(self):
        """套用變更"""
        if self.details_changed:
            self.save_current_details()
        QMessageBox.information(self, "變更已套用", "所有變更已儲存")
    
    def accept(self):
        """接受對話框"""
        if self.details_changed:
            self.save_current_details()
        super().accept()


class AddClassDialog(QDialog):
    """新增車種對話框"""
    
    def __init__(self, class_manager: VehicleClassManager, parent=None):
        super().__init__(parent)
        self.class_manager = class_manager
        self.setWindowTitle('新增車種')
        self.setFixedSize(400, 350)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QFormLayout(self)
        
        # 車種名稱
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("例如：電動車")
        layout.addRow("車種名稱 *:", self.name_edit)
        
        # 表情符號
        self.emoji_edit = QLineEdit()
        self.emoji_edit.setMaxLength(2)
        self.emoji_edit.setPlaceholderText("🚗")
        self.emoji_edit.setText("🚗")
        layout.addRow("表情符號:", self.emoji_edit)
        
        # 快捷鍵
        self.shortcut_edit = QLineEdit()
        self.shortcut_edit.setMaxLength(1)
        self.shortcut_edit.setPlaceholderText("例如：E")
        layout.addRow("快捷鍵:", self.shortcut_edit)
        
        # 顏色選擇
        color_layout = QHBoxLayout()
        self.color_label = QLabel("    ")
        self.current_color = QColor(255, 75, 75)
        self.color_label.setStyleSheet(f"background-color: {self.current_color.name()}; border: 1px solid black;")
        self.color_label.setFixedSize(30, 20)
        
        self.color_btn = QPushButton("選擇顏色")
        self.color_btn.clicked.connect(self.choose_color)
        
        color_layout.addWidget(self.color_label)
        color_layout.addWidget(self.color_btn)
        color_layout.addStretch()
        
        layout.addRow("標註顏色:", color_layout)
        
        # 描述
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("車種描述（可選）")
        layout.addRow("描述:", self.description_edit)
        
        # 按鈕
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_dialog)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
    
    def choose_color(self):
        """選擇顏色"""
        color = QColorDialog.getColor(self.current_color, self, "選擇標註顏色")
        if color.isValid():
            self.current_color = color
            self.color_label.setStyleSheet(f"background-color: {color.name()}; border: 1px solid black;")
    
    def accept_dialog(self):
        """接受對話框"""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "輸入錯誤", "請輸入車種名稱")
            return
        
        try:
            self.class_manager.add_class(
                name=name,
                color=self.current_color,
                description=self.description_edit.toPlainText(),
                shortcut_key=self.shortcut_edit.text(),
                emoji=self.emoji_edit.text() or "🚗"
            )
            self.accept()
            
        except ValueError as e:
            QMessageBox.warning(self, "新增失敗", str(e))


# 使用範例
if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    
    # 創建車種管理器
    manager = VehicleClassManager()
    
    # 顯示管理對話框
    dialog = VehicleClassManagerDialog(manager)
    dialog.show()
    
    sys.exit(app.exec_())
