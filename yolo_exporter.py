import os
from PyQt5.QtGui import QPixmap

class YoloExporter:
    """YOLO v8格式匯出器"""
    
    @staticmethod
    def get_class_names():
        """取得支援的車輛類別名稱"""
        from annotator import VEHICLE_CLASSES
        return [name for name, _ in VEHICLE_CLASSES]
    
    @staticmethod
    def export_annotations(image_path, annotations, output_dir='labels'):
        """
        匯出標註為YOLO v8格式
        
        Args:
            image_path (str): 圖片路徑
            annotations (list): 標註資料 [{'id': int, 'rect': QRect, 'class_id': int, 'class_name': str}]
            output_dir (str): 輸出目錄
            
        Returns:
            str: 匯出檔案路徑
        """
        if not annotations:
            raise ValueError("沒有標註資料可匯出")
            
        # 確保輸出目錄存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 獲取圖片尺寸
        img = QPixmap(image_path)
        img_w, img_h = img.width(), img.height()
        
        # 生成標註檔案路徑
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        label_path = os.path.join(output_dir, f'{base_name}.txt')
        
        # 寫入YOLO格式標註
        with open(label_path, 'w', encoding='utf-8') as f:
            for annotation in annotations:
                rect = annotation['rect']
                class_id = annotation['class_id']
                
                # 計算邊界框座標
                x1, y1 = rect.x(), rect.y()
                x2, y2 = x1 + rect.width(), y1 + rect.height()
                
                # 轉換為YOLO格式 (相對座標)
                x_center = (x1 + x2) / 2 / img_w
                y_center = (y1 + y2) / 2 / img_h
                width = abs(x2 - x1) / img_w
                height = abs(y2 - y1) / img_h
                
                # 寫入檔案 (class_id x_center y_center width height)
                f.write(f'{class_id} {x_center:.10f} {y_center:.10f} {width:.10f} {height:.10f}\n')
        
        return label_path
    
    @staticmethod
    def get_class_names():
        """獲取類別名稱對應表"""
        return {
            0: '機車',
            1: '汽車', 
            2: '卡車',
            3: '公車'
        }
    
    @staticmethod
    def get_class_names_english():
        """獲取英文類別名稱對應表"""
        return {
            0: 'motorcycle',
            1: 'car',
            2: 'truck',
            3: 'bus'
        }
    
    @staticmethod
    def export_classes_file(output_path='classes.txt', use_english=True):
        """
        匯出類別檔案
        
        Args:
            output_path (str): 輸出檔案路徑
            use_english (bool): 是否使用英文類別名稱
            
        Returns:
            str: 類別檔案路徑
        """
        # 確保輸出目錄存在
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        
        if use_english:
            class_names = YoloExporter.get_class_names_english()
        else:
            class_names = YoloExporter.get_class_names()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for class_id in sorted(class_names.keys()):
                f.write(f'{class_names[class_id]}\n')
        
        return output_path
