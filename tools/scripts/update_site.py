import os
from generate_site import main as generate_site

def backup_files():
    """备份重要文件"""
    files_to_backup = [
        '../../cn/index.html',
        '../../en/index.html',
    ]
    
    for file_path in files_to_backup:
        if os.path.exists(file_path):
            backup_path = file_path + '.backup'
            print(f'备份文件: {file_path} -> {backup_path}')
            with open(file_path, 'r', encoding='utf-8') as source:
                with open(backup_path, 'w', encoding='utf-8') as target:
                    target.write(source.read())

def main():
    """主函数"""
    print('开始更新网站内容...')
    
    # 第一步：备份文件
    print('\n1. 备份原始文件...')
    backup_files()
    
    # 第二步：生成新内容
    print('\n2. 生成新的网站内容...')
    try:
        generate_site()
        print('✅ 网站内容更新成功！')
    except Exception as e:
        print('❌ 更新失败！错误信息：', str(e))
        print('提示：可以使用备份文件恢复原始内容')
        return
    
    print('''
完成！接下来您需要：
1. 检查 cn/index.html 确认内容是否正确
2. 如果内容有问题，可以用 .backup 文件恢复
3. 确认无误后，可以提交到 GitHub
    ''')

if __name__ == '__main__':
    main() 