from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant, QModelIndex
from PyQt5.QtGui import QColor, QBrush, QFont
from datetime import datetime


class TkTableModel(QAbstractTableModel):
    """
    TK达人表格数据模型
    """
    
    # 定义列
    COLUMNS = ["序号", "达人用户名", "记录时间", "是否重复", "备注"]
    
    def __init__(self, data_manager):
        """
        初始化表格模型
        
        Args:
            data_manager: 数据管理器实例
        """
        super().__init__()
        self.data_manager = data_manager
    
    def rowCount(self, parent=QModelIndex()):
        """
        返回行数
        """
        return self.data_manager.get_count()
    
    def columnCount(self, parent=QModelIndex()):
        """
        返回列数
        """
        return len(self.COLUMNS)
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """
        返回表头数据
        """
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.COLUMNS[section]
            else:
                return str(section + 1)
        return QVariant()
    
    def data(self, index, role=Qt.DisplayRole):
        """
        返回单元格数据
        """
        if not index.isValid():
            return QVariant()
        
        row = index.row()
        col = index.column()
        
        if row >= self.rowCount() or col >= self.columnCount():
            return QVariant()
        
        # 获取对应行的数据
        record = self.data_manager.get_record(row)
        
        if role == Qt.DisplayRole:
            # 显示数据
            if col == 0:  # 序号
                return str(row + 1)
            elif col == 1:  # 达人用户名
                return record.get("username", "")
            elif col == 2:  # 记录时间
                import_time = record.get("import_time")
                if import_time:
                    return import_time.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    return "尚未记录"
            elif col == 3:  # 是否重复
                return "是" if record.get("is_duplicate", False) else "否"
            elif col == 4:  # 备注
                return record.get("remark", "")
        
        elif role == Qt.BackgroundRole:
            # 设置背景色
            if record.get("is_duplicate", False):
                return QBrush(QColor(255, 230, 230))  # 浅红色
        
        elif role == Qt.ForegroundRole:
            # 设置文字颜色
            if record.get("is_duplicate", False):
                return QBrush(QColor(200, 0, 0))  # 红色
            
            # 如果没有记录时间，使用灰色显示
            if col == 2 and not record.get("import_time"):
                return QBrush(QColor(150, 150, 150))  # 灰色
        
        elif role == Qt.FontRole:
            # 设置字体
            font = QFont()
            if record.get("is_duplicate", False):
                font.setBold(True)
            return font
        
        elif role == Qt.TextAlignmentRole:
            # 设置对齐方式
            if col == 0:  # 序号
                return Qt.AlignCenter
            else:
                return Qt.AlignVCenter | Qt.AlignLeft
        
        return QVariant()
    
    def sort(self, column, order=Qt.AscendingOrder):
        """
        排序数据
        """
        # 映射列索引到字段名
        field_map = {
            0: "id",
            1: "username",
            2: "import_time",
            3: "is_duplicate",
            4: "remark"
        }
        
        if column in field_map:
            # 排序
            self.layoutAboutToBeChanged.emit()
            self.data_manager.sort_by(field_map[column], order == Qt.AscendingOrder)
            self.layoutChanged.emit() 