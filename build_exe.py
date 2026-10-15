import os
import sys
import subprocess
import shutil
from pathlib import Path

def create_exe():
    """
    创建可执行文件
    """
    print("开始创建TK达人管理系统可执行文件...")
    
    # 确保工作目录正确
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # 创建构建目录
    dist_dir = script_dir / "dist"
    build_dir = script_dir / "build"
    
    # 删除之前的构建文件
    if dist_dir.exists():
        print("正在清理之前的构建文件...")
        shutil.rmtree(dist_dir)
    if build_dir.exists():
        shutil.rmtree(build_dir)
    
    # 构建命令
    cmd = [
        "pyinstaller",
        "--name", "TK达人管理系统",
        "--windowed",  # 使用GUI模式，不显示控制台窗口
        "--onefile",   # 生成单个exe文件
        "--clean",     # 清理临时文件
        "main.py"
    ]
    
    # 执行构建
    print("正在打包可执行文件，这可能需要几分钟时间...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # 检查构建结果
    if result.returncode == 0:
        print("构建成功!")
        
        # 复制README文件到发布目录
        if (script_dir / "README.md").exists():
            shutil.copy(script_dir / "README.md", dist_dir / "使用说明.md")
        
        # 显示成功信息
        exe_path = dist_dir / "TK达人管理系统.exe"
        if exe_path.exists():
            print(f"\n可执行文件已创建: {exe_path}")
            print("\n您现在可以直接运行此exe文件，无需担心配置文件问题，程序会自动在用户主目录创建配置。")
        else:
            print("警告: 构建虽然成功，但找不到生成的exe文件。")
    else:
        print("构建失败。错误信息:")
        print(result.stdout)
        print(result.stderr)

if __name__ == "__main__":
    create_exe() 