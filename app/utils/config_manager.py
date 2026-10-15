import os
import json
from pathlib import Path

class ConfigManager:
    """
    配置管理器，负责管理应用程序配置和数据文件路径
    """
    
    # 默认配置文件名
    CONFIG_FILENAME = 'tk_config.json'
    
    # 默认数据文件名
    DATA_FILENAME = 'tk_records.dat'
    
    def __init__(self):
        """
        初始化配置管理器
        """
        # 确定配置文件目录
        self.config_dir = self._get_config_dir()
        
        # 确保配置目录存在
        os.makedirs(self.config_dir, exist_ok=True)
        
        # 配置文件和数据文件的完整路径
        self.config_file_path = os.path.join(self.config_dir, self.CONFIG_FILENAME)
        self.data_file_path = os.path.join(self.config_dir, self.DATA_FILENAME)
        
        # 加载或创建默认配置
        self.config = self._load_config()
    
    def _get_config_dir(self):
        """
        获取配置文件目录
        
        Returns:
            str: 配置文件目录路径
        """
        # 使用用户主目录下的专用文件夹存储配置
        user_home = Path.home()
        return os.path.join(user_home, '.tk_manager')
    
    def _load_config(self):
        """
        加载配置文件，如果不存在则创建默认配置
        
        Returns:
            dict: 配置字典
        """
        if os.path.exists(self.config_file_path):
            try:
                with open(self.config_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置文件时出错: {str(e)}")
                # 如果加载失败，返回默认配置
        
        # 默认配置
        default_config = {
            'data_file_path': self.data_file_path,
            'max_records_per_export': 50,
            'default_export_format': 'xlsx',
            'default_export_prefix': 'TK达人_',
        }
        
        # 保存默认配置
        self.save_config(default_config)
        
        return default_config
    
    def save_config(self, config=None):
        """
        保存配置到文件
        
        Args:
            config (dict, optional): 配置字典，如果为None则保存当前配置
            
        Returns:
            bool: 保存是否成功
        """
        if config is not None:
            self.config = config
            
        try:
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存配置文件时出错: {str(e)}")
            return False
    
    def get_data_file_path(self):
        """
        获取数据文件路径
        
        Returns:
            str: 数据文件路径
        """
        return self.config.get('data_file_path', self.data_file_path)
    
    def get_config_value(self, key, default=None):
        """
        获取配置值
        
        Args:
            key (str): 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        return self.config.get(key, default)
    
    def set_config_value(self, key, value):
        """
        设置配置值
        
        Args:
            key (str): 配置键
            value: 配置值
            
        Returns:
            bool: 设置是否成功
        """
        self.config[key] = value
        return self.save_config() 