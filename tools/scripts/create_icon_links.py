#!/usr/bin/env python3
import os
import shutil

# 图标对应关系：英文名称 -> 中文名称
icon_mappings = {
    "Microsoft Copilot": "微软Copilot",
    "Google Gemini": "Gemini",
    "MobanWang": "模板王",
    "Alibaba Cloud": "阿里云",
    "SEO Daily Tips": "SEO每天一贴",
    "Baidu Index": "百度指数",
    "Google Trends": "Google趋势",
    "5118 Data Analysis": "5118数据分析",
    "Chinaz": "站长之家",
    "IMOOC": "慕课网",
    "Runoob": "菜鸟教程",
    "Anthropic Claude": "Claude",
    "Google Search Console": "Search Console"
}

def main():
    # 图标目录路径
    icons_dir = "../../assets/images/logos"
    
    # 确保目录存在
    if not os.path.exists(icons_dir):
        print(f"错误：找不到图标目录 {icons_dir}")
        return
    
    # 为每个映射创建英文名称的图标文件（复制文件）
    for en_name, cn_name in icon_mappings.items():
        cn_icon_path = os.path.join(icons_dir, f"{cn_name}.png")
        en_icon_path = os.path.join(icons_dir, f"{en_name}.png")
        
        # 检查中文名称的图标是否存在
        if os.path.exists(cn_icon_path):
            # 检查英文名称的图标是否已存在
            if not os.path.exists(en_icon_path):
                try:
                    # 复制文件
                    shutil.copy2(cn_icon_path, en_icon_path)
                    print(f"已创建图标：{en_name}.png (从 {cn_name}.png 复制)")
                except Exception as e:
                    print(f"创建图标 {en_name}.png 时出错：{str(e)}")
            else:
                print(f"图标已存在：{en_name}.png")
        else:
            print(f"警告：找不到中文图标 {cn_name}.png")
    
    print("\n图标处理完成！")

if __name__ == "__main__":
    main() 