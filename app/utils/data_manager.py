import os
import json
import pandas as pd
import time
from datetime import datetime
import math
import pickle
from PyQt5.QtWidgets import QApplication
from app.utils.config_manager import ConfigManager


class DataManager:
    """
    TK达人数据管理器，负责处理数据的导入、导出和处理
    """
    
    def __init__(self):
        """
        初始化数据管理器
        """
        # 创建配置管理器
        self.config_manager = ConfigManager()
        
        # 历史记录列表（所有曾经导入过的数据）
        self.history_records = []
        
        # 当前会话记录列表（仅当前导入的数据）
        self.current_records = []
        
        # 记录用户名到索引的映射，便于快速查找重复
        self.username_index = {}
        
        # 记录最近导入的数据索引，用于清空本次导入
        self.last_import_indices = []
        
        # 尝试加载保存的历史数据
        self.load_data()
    
    def save_data(self):
        """
        保存历史数据到文件
        
        Returns:
            bool: 保存是否成功
        """
        try:
            # 获取数据文件路径
            data_file_path = self.config_manager.get_data_file_path()
            
            # 创建保存的数据对象（只保存历史记录）
            data = {
                "records": self.history_records,
                "timestamp": datetime.now().isoformat()
            }
            
            # 确保目录存在
            os.makedirs(os.path.dirname(data_file_path), exist_ok=True)
            
            # 保存数据
            with open(data_file_path, 'wb') as f:
                pickle.dump(data, f)
            
            return True
        except Exception as e:
            print(f"保存数据时出错: {str(e)}")
            return False
    
    def load_data(self):
        """
        从文件加载历史数据
        
        Returns:
            bool: 加载是否成功
        """
        # 获取数据文件路径
        data_file_path = self.config_manager.get_data_file_path()
        
        if not os.path.exists(data_file_path):
            return False
        
        try:
            # 加载数据
            with open(data_file_path, 'rb') as f:
                data = pickle.load(f)
            
            # 恢复历史记录
            self.history_records = data.get("records", [])
            
            # 当前会话记录初始为空
            self.current_records = []
            
            # 重建用户名索引（仅基于历史记录）
            self.rebuild_index()
            
            return True
        except Exception as e:
            print(f"加载数据时出错: {str(e)}")
            self.history_records = []
            self.current_records = []
            self.username_index = {}
            return False
    
    def rebuild_index(self):
        """
        重建用户名索引（基于历史记录）
        """
        self.username_index = {}
        # 使用历史记录重建索引，用于重复检测
        for record in self.history_records:
            username = record["username"]
            if username not in self.username_index:
                self.username_index[username] = True
    
    def import_files(self, file_paths, progress_callback=None):
        """
        导入多个表格文件
        
        Args:
            file_paths (list): 文件路径列表
            progress_callback (function, optional): 进度回调函数
            
        Returns:
            list: 重复的达人用户名列表
        """
        total_files = len(file_paths)
        duplicates = []
        
        # 记录导入前的记录数，用于标记本次导入的数据
        start_index = len(self.current_records)
        
        for i, file_path in enumerate(file_paths):
            try:
                # 读取文件
                sheet_data = self._read_file(file_path)
                
                # 处理表格数据
                file_duplicates = self._process_sheet_data(sheet_data)
                duplicates.extend(file_duplicates)
                
                # 更新进度
                if progress_callback:
                    progress = int((i + 1) / total_files * 100)
                    progress_callback(progress)
                
            except Exception as e:
                print(f"导入文件 {file_path} 时出错: {str(e)}")
                raise
        
        # 记录本次导入的索引范围
        end_index = len(self.current_records)
        if end_index > start_index:
            self.last_import_indices = list(range(start_index, end_index))
        else:
            self.last_import_indices = []
        
        # 导入完成后保存历史数据
        self.save_data()
        
        return duplicates
    
    def export_data(self, export_dir, records_per_file=50, export_duplicates=False, 
                   file_prefix="TK达人_", file_format="xlsx", progress_callback=None, export_username_only=False):
        """
        导出数据到多个表格文件，并在首次导出时记录时间
        
        Args:
            export_dir (str): 导出目录
            records_per_file (int): 每个文件包含的记录数
            export_duplicates (bool): 是否导出重复记录
            file_prefix (str): 文件名前缀
            file_format (str): 文件格式（xlsx或xls或csv）
            progress_callback (function, optional): 进度回调函数
            export_username_only (bool): 是否只导出用户名字段
            
        Returns:
            int: 导出的文件数量
        """
        # 当前时间，用于记录导出时间
        current_time = datetime.now()
        data_changed = False
        
        # 筛选记录并为未记录时间的记录设置时间
        export_records = []
        for record in self.current_records:
            # 如果没有记录时间或时间为空，则设置为当前时间
            if "import_time" not in record or not record["import_time"]:
                record["import_time"] = current_time
                data_changed = True
                
            if export_duplicates or not record["is_duplicate"]:
                export_records.append(record)
        
        # 如果数据有变化，更新历史记录并保存数据
        if data_changed:
            self.update_history_records()
            self.save_data()
            
        # 计算需要多少个文件
        total_records = len(export_records)
        file_count = math.ceil(total_records / records_per_file)
        
        for i in range(file_count):
            # 计算当前文件的记录范围
            start_idx = i * records_per_file
            end_idx = min((i + 1) * records_per_file, total_records)
            current_records = export_records[start_idx:end_idx]
            
            # 创建DataFrame
            if export_username_only:
                # 只导出用户名字段
                df = pd.DataFrame({
                    "达人用户名": [r["username"] for r in current_records]
                })
            else:
                # 导出所有字段
                df = pd.DataFrame({
                    "序号": range(1, len(current_records) + 1),
                    "达人用户名": [r["username"] for r in current_records],
                    "记录时间": [r["import_time"].strftime("%Y-%m-%d %H:%M:%S") for r in current_records],
                    "是否重复": ["是" if r["is_duplicate"] else "否" for r in current_records],
                    "备注": [r.get("remark", "") for r in current_records]
                })
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{file_prefix}{i+1}_{timestamp}.{file_format}"
            file_path = os.path.join(export_dir, filename)
            
            # 导出到文件
            if file_format == "csv":
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
            elif file_format == "xlsx":
                df.to_excel(file_path, index=False, engine="openpyxl")
            else:
                df.to_excel(file_path, index=False, engine="xlwt")
            
            # 更新进度
            if progress_callback:
                progress = int((i + 1) / file_count * 100)
                progress_callback(progress)
        
        return file_count
    
    def update_history_records(self):
        """
        将当前会话的记录更新到历史记录中
        """
        # 遍历当前会话记录
        for record in self.current_records:
            username = record["username"]
            # 不重复添加到历史记录
            if not any(r["username"] == username for r in self.history_records):
                # 深拷贝记录，避免引用问题
                history_record = record.copy()
                self.history_records.append(history_record)
    
    def get_count(self):
        """
        获取当前会话记录总数
        
        Returns:
            int: 记录总数
        """
        return len(self.current_records)
    
    def get_record(self, index):
        """
        获取指定索引的当前会话记录
        
        Args:
            index (int): 记录索引
            
        Returns:
            dict: 记录字典
        """
        if 0 <= index < len(self.current_records):
            return self.current_records[index]
        return {}
    
    def get_duplicates(self):
        """
        获取当前会话中重复的达人用户名
        
        Returns:
            list: 重复的达人用户名列表
        """
        duplicates = []
        for record in self.current_records:
            if record["is_duplicate"]:
                duplicates.append(record["username"])
        return duplicates
    
    def remove_duplicates(self):
        """
        删除当前会话中重复的达人用户名记录
        
        Returns:
            int: 删除的记录数量
        """
        # 记录要删除的索引
        to_remove = []
        
        # 查找重复项
        for i, record in enumerate(self.current_records):
            if record["is_duplicate"]:
                to_remove.append(i)
        
        # 删除重复记录（从后往前删除，避免索引变化）
        to_remove.sort(reverse=True)
        for idx in to_remove:
            del self.current_records[idx]
        
        # 清空最近导入的索引，因为索引已经改变
        self.last_import_indices = []
        
        return len(to_remove)
    
    def clear_last_import(self):
        """
        清空最近一次导入的数据
        
        Returns:
            int: 清空的记录数量
        """
        # 如果没有最近导入的数据，返回0
        if not self.last_import_indices:
            return 0
        
        # 复制一份列表，并按降序排序，以便从后往前删除
        indices_to_remove = sorted(self.last_import_indices, reverse=True)
        
        # 删除记录
        for idx in indices_to_remove:
            if 0 <= idx < len(self.current_records):
                del self.current_records[idx]
        
        # 清空最近导入的索引
        count = len(self.last_import_indices)
        self.last_import_indices = []
        
        return count
    
    def clear_all_data(self):
        """
        清空当前会话的所有数据（不清空历史记录）
        
        Returns:
            int: 清空的记录数量
        """
        count = len(self.current_records)
        self.current_records = []
        self.last_import_indices = []
        
        return count
    
    def clear_history(self):
        """
        清空所有历史记录
        
        Returns:
            int: 清空的记录数量
        """
        count = len(self.history_records)
        self.history_records = []
        self.username_index = {}
        
        # 保存更改
        self.save_data()
        
        return count
    
    def has_last_import(self):
        """
        检查是否有最近导入的数据
        
        Returns:
            bool: 是否有最近导入的数据
            int: 最近导入的数据条数
        """
        count = len(self.last_import_indices)
        return count > 0, count
    
    def _process_sheet_data(self, sheet_data):
        """
        处理表格数据，添加到当前会话记录列表
        
        Args:
            sheet_data (list): 表格数据列表
            
        Returns:
            list: 重复的达人用户名列表
        """
        duplicates = []
        
        for username in sheet_data:
            # 检查是否在历史记录或当前会话中重复
            is_duplicate = username in self.username_index or any(r["username"] == username for r in self.current_records)
            
            if is_duplicate:
                duplicates.append(username)
            
            # 添加记录到当前会话 - 不在导入时设置时间，而是在导出时设置
            record = {
                "username": username,
                "import_time": None,  # 初始设置为None，在首次导出时设置时间
                "is_duplicate": is_duplicate,
                "remark": "重复导入" if is_duplicate else ""
            }
            
            self.current_records.append(record)
        
        return duplicates
    
    def _read_file(self, file_path):
        """
        读取文件内容
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            list: 表格数据列表
        """
        # 获取文件扩展名
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            # 根据文件类型选择读取方法
            if file_ext == ".csv":
                return self._read_csv_file(file_path)
            else:
                return self._read_excel_file(file_path)
            
        except Exception as e:
            print(f"读取文件 {file_path} 时出错: {str(e)}")
            raise
    
    def _read_csv_file(self, file_path):
        """
        读取CSV文件内容
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            list: 表格数据列表
        """
        try:
            # 尝试使用UTF-8编码读取
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            # 如果失败，尝试使用GB18030编码读取
            try:
                df = pd.read_csv(file_path, encoding='gb18030')
            except UnicodeDecodeError:
                # 最后尝试使用Latin-1编码
                df = pd.read_csv(file_path, encoding='latin-1')
        
        # 提取可能的达人用户名列
        sheet_data = []
        for _, row in df.iterrows():
            # 尝试查找用户名列
            username = None
            
            # 检查列名包含"用户名"或"达人"的列
            for col in df.columns:
                col_str = str(col).lower()
                if "用户名" in col_str or "达人" in col_str:
                    username = str(row[col]).strip()
                    break
            
            # 如果没找到，尝试使用第一列非空值
            if not username:
                for col in df.columns:
                    value = row[col]
                    if pd.notna(value) and str(value).strip():
                        username = str(value).strip()
                        break
            
            if username:
                sheet_data.append(username)
        
        return sheet_data
    
    def _read_excel_file(self, file_path):
        """
        读取Excel文件内容
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            list: 表格数据列表
        """
        # 获取文件扩展名
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # 根据文件类型选择引擎
        engine = "openpyxl" if file_ext == ".xlsx" else "xlrd"
        
        try:
            # 读取Excel文件
            df = pd.read_excel(file_path, engine=engine)
            
            # 提取可能的达人用户名列
            sheet_data = []
            for _, row in df.iterrows():
                # 尝试查找用户名列
                username = None
                
                # 检查列名包含"用户名"或"达人"的列
                for col in df.columns:
                    col_str = str(col).lower()
                    if "用户名" in col_str or "达人" in col_str:
                        username = str(row[col]).strip()
                        break
                
                # 如果没找到，尝试使用第一列非空值
                if not username:
                    for col in df.columns:
                        value = row[col]
                        if pd.notna(value) and str(value).strip():
                            username = str(value).strip()
                            break
                
                if username:
                    sheet_data.append(username)
            
            return sheet_data
            
        except Exception as e:
            print(f"读取Excel文件 {file_path} 时出错: {str(e)}")
            raise 

    def sort_by(self, field, ascending=True):
        """
        按指定字段排序当前会话记录
        
        Args:
            field (str): 排序字段
            ascending (bool): 是否升序
        """
        if field == "id":
            # ID排序实际上是重置为原始顺序
            pass
        else:
            # 按字段排序
            reverse = not ascending
            self.current_records.sort(key=lambda x: x.get(field, ""), reverse=reverse) 