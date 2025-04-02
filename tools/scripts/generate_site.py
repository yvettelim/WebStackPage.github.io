import os
import re
import json
from datetime import datetime
from urllib.parse import urljoin
import pandas as pd

def read_markdown_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

def parse_markdown_tables(content):
    sections = {}
    current_section = None
    
    lines = content.split('\n')
    for line in lines:
        section_match = re.match(r'^## \d+\. (.+) \((.+)\)$', line)
        if section_match:
            current_section = section_match.group(1)
            sections[current_section] = {
                'title_en': section_match.group(2),
                'items': []
            }
            continue
            
        if '|' not in line or '---' in line or '网站名称' in line:
            continue
            
        if current_section and '|' in line:
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if len(cells) == 5:
                item = {
                    'name': cells[0],
                    'name_en': cells[1],
                    'url': cells[2],
                    'description': cells[3],
                    'description_en': cells[4]
                }
                sections[current_section]['items'].append(item)
    
    return sections

def generate_sidebar_html(sections):
    sidebar_html = '''<ul id="main-menu" class="main-menu">'''
    
    for section_name, section_data in sections.items():
        section_id = section_name.replace(' ', '_')
        sidebar_html += f'''
        <li>
            <a href="#{section_id}" class="smooth">
                <i class="linecons-star"></i>
                <span class="title">{section_name}</span>
            </a>
        </li>
        '''
    
    sidebar_html += '</ul>'
    return sidebar_html

def generate_content_html(sections):
    content_html = '<div class="main-content-inner">'
    
    for section_name, section_data in sections.items():
        section_id = section_name.replace(' ', '_')
        content_html += f'''
            <h4 class="text-gray"><i class="linecons-tag" style="margin-right: 7px;" id="{section_id}"></i>{section_name}</h4>
            <div class="row">
        '''
        
        for item in section_data['items']:
            logo_path = f"../assets/images/logos/{item['name']}.png"
            content_html += f'''
                <div class="col-sm-3">
                    <div class="xe-widget xe-conversations box2 label-info" onclick="window.open('{item['url']}', '_blank')" data-toggle="tooltip" data-placement="bottom" title="" data-original-title="{item['url']}">
                        <div class="xe-comment-entry">
                            <a class="xe-user-img">
                                <img src="{logo_path}" class="img-circle" width="40">
                            </a>
                            <div class="xe-comment">
                                <a href="#" class="xe-user-name overflowClip_1">
                                    <strong>{item['name']}</strong>
                                </a>
                                <p class="overflowClip_2">{item['description']}</p>
                            </div>
                        </div>
                    </div>
                </div>
            '''
        
        content_html += '''
            </div>
            <br />
        '''
    
    content_html += '</div>'
    return content_html

def generate_header_html():
    return '''
    <div class="nav-header">
        <div class="nav-brand">
            <img src="../assets/images/logo@2x.png" class="logo normal" alt="logo">
            <img src="../assets/images/logo-collapsed@2x.png" class="logo-collapsed" alt="logo">
        </div>
    </div>
    '''

def generate_language_switch_html():
    return '''
    <ul class="nav navbar-nav navbar-right">
        <li>
            <a href="../cn/index.html">
                <img src="../assets/images/flags/flag-cn.png" height="16" width="16">
            </a>
        </li>
        <li>
            <a href="../en/index.html">
                <img src="../assets/images/flags/flag-us.png" height="16" width="16">
            </a>
        </li>
    </ul>
    '''

def update_html_file(input_file, output_file, sections):
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 生成侧边栏HTML
    sidebar_html = generate_sidebar_html(sections)
    
    # 生成内容HTML
    content_html = generate_content_html(sections)
    
    # 保持原始head内容
    head_content = re.search('<head>(.*?)</head>', content, re.DOTALL).group(1)
    
    # 更新页面内容
    new_content = f'''<!DOCTYPE html>
<html lang="zh">
<head>
{head_content}
</head>

<body class="page-body">
    <div class="page-container">
        <div class="sidebar-menu toggle-others fixed">
            <div class="sidebar-menu-inner">
                <header class="logo-env">
                    <!-- logo -->
                    <div class="logo">
                        <a href="index.html" class="logo-expanded">
                            <img src="../assets/images/logo@2x.png" width="100%" alt="" />
                        </a>
                        <a href="index.html" class="logo-collapsed">
                            <img src="../assets/images/logo-collapsed@2x.png" width="40" alt="" />
                        </a>
                    </div>
                    <div class="mobile-menu-toggle visible-xs">
                        <a href="#" data-toggle="mobile-menu">
                            <i class="fa-bars"></i>
                        </a>
                    </div>
                </header>
                {sidebar_html}
            </div>
        </div>
        
        <div class="main-content">
            <nav class="navbar user-info-navbar" role="navigation">
                <!-- User Info, Notifications and Menu Bar -->
                <!-- Left links for user info navbar -->
                <ul class="user-info-menu left-links list-inline list-unstyled">
                    <li class="hidden-sm hidden-xs">
                        <a href="#" data-toggle="sidebar">
                            <i class="fa-bars"></i>
                        </a>
                    </li>
                </ul>
                <ul class="user-info-menu right-links list-inline list-unstyled">
                    <li>
                        <a href="../cn/index.html">
                            <img src="../assets/images/flags/flag-cn.png" width="16" height="16" />
                        </a>
                    </li>
                    <li>
                        <a href="../en/index.html">
                            <img src="../assets/images/flags/flag-us.png" width="16" height="16" />
                        </a>
                    </li>
                </ul>
            </nav>
            {content_html}
        </div>
    </div>

    <!-- Bottom Scripts -->
    <script src="../assets/js/bootstrap.min.js"></script>
    <script src="../assets/js/TweenMax.min.js"></script>
    <script src="../assets/js/resizeable.js"></script>
    <script src="../assets/js/joinable.js"></script>
    <script src="../assets/js/xenon-api.js"></script>
    <script src="../assets/js/xenon-toggles.js"></script>
    <script src="../assets/js/xenon-custom.js"></script>
</body>
</html>'''
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(new_content)

def generate_sitemap(sections, base_url):
    sitemap = '''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
'''
    
    # 添加首页
    sitemap += f'''
    <url>
        <loc>{base_url}</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>
'''
    
    # 添加中文版和英文版
    for lang in ['cn', 'en']:
        sitemap += f'''
    <url>
        <loc>{urljoin(base_url, f'{lang}/index.html')}</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.9</priority>
    </url>
'''
    
    sitemap += '</urlset>'
    return sitemap

def generate_robots_txt(base_url):
    robots_content = f'''User-agent: *
Allow: /
Sitemap: {urljoin(base_url, 'sitemap.xml')}'''
    
    with open('../../robots.txt', 'w', encoding='utf-8') as f:
        f.write(robots_content)

def main():
    # 读取markdown文件
    md_content = read_markdown_content('../data/comprehensive-nav-resource-tables.md')
    
    # 解析内容
    sections = parse_markdown_tables(md_content)
    
    # 更新HTML文件
    update_html_file(
        '../../cn/index.html',
        '../../cn/index.html',
        sections
    )
    
    # 生成sitemap
    generate_sitemap(sections, 'https://your-domain.com')
    
    # 生成robots.txt
    generate_robots_txt('https://your-domain.com')
    
    print("网站内容已更新完成！")

if __name__ == '__main__':
    main() 