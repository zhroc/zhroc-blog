#!/usr/bin/env python3
"""
Hugo WOFF2 子集生成工具 (增强进度显示版)
功能：
1. 实时显示每个步骤的进度
2. 直接处理 WOFF2 格式字体文件
3. 自动运行 Hugo 构建
"""

import os
import sys
import glob
import yaml
import subprocess
from fontTools.subset import Subsetter
from fontTools.ttLib import TTFont, TTLibError

# === 配置区 ===
CONFIG_FILE = "../config.yml"
FONT_SOURCE = "../static/fonts/LXGWWenKaiLite-Bold.woff2"
OUTPUT_DIR = "../static/fonts"
OUTPUT_NAME = "LXGWBold-subset"
HUGO_ARGS = ["--minify", "--cleanDestinationDir"]
# ==============

def print_step(step, status="开始"):
    """格式化打印步骤信息"""
    print(f"\n▶ [{step}] {status}...")

def load_hugo_config():
    """加载并验证Hugo配置"""
    print_step("配置检查")
    try:
        print(f"正在读取配置文件: {os.path.abspath(CONFIG_FILE)}")
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        print("✓ 配置文件验证通过")
        return config
    except Exception as e:
        print(f"× 配置读取失败: {str(e)}")
        sys.exit(1)

def run_hugo_build():
    """执行Hugo构建并显示进度（保留实时输出）"""
    print_step("Hugo构建")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        print(f"工作目录: {project_root}")
        print("执行命令: hugo " + " ".join(HUGO_ARGS))
        
        # 关键修改：移除 capture_output，让Hugo直接输出到终端
        subprocess.run(
            ["hugo"] + HUGO_ARGS,
            cwd=project_root,
            check=True
        )
        
        print("✓ 构建成功完成")
    except subprocess.CalledProcessError as e:
        print(f"× 构建失败: {e.stderr if e.stderr else '未知错误'}")
        sys.exit(1)

def extract_chars():
    """提取字符并显示统计信息（过滤Emoji）"""
    print_step("字符提取")
    char_count = 0
    file_count = 0
    chars = set()
    
    def is_emoji(char):
        """判断字符是否为Emoji（简化版）"""
        try:
            cp = ord(char)
            # 表情符号 # 符号和象形文字 # 交通和地图符号 # 杂项符号
            return (cp >= 0x1F600 and cp <= 0x1F64F) or (cp >= 0x1F300 and cp <= 0x1F5FF) or (cp >= 0x1F680 and cp <= 0x1F6FF) or (cp >= 0x2600 and cp <= 0x26FF)       
        except:
            return False
    
    try:
        for html in glob.glob("../public/**/*.html", recursive=True):
            try:
                with open(html, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    # 过滤Emoji并统计
                    filtered = [c for c in content if not is_emoji(c)]
                    chars.update(filtered)
                    char_count += len(content)
                    file_count += 1
                    if file_count % 10 == 0:
                        print(f"已扫描 {file_count} 个文件，有效字符 {len(chars)}", end='\r')
            except UnicodeDecodeError:
                print(f"\n! 跳过非UTF-8文件: {html}")
            except Exception as e:
                print(f"\n! 文件 {html} 读取异常: {str(e)}")
                continue
        
        print(f"\n✓ 完成扫描 {file_count} 个HTML文件")
        print(f"发现总字符数: {char_count}")
        print(f"唯一有效字符数: {len(chars)} (已过滤Emoji)")
        return ''.join(sorted(chars))
    except Exception as e:
        print(f"\n× 提取失败: {str(e)}")
        sys.exit(1)

def generate_woff2(text):
    """生成字体子集并显示处理进度"""
    print_step("字体子集化")
    try:
        # 显示输入输出信息
        print(f"输入字体: {os.path.abspath(FONT_SOURCE)}")
        print(f"输出路径: {os.path.abspath(OUTPUT_DIR)}")
        print(f"字符数量: {len(text)}")
        
        # 准备输出目录
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        print("✓ 输出目录就绪")

        # 字体处理
        print("正在加载WOFF2字体...")
        font = TTFont(FONT_SOURCE)
        font.flavor = None
        
        print("正在生成子集...")
        subsetter = Subsetter()
        subsetter.populate(text=text)
        subsetter.subset(font)
        
        # 保存结果
        output_path = f"{OUTPUT_DIR}/{OUTPUT_NAME}.woff2"
        font.flavor = "woff2"
        font.save(output_path)
        
        print(f"✓ 子集生成完成: {output_path}")
        print(f"文件大小: {os.path.getsize(output_path)/1024:.1f} KB")
    except TTLibError as e:
        print(f"× 字体处理错误: {str(e)}")
        sys.exit(1)

def main():
    print("="*50)
    print("Hugo 字体子集生成工具")
    print("="*50)
    
    # 验证阶段
    if not os.path.exists(FONT_SOURCE):
        print(f"× 错误: 字体文件不存在 - {os.path.abspath(FONT_SOURCE)}")
        sys.exit(1)
    
    _ = load_hugo_config()
    
    # 执行流程
    run_hugo_build()
    unique_chars = extract_chars()
    
    if not unique_chars:
        print("× 错误: 未提取到有效字符")
        sys.exit(1)
        
    generate_woff2(unique_chars)
    
    print("\n" + "="*50)
    print("✓ 所有步骤已完成!")
    print("="*50)

if __name__ == "__main__":
    main()