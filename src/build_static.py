# -*- coding: utf-8 -*-
"""
自定义静态文件构建脚本 - 生成所有页面（首页+文章列表+文章详情）
"""
import os
import sys
import re
import shutil
import importlib.util
import json

here = os.path.dirname(os.path.abspath(__file__))
os.chdir(here)
BASE_DIR = os.path.dirname(here)
static_dir = BASE_DIR
print(f"将在项目根目录 {static_dir} 生成静态文件")

def fix_paths(html, depth):
    """将 Flask 绝对路径转为相对路径
    depth=0(root): /fonts/ → ./fonts/, /article/slug → articles/slug/
    depth=1(articles/): /fonts/ → ../fonts/, /article/slug → ./slug/
    depth=2(articles/slug/): /fonts/ → ../../fonts/, /article/slug → ../slug/
    """
    p = '../' * depth
    # 文章详情链接: /article/slug → 相对路径
    if depth == 0:
        ap = "articles/"
    elif depth == 1:
        ap = "./"
    else:
        ap = "../"
    # CSS url() 中的路径
    html = re.sub(r"url\('/fonts/", f"url('{p}fonts/", html)
    html = re.sub(r"url\('/content/", f"url('{p}content/", html)
    # HTML href - 文章详情链接
    html = re.sub(r'href="/article/([^"\'>\s]+)"', f'href="{ap}\\1/"', html)
    # HTML href - 文章列表
    if depth >= 1:
        html = re.sub(r'href="/articles"', f'href="{ap}"', html)
    else:
        html = re.sub(r'href="/articles"', f'href="{p}articles/"', html)
    # HTML href - 首页
    html = re.sub(r'href="/"', f'href="{p}"', html)
    return html

def get_articles():
    """从 app.py 中复用获取文章列表的逻辑"""
    arts = []
    ads = os.path.join(BASE_DIR, 'articles')
    if not os.path.exists(ads):
        return arts
    for f in sorted(os.listdir(ads)):
        if not f.endswith('.md'):
            continue
        slug = f[:-3]
        title = slug
        fp = os.path.join(ads, f)
        try:
            with open(fp, 'r', encoding='utf-8') as fh:
                for line in fh:
                    s = line.strip()
                    if s.startswith('# ') and not s.startswith('## '):
                        title = s[2:].strip()
                        break
        except:
            pass
        arts.append({'title': title, 'slug': slug})
    return arts

def generate_page(client, route, output_path, depth):
    """生成单个静态页面并进行路径修复"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(f"  请求 {route} ...", end=' ')
    resp = client.get(route)
    if resp.status_code != 200:
        print(f"失败 (HTTP {resp.status_code})")
        return False
    html = resp.data.decode('utf-8')
    html = fix_paths(html, depth)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"→ {output_path}")
    return True

# 读取配置
config_path = os.path.join(BASE_DIR, 'config', 'config.json')
default_config_path = os.path.join(BASE_DIR, 'default', 'default_config.json')
background_image = 'background.jpg'
if os.path.exists(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    background_image = config.get('background', {}).get('image', 'background.jpg')
else:
    print("警告：未找到config.json文件")
    if os.path.exists(default_config_path):
        shutil.copy2(default_config_path, config_path)
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        background_image = config.get('background', {}).get('image', 'background.jpg')
        if not os.path.exists(os.path.join(BASE_DIR, 'content', background_image)) and \
           os.path.exists(os.path.join(BASE_DIR, 'default', background_image)):
            os.makedirs(os.path.join(BASE_DIR, 'content'), exist_ok=True)
            shutil.copy2(os.path.join(BASE_DIR, 'default', background_image),
                        os.path.join(BASE_DIR, 'content', background_image))

# 导入app.py
print("正在准备生成静态文件...")
spec = importlib.util.spec_from_file_location("app", os.path.join(here, "app.py"))
app_module = importlib.util.module_from_spec(spec)
sys.modules["app"] = app_module
spec.loader.exec_module(app_module)

if not hasattr(app_module, 'app'):
    print("错误：app.py中未找到app实例")
    sys.exit(1)

client = app_module.app.test_client()

# === 1. 生成首页 index.html (depth=0) ===
print("\n=== 生成首页 ===")
if generate_page(client, '/', os.path.join(static_dir, 'index.html'), 0):
    print("首页生成成功")

# === 2. 生成文章列表 articles/index.html (depth=1) ===
print("\n=== 生成文章列表 ===")
art_dir = os.path.join(static_dir, 'articles')
os.makedirs(art_dir, exist_ok=True)
if generate_page(client, '/articles', os.path.join(art_dir, 'index.html'), 1):
    print("文章列表生成成功")

# === 3. 生成每篇文章 articles/<slug>/index.html (depth=2) ===
print("\n=== 生成文章详情 ===")
articles = get_articles()
if not articles:
    print("没有找到任何文章")
else:
    for art in articles:
        slug = art['slug']
        slug_dir = os.path.join(art_dir, slug)
        os.makedirs(slug_dir, exist_ok=True)
        if generate_page(client, f'/article/{slug}',
                        os.path.join(slug_dir, 'index.html'), 2):
            print(f"    文章 [{art['title']}] 生成成功")

# === 4. 复制静态资源 ===
print("\n=== 复制静态资源 ===")
# 背景图片
content_dir = os.path.join(static_dir, 'content')
os.makedirs(content_dir, exist_ok=True)
for fn in [background_image]:
    src = os.path.join(BASE_DIR, 'content', fn)
    if not os.path.exists(src):
        src = os.path.join(BASE_DIR, 'default', fn)
    if os.path.exists(src):
        dst = os.path.join(content_dir, fn)
        if not os.path.normpath(src) == os.path.normpath(dst):
            shutil.copy(src, dst)
            print(f"  content/{fn} 已复制")
    else:
        print(f"  警告：未找到 {fn}")

# 复制 content 下其他文件（如图片）
for fn in os.listdir(os.path.join(BASE_DIR, 'content')):
    if fn != background_image:
        src = os.path.join(BASE_DIR, 'content', fn)
        dst = os.path.join(content_dir, fn)
        if os.path.isfile(src) and not os.path.normpath(src) == os.path.normpath(dst):
            shutil.copy(src, dst)
            print(f"  content/{fn} 已复制")

# fonts 目录
fonts_dir = os.path.join(static_dir, 'fonts')
if not os.path.exists(fonts_dir):
    src_fonts = os.path.join(BASE_DIR, 'fonts')
    if os.path.exists(src_fonts):
        shutil.copytree(src_fonts, fonts_dir, dirs_exist_ok=True)
        print(f"  fonts/ 已复制")

print("\n✅ 全部完成！")
print(f"\n生成的静态文件结构:")
print(f"  {os.path.join(static_dir, 'index.html')}  (首页)")
print(f"  {os.path.join(art_dir, 'index.html')}  (文章列表)")
for art in articles:
    print(f"  {os.path.join(art_dir, art['slug'], 'index.html')}  (文章: {art['title']})")
print(f"  {os.path.join(content_dir, '...')}  (资源文件)")
print(f"  {os.path.join(fonts_dir, '...')}  (字体文件)")
print(f"\n已将 .nojekyll 写入项目根目录")
# 写入 .nojekyll（确保 GitHub Pages 正确处理 fonts/ 等目录）
with open(os.path.join(static_dir, '.nojekyll'), 'w') as f:
    f.write('')
