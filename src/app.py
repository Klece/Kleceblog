import os
import json
import markdown
import requests
import calendar
from flask import Flask, render_template, jsonify, send_from_directory, abort
from datetime import datetime
import shutil

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES_DIR = os.path.join(BASE_DIR, 'articles')

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, 'templates'))
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# 全局变量
config = None
skills_data = None
projects_data = None
pixel_text_data = None

# 读取配置文件
def load_all_configs():
    global config, skills_data, projects_data
    
    # 读取主配置
    try:
        with open(os.path.join(BASE_DIR, 'config', 'config.json'), 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        default_config_path = os.path.join(BASE_DIR, 'default', 'default_config.json')
        if os.path.exists(default_config_path):
            print(f"config.json不存在，从{default_config_path}复制默认配置")
            shutil.copy2(default_config_path, os.path.join(BASE_DIR, 'config', 'config.json'))
            with open(os.path.join(BASE_DIR, 'config', 'config.json'), 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if 'background' in config and 'image' in config['background']:
                background_image = config['background']['image']
                if not os.path.exists(os.path.join(BASE_DIR, 'content', background_image)) and os.path.exists(os.path.join('default', background_image)):
                    shutil.copy2(os.path.join('default', background_image), os.path.join(BASE_DIR, 'content', background_image))
        else:
            config = {
                "github_url": "https://github.com/example",
                "dark_mode": "auto",
                "name": "Example User",
                "bio": "Python Developer",
                "introduction_file": "content/Introduction.md",
                "theme": {
                    "primary_color": "#6a11cb",
                    "secondary_color": "#2575fc",
                    "dark_primary_color": "#a855f7",
                    "dark_secondary_color": "#60a5fa"
                },
                "background": {
                    "image": "content/background.jpg",
                    "blur": 4,
                    "overlay_opacity": 0.6,
                    "overlay_color": "#f3f4f6",
                    "dark_overlay_color": "#121212"
                },
                "contact": {
                    "qq": "",
                    "wechat": "",
                    "bilibili": "",
                    "douyin": "",
                    "xiaohongshu": ""
                }
            }
            with open(os.path.join(BASE_DIR, 'config', 'config.json'), 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
    
    # 读取技能配置
    try:
        with open(os.path.join(BASE_DIR, 'config', 'skills.json'), 'r', encoding='utf-8') as f:
            skills_data = json.load(f)
    except FileNotFoundError:
        skills_data = {"skills": []}
    
    # 读取项目配置
    try:
        with open(os.path.join(BASE_DIR, 'config', 'projects.json'), 'r', encoding='utf-8') as f:
            projects_data = json.load(f)
    except FileNotFoundError:
        projects_data = {"projects": []}
    
    # 读取像素文字配置
    try:
        with open(os.path.join(BASE_DIR, 'config', 'pixel-text.json'), 'r', encoding='utf-8') as f:
            pixel_text_data = json.load(f)
            print(f"成功读取像素文字配置，包含 {len(pixel_text_data)} 个字")
    except FileNotFoundError:
        pixel_text_data = {"我": {"width": 12, "height": 12, "pixels": []}, "爱": {"width": 12, "height": 12, "pixels": []}, "雨": {"width": 12, "height": 12, "pixels": []}, "云": {"width": 12, "height": 12, "pixels": []}}

# 模块加载时立即加载配置
load_all_configs()

# 读取本地Introduction.md文件
def get_introduction_content():
    try:
        introduction_file = os.path.join(BASE_DIR, config.get('introduction_file', 'content/Introduction.md'))
        if os.path.exists(introduction_file):
            with open(introduction_file, 'r', encoding='utf-8') as f:
                md_text = f.read()
                return markdown.markdown(
                    md_text,
                    extensions=['extra', 'codehilite', 'toc', 'tables', 'md_in_html'],
                    extension_configs={
                        'codehilite': {
                            'css_class': 'highlight',
                            'linenums': False
                        }
                    }
                )
    except Exception:
        pass
    return "<p>这个人很懒，什么都没有留下～</p>"

# 获取诗句列表
def get_poems():
    try:
        poems_file = os.path.join(BASE_DIR, 'config', 'poems.txt')
        if os.path.exists(poems_file):
            with open(poems_file, 'r', encoding='utf-8') as f:
                poems = [line.strip() for line in f.readlines() if line.strip()]
                return poems if poems else ["欢迎来到我的个人主页"]
    except Exception as e:
        print(f"读取诗句失败: {e}")
    return ["欢迎来到我的个人主页"]

# 读取悬浮窗配置
def get_tooltips():
    try:
        with open(os.path.join(BASE_DIR, 'config', 'tooltips.json'), 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "avatar": {
                "title": "关于我",
                "content": "一名热爱编程的高中生，喜欢探索新技术"
            },
            "tech_stack": {
                "Python": {
                    "title": "Python",
                    "content": "熟练使用Python进行后端开发和自动化脚本编写"
                },
                "JavaScript": {
                    "title": "JavaScript",
                    "content": "能够使用JavaScript进行前端交互开发"
                }
            }
        }
    except Exception as e:
        print(f"读取悬浮窗配置失败: {e}")
        return {}

# 获取技能熟练度数据（用于图表）
def get_skills_data_for_chart():
    if not skills_data or 'skills' not in skills_data or not skills_data['skills']:
        return [], [], []
    
    try:
        skills = skills_data['skills']
        labels = [skill['name'] for skill in skills]
        data = [skill['level'] for skill in skills]
        colors = [skill.get('color', config['theme']['primary_color']) for skill in skills]
        
        return labels, data, colors
    except Exception as e:
        print(f"获取技能数据失败: {e}")
        return [], [], []

# 获取技术栈（从配置文件读取）
def get_tech_stack():
    try:
        tech_stack = config.get('tech_stack', [])
        if not tech_stack:
            return []
        return tech_stack
    except Exception as e:
        print(f"获取技术栈失败: {e}")
        return []

# 文章相关函数
def get_articles():
    arts = []
    if not os.path.exists(ARTICLES_DIR):
        return arts
    for f in sorted(os.listdir(ARTICLES_DIR)):
        if not f.endswith('.md'):
            continue
        slug = f[:-3]
        title = slug
        fpath = os.path.join(ARTICLES_DIR, f)
        try:
            with open(fpath, 'r', encoding='utf-8') as fh:
                for line in fh:
                    line = line.strip()
                    if line.startswith('# ') and not line.startswith('## '):
                        title = line[2:].strip()
                        break
        except:
            pass
        arts.append({'title': title, 'slug': slug})
    return arts

def get_article_content(slug):
    fpath = os.path.join(ARTICLES_DIR, f'{slug}.md')
    if not os.path.exists(fpath):
        return None
    with open(fpath, 'r', encoding='utf-8') as f:
        md_text = f.read()
        return markdown.markdown(
            md_text,
            extensions=['extra', 'codehilite', 'toc', 'tables', 'md_in_html'],
            extension_configs={
                'codehilite': {'css_class': 'highlight', 'linenums': False}
            }
        )

def get_background():
    bg_name = config.get('background', {}).get('image', 'background.jpg')
    possible = [
        os.path.join(BASE_DIR, 'content', bg_name),
        os.path.join(BASE_DIR, bg_name),
        os.path.join(os.getcwd(), bg_name),
        os.path.join(os.getcwd(), 'static', bg_name)
    ]
    exists = False
    path = bg_name
    for p in possible:
        if os.path.exists(p):
            exists = True
            if 'static' in p:
                path = f'/static/{bg_name}'
            elif BASE_DIR in p:
                path = f'/content/{bg_name}'
            else:
                path = bg_name
            break
    return exists, path

# GitHub API 请求函数
def make_github_request(url, timeout=5):
    try:
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context
        
        headers = {'Accept': 'application/vnd.github.v3+json'}
        response = requests.get(url, headers=headers, timeout=timeout, verify=False)
        print(f"GitHub API请求: {url}, 状态码: {response.status_code}")
        return response
    except Exception as e:
        print(f"GitHub API请求异常: {e}")
        class MockResponse:
            def __init__(self):
                self.status_code = 500
                self.text = "模拟错误响应"
        return MockResponse()

# 从GitHub获取项目列表

def get_github_projects():

    print("开始从GitHub获取项目列表")

    

    github_url = config.get('github_url', 'https://github.com/example')

    username = github_url.rstrip('/').split('/')[-1]

    print(f"从GitHub获取用户 {username} 的项目")

    

    try:

        repos_response = make_github_request(f'https://api.github.com/users/{username}/repos?sort=pushed&per_page=100')

        

        if repos_response.status_code == 200:

            repos = repos_response.json()

            print(f"成功获取到 {len(repos)} 个项目")

            

            if len(repos) == 0:

                print(f"警告：用户 {username} 没有公开的仓库")

            

            # 转换为项目列表格式

            projects = []

            for repo in repos:

                projects.append({

                    "name": repo.get('name'),

                    "description": repo.get('description', '暂无描述'),

                    "url": repo.get('html_url'),

                    "language": repo.get('language', 'Unknown'),

                    "tags": [repo.get('language')] if repo.get('language') else [],

                    "stars": repo.get('stargazers_count', 0),

                    "updated": repo.get('pushed_at', '')[:10] if repo.get('pushed_at') else ''

                })

            

            projects.sort(key=lambda x: x['stars'], reverse=True)
            return projects[:10]

        else:

            print(f"GitHub API返回错误: {repos_response.status_code}")

            if repos_response.status_code == 403:

                print("提示：可能受到 GitHub API 限制，请稍后再试")

            return []

    except Exception as e:

        print(f"获取GitHub项目失败: {e}")

        return []

# 获取项目列表（优先从GitHub，失败则从本地）
def get_projects():
    # 先尝试从GitHub获取
    github_projects = get_github_projects()
    if github_projects:
        return github_projects
    
    # GitHub获取失败，从本地读取
    print("GitHub获取失败，使用本地项目数据")
    if projects_data and 'projects' in projects_data:
        return projects_data['projects']
    return []

# 获取GitHub贡献数据（只使用真实API数据）
_contrib_cache = None

def get_github_contributions(months=12):
    """从 Events API + per-repo Commits API 获取真实贡献数据，绝不生成假数据"""
    global _contrib_cache
    if _contrib_cache is not None:
        print("命中贡献数据缓存")
        return _contrib_cache
    
    from datetime import datetime
    from collections import defaultdict
    
    github_url = config.get('github_url', 'https://github.com/example')
    username = github_url.rstrip('/').split('/')[-1]
    
    print(f"获取 {username} 的真实贡献数据")
    
    # 预填12个月（1月-12月），全部为0
    result = [{'date': f"{m}月", 'count': 0} for m in range(1, 13)]
    by_month = defaultdict(int)
    processed = set()  # 去重
    
    try:
        # ===== 1. 获取用户所有仓库（备份中的 repos API 遍历策略） =====
        repos_r = make_github_request(f'https://api.github.com/users/{username}/repos?per_page=100')
        if repos_r.status_code == 200:
            repos = repos_r.json()
            print(f"获取到 {len(repos)} 个仓库，开始查询各仓库的提交记录")
            for repo in repos:
                rn = repo['name']
                # 查询该仓库中该用户的 commits（备份中没有 author 参数，但我们加上更精确）
                c_r = make_github_request(
                    f'https://api.github.com/repos/{username}/{rn}/commits?author={username}&per_page=100'
                )
                if c_r.status_code == 200:
                    commits = c_r.json()
                    for c in commits:
                        sha = c.get('sha', '')
                        if sha and sha not in processed:
                            processed.add(sha)
                            try:
                                dt = c['commit']['committer']['date'][:7]
                                by_month[dt] += 1
                            except:
                                pass
                    if commits:
                        print(f"  {rn}: {len(commits)} 个提交")
                elif c_r.status_code == 409:
                    pass  # 空仓库，跳过
        else:
            print(f"获取仓库列表失败 ({repos_r.status_code})")
        
        # ===== 2. 获取 Events API（备份中的策略，捕获跨仓库提交） =====
        ev_r = make_github_request(f'https://api.github.com/users/{username}/events/public?per_page=300')
        if ev_r.status_code == 200:
            evts = ev_r.json()
            print(f"Events API 获取到 {len(evts)} 个事件")
            for e in evts:
                if e['type'] != 'PushEvent':
                    continue
                commits = e.get('payload', {}).get('commits', [])
                if commits:
                    mk = e['created_at'][:7]
                    # Events API 的 commit 对象是简化的，没有完整 sha，直接加数量
                    by_month[mk] += len(commits)
        
        # ===== 3. 填充到结果 =====
        for mk, cnt in by_month.items():
            try:
                mn = int(mk[5:7])
                result[mn - 1]['count'] += cnt
            except:
                pass
        
        total = sum(r['count'] for r in result)
        print(f"真实贡献: {[(r['date'], r['count']) for r in result]} (总计:{total})")
        
        _contrib_cache = result
        return result
        
    except Exception as e:
        print(f"获取贡献数据失败: {e}，返回空数据")
        _contrib_cache = result
        return result

@app.route('/')
def index():
    # 读取像素文字配置（确保总是有数据）
    try:
        with open(os.path.join(BASE_DIR, 'config', 'pixel-text.json'), 'r', encoding='utf-8') as f:
            pixel_text_config = json.load(f)
    except FileNotFoundError:
        pixel_text_config = {"我": {"width": 12, "height": 12, "pixels": []}, "爱": {"width": 12, "height": 12, "pixels": []}, "雨": {"width": 12, "height": 12, "pixels": []}, "云": {"width": 12, "height": 12, "pixels": []}}
    
    # 获取技能图表数据
    skill_labels, skill_data, skill_colors = get_skills_data_for_chart()
    
    # 获取项目列表（优先从GitHub，失败则从本地）
    projects = get_projects()
    
    # 获取技术栈（从配置文件读取）
    tech_stack = get_tech_stack()
    
    # 获取诗句列表
    poems = get_poems()
    
    # 获取悬浮窗配置
    tooltips = get_tooltips()
    
    # 获取贡献数据（最近12个月）
    contributions = get_github_contributions(months=12)
    
    # 检查背景图片
    background_image = config.get('background', {}).get('image', 'background.jpg')
    print(f"开始检查背景图片: {background_image}")
    
    possible_paths = [
        os.path.join(BASE_DIR, 'content', background_image),
        os.path.join(BASE_DIR, background_image),
        os.path.join(os.getcwd(), background_image),
        os.path.join(os.getcwd(), 'static', background_image)
    ]
    
    print(f"可能的背景图片路径: {possible_paths}")
    
    background_exists = False
    background_path = background_image
    
    for path in possible_paths:
        print(f"检查路径: {path}, 存在: {os.path.exists(path)}")
        if os.path.exists(path):
            background_exists = True
            if 'static' in path:
                background_path = f'/static/{background_image}'
                print(f"使用static路径: {background_path}")
            elif BASE_DIR in path:
                # 使用相对路径，便于部署到 GitHub Pages
                background_path = f'/content/{background_image}'
                print(f"使用content相对路径: {background_path}")
            else:
                background_path = background_image
                print(f"使用原始路径: {background_path}")
            break
    
    print(f"最终背景图片状态: exists={background_exists}, path={background_path}")
    
    # 构建返回数据
    github_info = {
        "avatar_url": config.get('avatar_url', 'https://avatars.githubusercontent.com/u/1000000?v=4'),
        "name": config.get('name', 'Example User'),
        "bio": config.get('bio', 'Python Developer'),
        "readme_content": get_introduction_content(),
        "recent_repos": projects,
        "skill_data": skill_data,
        "skill_labels": skill_labels,
        "skill_colors": skill_colors,
        "tech_stack": tech_stack,
        "poems": poems,
        "tooltips": tooltips,
        "pixel_text": pixel_text_config,
        "contributions": contributions
    }
    
    return render_template('index.html', 
                          github_info=github_info, 
                          config=config,
                          now=datetime.now(),
                          background_exists=background_exists,
                          background_path=background_path)

@app.route('/articles')
def articles_list():
    arts = get_articles()
    bg_exists, bg_path = get_background()
    resp = render_template('articles.html', articles=arts, config=config,
                          background_exists=bg_exists, background_path=bg_path)
    resp = app.make_response(resp)
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, proxy-revalidate'
    resp.headers['Pragma'] = 'no-cache'
    resp.headers['Expires'] = '0'
    return resp

@app.route('/article/<slug>')
def article_view(slug):
    content = get_article_content(slug)
    if content is None:
        abort(404)
    arts = get_articles()
    title = slug
    for a in arts:
        if a['slug'] == slug:
            title = a['title']
            break
    bg_exists, bg_path = get_background()
    return render_template('article.html', title=title, content=content, config=config, slug=slug,
                          background_exists=bg_exists, background_path=bg_path)

@app.route('/api/config')
def get_config():
    return jsonify(config)

@app.route('/content/<path:filename>')
def serve_content_file(filename):
    """服务 content 目录中的静态文件"""
    try:
        return send_from_directory(os.path.join(BASE_DIR, 'content'), filename)
    except FileNotFoundError:
        abort(404)

@app.route('/fonts/<path:filename>')
def serve_fonts(filename):
    """服务 fonts 目录中的字体文件"""
    try:
        return send_from_directory(os.path.join(BASE_DIR, 'fonts'), filename)
    except FileNotFoundError:
        abort(404)

@app.route('/<path:filename>')
def serve_root_file(filename):
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.css', '.js', '.ttf', '.woff', '.woff2'}
    file_ext = os.path.splitext(filename)[1].lower()
    
    if file_ext in allowed_extensions:
        try:
            # 先尝试从 content 目录提供
            try:
                return send_from_directory(os.path.join(BASE_DIR, 'content'), filename)
            except FileNotFoundError:
                # 如果 content 目录没有，再尝试从项目根目录提供
                return send_from_directory(BASE_DIR, filename)
        except FileNotFoundError:
            abort(404)
    abort(404)

if __name__ == '__main__':
    import time as _time
    _cp = os.getpid()
    _pidf = os.path.join(BASE_DIR, '.flask.pid')
    if os.path.exists(_pidf):
        try:
            with open(_pidf) as _f:
                _op = _f.read().strip()
            if _op and _op.isdigit():
                _op = int(_op)
                if _op != _cp:  # 避免杀自己（系统可能复用了PID）
                    os.kill(_op, 9)
                    _time.sleep(0.5)
        except:
            pass
    try:
        with open(_pidf, 'w') as _f:
            _f.write(str(_cp))
    except:
        pass
    app.run(debug=False, host='0.0.0.0', port=5000)