import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFileDialog, QGroupBox, QRadioButton,
                            QCheckBox, QSpinBox, QFormLayout, QLineEdit)
from PyQt5.QtCore import Qt


class ExportDialog(QDialog):
    """
    导出表格文件的对话框
    """
    
    def __init__(self, parent=None):
        """
        初始化导出对话框
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        
        # 设置对话框属性
        self.setWindowTitle("导出TK达人表格")
        self.resize(500, 350)
        self.setModal(True)
        
        # 导出目录
        self.export_directory = ""
        
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
        self.info_label = QLabel("设置导出选项并选择导出目录")
        self.main_layout.addWidget(self.info_label)
        
        # 创建导出目录选择
        self.create_directory_group()
        
        # 创建导出选项
        self.create_options_group()
        
        # 创建文件名选项
        self.create_filename_group()
        
        # 创建按钮组
        self.create_button_group()
    
    def create_directory_group(self):
        """
        创建导出目录选择组
        """
        # 创建组框
        self.dir_group = QGroupBox("导出目录")
        self.dir_layout = QHBoxLayout(self.dir_group)
        
        # 创建路径输入框
        self.dir_edit = QLineEdit()
        self.dir_edit.setReadOnly(True)
        self.dir_edit.setPlaceholderText("请选择导出目录...")
        
        # 创建浏览按钮
        self.browse_button = QPushButton("浏览...")
        
        # 添加到布局
        self.dir_layout.addWidget(self.dir_edit)
        self.dir_layout.addWidget(self.browse_button)
        
        # 设置信号连接
        self.browse_button.clicked.connect(self.browse_directory)
        
        self.main_layout.addWidget(self.dir_group)
    
    def create_options_group(self):
        """
        创建导出选项组
        """
        # 创建组框
        self.options_group = QGroupBox("导出选项")
        self.options_layout = QFormLayout(self.options_group)
        
        # 创建每个文件记录数量选择
        self.records_per_file_label = QLabel("每个文件记录数量:")
        self.records_per_file_spin = QSpinBox()
        self.records_per_file_spin.setRange(1, 1000)
        self.records_per_file_spin.setValue(50)
        self.records_per_file_spin.setSingleStep(10)
        
        # 创建选项
        self.export_duplicates_checkbox = QCheckBox("导出重复记录")
        self.export_username_only_checkbox = QCheckBox("只导出用户名字段")
        self.export_all_checkbox = QCheckBox("导出所有字段")
        
        # 设置默认状态
        self.export_username_only_checkbox.setChecked(True)
        
        # 添加到布局
        self.options_layout.addRow(self.records_per_file_label, self.records_per_file_spin)
        self.options_layout.addRow(self.export_duplicates_checkbox)
        self.options_layout.addRow(self.export_username_only_checkbox)
        self.options_layout.addRow(self.export_all_checkbox)
        
        # 连接信号槽，使选项互斥
        self.export_username_only_checkbox.toggled.connect(self.toggle_export_options)
        self.export_all_checkbox.toggled.connect(self.toggle_export_options)
        
        self.main_layout.addWidget(self.options_group)
    
    def toggle_export_options(self, checked):
        """
        切换导出选项，确保两个选项互斥
        """
        sender = self.sender()
        if checked:
            if sender == self.export_username_only_checkbox:
                self.export_all_checkbox.setChecked(False)
            elif sender == self.export_all_checkbox:
                self.export_username_only_checkbox.setChecked(False)
    
    def create_filename_group(self):
        """
        创建文件名选项组
        """
        # 创建组框
        self.filename_group = QGroupBox("文件命名")
        self.filename_layout = QFormLayout(self.filename_group)
        
        # 创建文件名前缀
        self.prefix_label = QLabel("文件名前缀:")
        self.prefix_edit = QLineEdit("TK达人_")
        
        # 创建文件格式选择
        self.format_label = QLabel("文件格式:")
        self.format_xlsx_radio = QRadioButton("Excel 2007+ (.xlsx)")
        self.format_xls_radio = QRadioButton("Excel 97-2003 (.xls)")
        self.format_csv_radio = QRadioButton("CSV文件 (.csv)")
        
        # 默认选择
        self.format_xlsx_radio.setChecked(True)
        
        # 创建格式布局
        format_layout = QVBoxLayout()
        format_layout.addWidget(self.format_xlsx_radio)
        format_layout.addWidget(self.format_xls_radio)
        format_layout.addWidget(self.format_csv_radio)
        
        # 添加到布局
        self.filename_layout.addRow(self.prefix_label, self.prefix_edit)
        self.filename_layout.addRow(self.format_label, format_layout)
        
        self.main_layout.addWidget(self.filename_group)
    
    def create_button_group(self):
        """
        创建按钮组
        """
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 创建按钮
        self.export_button = QPushButton("导出")
        self.cancel_button = QPushButton("取消")
        
        # 设置按钮属性
        self.export_button.setDefault(True)
        
        # 添加到布局
        button_layout.addStretch()
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.cancel_button)
        
        # 设置信号连接
        self.export_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        self.main_layout.addLayout(button_layout)
    
    def browse_directory(self):
        """
        浏览并选择导出目录
        """
        directory = QFileDialog.getExistingDirectory(self, "选择导出目录")
        
        if directory:
            self.export_directory = directory
            self.dir_edit.setText(directory)
    
    def get_export_directory(self):
        """
        获取导出目录
        
        Returns:
            str: 导出目录路径
        """
        return self.export_directory
    
    def get_options(self):
        """
        获取导出选项
        
        Returns:
            dict: 选项字典
        """
        file_format = "xlsx"
        if self.format_xls_radio.isChecked():
            file_format = "xls"
        elif self.format_csv_radio.isChecked():
            file_format = "csv"
            
        return {
            "records_per_file": self.records_per_file_spin.value(),
            "export_duplicates": self.export_duplicates_checkbox.isChecked(),
            "export_username_only": self.export_username_only_checkbox.isChecked(),
            "export_all_fields": self.export_all_checkbox.isChecked(),
            "file_prefix": self.prefix_edit.text(),
            "file_format": file_format
        } 