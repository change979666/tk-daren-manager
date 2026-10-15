import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFileDialog, QListWidget, QListWidgetItem,
                            QCheckBox, QGroupBox, QRadioButton, QMessageBox,
                            QFormLayout)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon


class ImportDialog(QDialog):
    """
    导入表格文件的对话框
    """
    
    def __init__(self, parent=None):
        """
        初始化导入对话框
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        
        # 设置对话框属性
        self.setWindowTitle("导入TK达人表格")
        self.resize(600, 400)
        self.setModal(True)
        
        # 文件列表
        self.file_paths = []
        
        # 初始化UI
        self.init_ui()
    
    def init_ui(self):
        """
        初始化用户界面
        """
        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # 添加说明标签
        self.info_label = QLabel("请选择要导入的表格文件（支持.xls、.xlsx和.csv格式）")
        self.main_layout.addWidget(self.info_label)
        
        # 创建文件列表组
        self.create_file_list_group()
        
        # 创建选项组
        self.create_options_group()
        
        # 创建按钮组
        self.create_button_group()
    
    def create_file_list_group(self):
        """
        创建文件列表组
        """
        # 创建组框
        self.file_group = QGroupBox("导入文件列表")
        self.file_layout = QVBoxLayout(self.file_group)
        
        # 创建文件列表
        self.file_list = QListWidget()
        self.file_list.setAlternatingRowColors(True)
        self.file_layout.addWidget(self.file_list)
        
        # 创建文件操作按钮
        file_buttons_layout = QHBoxLayout()
        
        self.add_file_button = QPushButton("添加文件")
        self.add_dir_button = QPushButton("添加目录")
        self.remove_file_button = QPushButton("移除选中")
        self.clear_all_button = QPushButton("清空列表")
        
        file_buttons_layout.addWidget(self.add_file_button)
        file_buttons_layout.addWidget(self.add_dir_button)
        file_buttons_layout.addWidget(self.remove_file_button)
        file_buttons_layout.addWidget(self.clear_all_button)
        
        self.file_layout.addLayout(file_buttons_layout)
        
        # 设置信号连接
        self.add_file_button.clicked.connect(self.add_files)
        self.add_dir_button.clicked.connect(self.add_directory)
        self.remove_file_button.clicked.connect(self.remove_selected_files)
        self.clear_all_button.clicked.connect(self.clear_file_list)
        
        self.main_layout.addWidget(self.file_group)
    
    def create_options_group(self):
        """
        创建选项组
        """
        # 创建组框
        self.options_group = QGroupBox("导入选项")
        self.options_layout = QFormLayout(self.options_group)
        
        # 创建选项
        self.replace_checkbox = QCheckBox("清空现有数据后导入")
        self.validate_checkbox = QCheckBox("导入前检查表格格式")
        self.mark_duplicates_checkbox = QCheckBox("自动标记重复的达人用户名")
        
        # 默认值
        self.validate_checkbox.setChecked(True)
        self.mark_duplicates_checkbox.setChecked(True)
        
        # 添加到布局
        self.options_layout.addRow(self.replace_checkbox)
        self.options_layout.addRow(self.validate_checkbox)
        self.options_layout.addRow(self.mark_duplicates_checkbox)
        
        self.main_layout.addWidget(self.options_group)
    
    def create_button_group(self):
        """
        创建按钮组
        """
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 创建按钮
        self.import_button = QPushButton("导入")
        self.cancel_button = QPushButton("取消")
        
        # 设置按钮属性
        self.import_button.setDefault(True)
        
        # 添加到布局
        button_layout.addStretch()
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.cancel_button)
        
        # 设置信号连接
        self.import_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        self.main_layout.addLayout(button_layout)
    
    def add_files(self):
        """
        添加文件
        """
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "选择表格文件", "",
            "表格文件 (*.xlsx *.xls *.csv);;Excel文件 (*.xlsx *.xls);;CSV文件 (*.csv);;所有文件 (*.*)"
        )
        
        if file_paths:
            for file_path in file_paths:
                if file_path not in self.file_paths:
                    self.file_paths.append(file_path)
                    item = QListWidgetItem(os.path.basename(file_path))
                    item.setToolTip(file_path)
                    self.file_list.addItem(item)
    
    def add_directory(self):
        """
        添加目录中的所有Excel文件
        """
        dir_path = QFileDialog.getExistingDirectory(self, "选择目录")
        
        if dir_path:
            table_files = []
            for root, _, files in os.walk(dir_path):
                for file in files:
                    if file.endswith((".xlsx", ".xls", ".csv")):
                        file_path = os.path.join(root, file)
                        table_files.append(file_path)
            
            if table_files:
                for file_path in table_files:
                    if file_path not in self.file_paths:
                        self.file_paths.append(file_path)
                        item = QListWidgetItem(os.path.basename(file_path))
                        item.setToolTip(file_path)
                        self.file_list.addItem(item)
                
                QMessageBox.information(self, "添加成功", 
                                       f"从目录 {dir_path} 添加了 {len(table_files)} 个表格文件。")
            else:
                QMessageBox.warning(self, "未找到文件", 
                                   f"在目录 {dir_path} 中未找到支持的表格文件(.xlsx, .xls, .csv)。")
    
    def remove_selected_files(self):
        """
        移除选中的文件
        """
        selected_items = self.file_list.selectedItems()
        
        if not selected_items:
            return
        
        for item in selected_items:
            file_path = item.toolTip()
            row = self.file_list.row(item)
            self.file_list.takeItem(row)
            if file_path in self.file_paths:
                self.file_paths.remove(file_path)
    
    def clear_file_list(self):
        """
        清空文件列表
        """
        self.file_list.clear()
        self.file_paths = []
    
    def get_selected_files(self):
        """
        获取选择的文件列表
        
        Returns:
            list: 文件路径列表
        """
        return self.file_paths
    
    def get_options(self):
        """
        获取导入选项
        
        Returns:
            dict: 选项字典
        """
        return {
            "replace_existing": self.replace_checkbox.isChecked(),
            "validate": self.validate_checkbox.isChecked(),
            "mark_duplicates": self.mark_duplicates_checkbox.isChecked()
        } 