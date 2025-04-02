# tools/scripts/download_icons.py

import os
import pandas as pd
import requests
from pathlib import Path
from PIL import Image
import io
import re
import logging
import shutil
from datetime import datetime


class IconDownloader:
    def __init__(self):
        # 设置日志
        logging.basicConfig(
            filename='icon_download.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

        # 获取项目根目录
        self.script_dir = Path(__file__).parent
        self.project_root = self.script_dir.parent.parent

        # 设置各种路径
        self.md_file = self.project_root / "tools" / "data" / "comprehensive-nav-resource-tables.md"
        self.temp_icons_dir = self.project_root / "tools" / "data" / "temp_icons"
        self.final_icons_dir = self.project_root / "assets" / "images" / "logos"

        # 创建必要的目录
        self.temp_icons_dir.mkdir(parents=True, exist_ok=True)
        self.final_icons_dir.mkdir(parents=True, exist_ok=True)

        logging.info(f"临时目录: {self.temp_icons_dir}")
        logging.info(f"最终目录: {self.final_icons_dir}")

    def clean_directories(self):
        """清理目录"""
        print("\n清理目录...")

        # 清理临时目录
        if self.temp_icons_dir.exists():
            shutil.rmtree(self.temp_icons_dir)
            self.temp_icons_dir.mkdir(parents=True)
            print("✓ 已清理临时目录")

        # 清理最终目录
        if self.final_icons_dir.exists():
            # 创建备份目录
            backup_dir = self.final_icons_dir.parent / f"logos_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copytree(self.final_icons_dir, backup_dir)
            print(f"✓ 已备份原始图标到: {backup_dir}")

            # 清理目录
            shutil.rmtree(self.final_icons_dir)
            self.final_icons_dir.mkdir(parents=True)
            print("✓ 已清理最终目录")

    def parse_markdown(self):
        """解析markdown文件，提取网站信息"""
        print("\n开始解析Markdown文件...")
        websites = []

        with open(self.md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 使用正则表达式匹配表格行
        pattern = r'\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|'
        matches = re.findall(pattern, content)

        for match in matches:
            # 跳过表头和分隔行
            if '---' in match[0] or '网站名称' in match[0]:
                continue

            website = {
                'name': match[0].strip(),
                'name_en': match[1].strip(),
                'url': match[2].strip(),
                'description': match[3].strip(),
                'description_en': match[4].strip()
            }
            websites.append(website)

        print(f"找到 {len(websites)} 个网站")
        return websites

    def get_favicon_url(self, url):
        """获取网站图标的URL"""
        # 移除URL末尾的斜杠和协议
        url = url.rstrip('/')
        domain = url.split('://')[-1]

        # 尝试不同的图标服务
        icon_urls = [
            f"https://www.google.com/s2/favicons?domain={domain}&sz=128",
            f"https://icon.horse/icon/{domain}",
            f"https://favicons.githubusercontent.com/{domain}",
            f"{url}/apple-touch-icon.png",
            f"{url}/apple-touch-icon-precomposed.png",
            f"{url}/favicon-196x196.png",
            f"{url}/favicon-128x128.png",
            f"{url}/favicon-96x96.png",
            f"{url}/favicon-32x32.png",
            f"{url}/favicon.png",
            f"{url}/favicon.ico"
        ]
        return icon_urls

    def download_icon(self, url, site_name):
        """下载单个网站的图标"""
        print(f"\n尝试下载 {site_name} 的图标...")
        logging.info(f"开始下载 {site_name} 的图标")

        icon_urls = self.get_favicon_url(url)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        for icon_url in icon_urls:
            try:
                print(f"尝试: {icon_url}")
                response = requests.get(icon_url, headers=headers, timeout=10)

                if response.status_code == 200:
                    try:
                        img = Image.open(io.BytesIO(response.content))

                        # 检查图片尺寸
                        if img.size[0] < 32 or img.size[1] < 32:
                            print(f"图标太小 ({img.size[0]}x{img.size[1]}px)，尝试下一个源")
                            continue

                        # 保存为PNG格式
                        icon_path = self.temp_icons_dir / f"{site_name}.png"
                        img.save(icon_path, 'PNG')

                        print(f"✓ 成功下载并保存 {site_name} 的图标")
                        logging.info(f"成功下载 {site_name} 的图标: {icon_url}")
                        return icon_path
                    except Exception as e:
                        print(f"处理图片失败: {e}")
                        continue

            except Exception as e:
                print(f"下载失败: {e}")
                continue

        print(f"✗ 无法获取 {site_name} 的有效图标")
        logging.error(f"无法下载 {site_name} 的图标")
        return None

    def process_icon(self, icon_path):
        """处理图标尺寸"""
        try:
            with Image.open(icon_path) as img:
                # 转换为RGBA模式
                img = img.convert('RGBA')

                # 创建白色背景
                background = Image.new('RGBA', img.size, (255, 255, 255, 255))

                # 合并图片
                img = Image.alpha_composite(background, img)

                # 计算新尺寸，保持纵横比
                ratio = img.size[0] / img.size[1]
                if ratio > 1:
                    new_size = (120, int(120 / ratio))
                else:
                    new_size = (int(120 * ratio), 120)

                # 调整大小
                img = img.resize(new_size, Image.Resampling.LANCZOS)

                # 创建120x120的画布
                final_img = Image.new('RGBA', (120, 120), (255, 255, 255, 0))

                # 将调整后的图片居中放置
                x = (120 - new_size[0]) // 2
                y = (120 - new_size[1]) // 2
                final_img.paste(img, (x, y))

                # 保存
                final_img.save(icon_path, 'PNG')

                print(f"✓ 成功处理图标: {icon_path}")
                return True
        except Exception as e:
            print(f"✗ 处理图标失败: {e}")
            logging.error(f"处理图标失败 {icon_path}: {e}")
            return False

    def verify_icons(self):
        """验证所有图标"""
        print("\n验证图标文件:")
        for icon_file in self.final_icons_dir.glob("*.png"):
            try:
                with Image.open(icon_file) as img:
                    size_str = f"{img.size[0]}x{img.size[1]}px"
                    if img.size != (120, 120):
                        print(f"警告: {icon_file.name} 尺寸不正确 ({size_str})")
                    else:
                        print(f"✓ {icon_file.name}: {size_str}")
            except Exception as e:
                print(f"错误: {icon_file.name} - {e}")

    def run(self):
        """运行完整的下载和处理流程"""
        # 1. 清理目录
        self.clean_directories()

        # 2. 解析markdown
        websites = self.parse_markdown()

        # 3. 下载和处理图标
        success_count = 0
        total_count = len(websites)

        for i, website in enumerate(websites, 1):
            name = website['name']
            url = website['url']

            print(f"\n处理网站 ({i}/{total_count}): {name}")

            # 下载图标
            icon_path = self.download_icon(url, name)
            if icon_path and icon_path.exists():
                # 处理图标尺寸
                if self.process_icon(icon_path):
                    # 移动到最终目录
                    final_path = self.final_icons_dir / f"{name}.png"
                    icon_path.rename(final_path)
                    success_count += 1
                    print(f"✓ 完成处理 {name} 的图标")

        # 4. 验证结果
        self.verify_icons()

        # 5. 输出总结
        print(f"\n总结:")
        print(f"总计: {total_count} 个网站")
        print(f"成功: {success_count} 个")
        print(f"失败: {total_count - success_count} 个")

        logging.info(f"下载完成 - 总计: {total_count}, 成功: {success_count}, 失败: {total_count - success_count}")


if __name__ == "__main__":
    downloader = IconDownloader()
    downloader.run()