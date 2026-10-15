import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QPushButton, QLabel, QFileDialog, QMessageBox,
                            QProgressBar, QTabWidget, QTableView, QHeaderView,
                            QAbstractItemView, QAction, QMenu, QToolBar, QStatusBar,
                            QApplication)
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette
from PyQt5.QtCore import Qt, QSize, pyqtSignal

from app.components.tk_table_model import TkTableModel
from app.components.import_dialog import ImportDialog
from app.components.export_dialog import ExportDialog
from app.utils.data_manager import DataManager


class MainWindow(QMainWindow):
    """
    TK达人管理系统的主窗口
    """
    
    def __init__(self):
        super().__init__()
        
        # 设置窗口标题和大小
        self.setWindowTitle("TK达人管理系统")
        self.resize(1000, 700)
        
        # 数据管理器
        self.data_manager = DataManager()
        
        # 初始化UI
        self.init_ui()
        self.setup_connections()
        self.create_menus()
        
        # 更新状态栏消息
        self.update_status_message()
        
        # 显示加载的历史记录数量
        history_count = len(self.data_manager.history_records)
        QMessageBox.information(self, "历史记录加载完成", 
                             f"成功加载{history_count}条历史记录数据，可用于检测重复的达人用户名。")
        
    def init_ui(self):
        """
        初始化用户界面
        """
        # 设置中心部件
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建表格视图
        self.create_table_view()
        
        # 创建底部状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("准备就绪")
        
        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
    def create_toolbar(self):
        """
        创建工具栏
        """
        # 创建工具栏
        self.toolbar = QToolBar("主工具栏")
        self.toolbar.setMovable(False)
        self.toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(self.toolbar)
        
        # 导入按钮
        self.import_action = QAction("导入表格", self)
        self.import_action.setStatusTip("导入TK达人数据表格")
        self.toolbar.addAction(self.import_action)
        
        # 导出按钮
        self.export_action = QAction("导出表格", self)
        self.export_action.setStatusTip("导出TK达人数据")
        self.toolbar.addAction(self.export_action)
        
        self.toolbar.addSeparator()
        
        # 删除重复项按钮
        self.remove_duplicates_action = QAction("删除重复项", self)
        self.remove_duplicates_action.setStatusTip("删除重复的达人用户名")
        self.toolbar.addAction(self.remove_duplicates_action)
        
        # 清空数据按钮
        self.clear_data_action = QAction("清空数据", self)
        self.clear_data_action.setStatusTip("清空所有已导入的数据")
        self.toolbar.addAction(self.clear_data_action)
        
        # 刷新按钮
        self.refresh_action = QAction("刷新数据", self)
        self.refresh_action.setStatusTip("刷新显示数据")
        self.toolbar.addAction(self.refresh_action)
    
    def create_table_view(self):
        """
        创建表格视图
        """
        # 创建表格模型
        self.table_model = TkTableModel(self.data_manager)
        
        # 创建表格视图
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.setSortingEnabled(True)
        
        # 将表格视图添加到主布局
        self.main_layout.addWidget(self.table_view)
        
    def setup_connections(self):
        """
        设置信号和槽的连接
        """
        self.import_action.triggered.connect(self.import_data)
        self.export_action.triggered.connect(self.export_data)
        self.remove_duplicates_action.triggered.connect(self.remove_duplicates)
        self.clear_data_action.triggered.connect(self.clear_data)
        self.refresh_action.triggered.connect(self.refresh_data)
    
    def import_data(self):
        """
        导入数据对话框
        """
        import_dialog = ImportDialog(self)
        if import_dialog.exec_():
            file_paths = import_dialog.get_selected_files()
            if file_paths:
                try:
                    self.progress_bar.setVisible(True)
                    self.progress_bar.setValue(0)
                    
                    # 导入数据
                    duplicates = self.data_manager.import_files(file_paths, 
                                                              progress_callback=self.update_progress)
                    
                    # 刷新表格
                    self.table_model.layoutChanged.emit()
                    self.progress_bar.setVisible(False)
                    
                    # 更新状态栏
                    self.update_status_message()
                    
                    # 显示结果
                    msg = f"成功导入{len(file_paths)}个文件，共{self.data_manager.get_count()}条记录。"
                    if duplicates:
                        msg += f"\n发现{len(duplicates)}个重复的达人用户名。"
                    
                    QMessageBox.information(self, "导入完成", msg)
                    
                except Exception as e:
                    self.progress_bar.setVisible(False)
                    QMessageBox.critical(self, "导入错误", f"导入过程中发生错误：{str(e)}")
    
    def export_data(self):
        """
        导出数据对话框
        """
        export_dialog = ExportDialog(self)
        if export_dialog.exec_():
            export_dir = export_dialog.get_export_directory()
            if export_dir:
                try:
                    self.progress_bar.setVisible(True)
                    self.progress_bar.setValue(0)
                    
                    # 获取导出选项
                    options = export_dialog.get_options()
                    
                    # 导出数据
                    files_count = self.data_manager.export_data(
                        export_dir, 
                        records_per_file=options["records_per_file"],
                        export_duplicates=options["export_duplicates"],
                        file_prefix=options["file_prefix"],
                        file_format=options["file_format"],
                        export_username_only=options["export_username_only"],
                        progress_callback=self.update_progress
                    )
                    
                    self.progress_bar.setVisible(False)
                    
                    # 更新状态栏（可能有新的时间记录）
                    self.update_status_message()
                    
                    # 构建消息
                    export_type = "仅用户名" if options["export_username_only"] else "所有字段"
                    
                    # 显示结果
                    QMessageBox.information(self, "导出完成", 
                                           f"成功导出{self.data_manager.get_count()}条记录({export_type})到{files_count}个文件。")
                    
                except Exception as e:
                    self.progress_bar.setVisible(False)
                    QMessageBox.critical(self, "导出错误", f"导出过程中发生错误：{str(e)}")
    
    def remove_duplicates(self):
        """
        删除重复达人用户名
        """
        duplicates = self.data_manager.get_duplicates()
        if not duplicates:
            QMessageBox.information(self, "无重复项", "没有发现重复的达人用户名。")
            return
            
        reply = QMessageBox.question(self, "删除重复项", 
                                    f"发现{len(duplicates)}个重复的达人用户名，是否删除？\n只保留最新导入的记录。",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                                    
        if reply == QMessageBox.Yes:
            try:
                removed_count = self.data_manager.remove_duplicates()
                self.table_model.layoutChanged.emit()
                
                # 更新状态栏
                self.update_status_message()
                
                QMessageBox.information(self, "删除完成", f"成功删除{removed_count}个重复记录。")
            except Exception as e:
                QMessageBox.critical(self, "删除错误", f"删除过程中发生错误：{str(e)}")
    
    def refresh_data(self):
        """
        刷新表格数据
        """
        self.table_model.layoutChanged.emit()
        self.update_status_message()
    
    def update_progress(self, value):
        """
        更新进度条
        
        Args:
            value (int): 进度值（0-100）
        """
        self.progress_bar.setValue(value)
        QApplication.processEvents()  # 确保UI更新 
    
    def clear_data(self):
        """
        清空数据，提供两个选项：全部清空或只清空本次导入
        """
        # 检查是否有数据
        total_count = self.data_manager.get_count()
        if total_count == 0:
            QMessageBox.information(self, "无数据", "当前没有任何数据，无需清空。")
            return
        
        # 检查是否有最近导入的数据
        has_last_import, last_import_count = self.data_manager.has_last_import()
        
        # 创建消息框，提供选项
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("清空数据")
        msg_box.setText("请选择要清空的数据范围：")
        
        # 添加按钮
        all_button = msg_box.addButton("清空所有数据", QMessageBox.DestructiveRole)
        
        # 只有当有最近导入的数据时，才显示清空本次导入的选项
        last_import_button = None
        if has_last_import:
            last_import_button = msg_box.addButton(f"仅清空本次导入的数据({last_import_count}条)", QMessageBox.ActionRole)
        
        cancel_button = msg_box.addButton("取消", QMessageBox.RejectRole)
        
        # 设置默认按钮
        msg_box.setDefaultButton(cancel_button)
        
        # 执行消息框
        msg_box.exec_()
        
        # 获取点击的按钮
        clicked_button = msg_box.clickedButton()
        
        if clicked_button == cancel_button:
            # 用户取消了操作
            return
        
        try:
            if clicked_button == all_button:
                # 清空所有数据
                # 再次确认
                reply = QMessageBox.question(
                    self, 
                    "确认清空所有数据", 
                    f"确定要清空所有 {total_count} 条记录吗？此操作不可恢复。",
                    QMessageBox.Yes | QMessageBox.No, 
                    QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    count = self.data_manager.clear_all_data()
                    QMessageBox.information(self, "清空完成", f"成功清空 {count} 条记录。")
            
            elif has_last_import and clicked_button == last_import_button:
                # 清空本次导入的数据
                count = self.data_manager.clear_last_import()
                QMessageBox.information(self, "清空完成", f"成功清空本次导入的 {count} 条记录。")
            
            # 刷新表格
            self.table_model.layoutChanged.emit()
            
            # 更新状态栏
            self.update_status_message()
                
        except Exception as e:
            QMessageBox.critical(self, "清空错误", f"清空数据过程中发生错误：{str(e)}")
    
    def closeEvent(self, event):
        """
        窗口关闭事件，保存数据
        """
        # 保存数据
        if self.data_manager.save_data():
            # 接受关闭事件
            event.accept()
        else:
            # 保存失败，提示用户
            reply = QMessageBox.question(
                self, 
                "保存失败", 
                "数据保存失败，确定要关闭程序吗？未保存的数据将丢失。",
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
    
    def create_menus(self):
        """
        创建菜单
        """
        # 创建菜单栏
        menubar = self.menuBar()
        
        # 创建数据管理菜单
        data_menu = menubar.addMenu("数据管理")
        
        # 添加查看历史记录菜单项
        view_history_action = QAction("查看历史记录统计", self)
        view_history_action.triggered.connect(self.view_history_stats)
        data_menu.addAction(view_history_action)
        
        # 添加清空历史记录菜单项
        clear_history_action = QAction("清空历史记录", self)
        clear_history_action.triggered.connect(self.clear_history)
        data_menu.addAction(clear_history_action)
    
    def view_history_stats(self):
        """
        查看历史记录统计
        """
        history_count = len(self.data_manager.history_records)
        current_count = self.data_manager.get_count()
        
        msg = f"历史记录统计:\n"
        msg += f"- 历史记录总数: {history_count} 条\n"
        msg += f"- 当前会话记录: {current_count} 条\n\n"
        msg += "提示: 历史记录仅用于检测重复项，不会显示在界面上或导出。"
        
        QMessageBox.information(self, "历史记录统计", msg)
    
    def clear_history(self):
        """
        清空历史记录
        """
        history_count = len(self.data_manager.history_records)
        
        if history_count == 0:
            QMessageBox.information(self, "无历史记录", "当前没有任何历史记录，无需清空。")
            return
        
        reply = QMessageBox.question(
            self, 
            "确认清空历史记录", 
            f"确定要清空所有历史记录吗？这将删除 {history_count} 条历史记录。\n"
            "清空后将无法检测之前导入过的重复项，但不会影响当前已导入的数据。",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                count = self.data_manager.clear_history()
                QMessageBox.information(self, "清空完成", f"成功清空 {count} 条历史记录。")
                
                # 更新状态栏
                self.update_status_message()
            except Exception as e:
                QMessageBox.critical(self, "清空错误", f"清空历史记录过程中发生错误：{str(e)}")
    
    def update_status_message(self):
        """
        更新状态栏消息
        """
        # 获取记录总数和重复数
        current_count = self.data_manager.get_count()
        duplicates = self.data_manager.get_duplicates()
        duplicate_count = len(duplicates)
        
        # 获取历史记录数
        history_count = len(self.data_manager.history_records)
        
        # 检查是否有最近导入的数据
        has_last_import, last_import_count = self.data_manager.has_last_import()
        
        # 更新状态栏消息
        if current_count > 0:
            message = f"当前: {current_count} 条记录，其中 {duplicate_count} 条重复"
            if has_last_import:
                message += f"，最近导入 {last_import_count} 条"
            message += f" | 历史: {history_count} 条"
            self.status_bar.showMessage(message)
        else:
            self.status_bar.showMessage(f"准备就绪 | 历史记录: {history_count} 条") 