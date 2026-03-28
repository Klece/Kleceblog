import os
import json
import markdown
import requests
from flask import Flask, render_template, jsonify, send_from_directory, abort
from datetime import datetime
import shutil

# 获取项目根目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(__name__, template_folder=os.path.join(BASE_DIR, 'templates'))

# 全局变量
config = None
skills_data = None
projects_data = None

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

# 在第一次请求前加载配置
@app.before_first_request
def load_config():
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
            
            return projects[:10]  # 只返回最近10个项目
        else:
            print(f"GitHub API返回错误: {repos_response.status_code}")
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

@app.route('/')
def index():
    load_all_configs()
    
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
    
    # 检查背景图片
    background_image = config.get('background', {}).get('image', 'background.jpg')
    possible_paths = [
        os.path.join(BASE_DIR, 'content', background_image),
        os.path.join(BASE_DIR, background_image),
        os.path.join(os.getcwd(), background_image),
        os.path.join(os.getcwd(), 'static', background_image)
    ]
    
    background_exists = False
    background_path = background_image
    
    for path in possible_paths:
        if os.path.exists(path):
            background_exists = True
            if 'static' in path:
                background_path = f'/static/{background_image}'
            elif BASE_DIR in path:
                # 使用相对路径，便于部署到 GitHub Pages
                background_path = f'content/{background_image}'
            else:
                background_path = background_image
            break
    
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
        "tooltips": tooltips
    }
    
    return render_template('index.html', 
                          github_info=github_info, 
                          config=config,
                          now=datetime.now(),
                          background_exists=background_exists,
                          background_path=background_path)

@app.route('/api/config')
def get_config():
    return jsonify(config)

@app.route('/<path:filename>')
def serve_root_file(filename):
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.svg', '.css', '.js'}
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
    app.run(debug=True, host='0.0.0.0', port=5000)