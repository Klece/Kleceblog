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
        print("像素文字配置文件未找到，使用空数据")

# 在第一次请求前加载配置（已移除，改为在index路由中直接调用）
# @app.before_first_request
# def load_config():
#     load_all_configs()

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

            

            return projects[:10]  # 只返回最近10个项目

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

# 获取GitHub贡献数据（最近days天）
def get_github_contributions(days=7):
    """获取用户最近days天的GitHub贡献数据（commit次数）"""
    from datetime import datetime, timedelta
    
    github_url = config.get('github_url', 'https://github.com/example')
    username = github_url.rstrip('/').split('/')[-1]
    
    print(f"开始获取用户 {username} 最近 {days} 天的贡献数据")
    
    try:
        # 使用 GraphQL API 获取贡献数据
        query = """
        query($login: String!, $from: DateTime!) {
          user(login: $login) {
            contributionsCollection(from: $from) {
              contributionCalendar {
                weeks {
                  contributionDays {
                    date
                    contributionCount
                  }
                }
              }
            }
          }
        }
        """
        
        # 计算 from 日期（最近365天）
        from_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        variables = {
            'login': username,
            'from': from_date
        }
        
        # 调用 GraphQL API
        headers = {'Authorization': f'Bearer {os.environ.get("GITHUB_TOKEN", "")}', 'Content-Type': 'application/json'}
        
        # 如果没有 Token，使用 REST API
        if not headers['Authorization'] or headers['Authorization'] == 'Bearer ':
            print("未配置 GitHub Token，使用备用方案")
            return get_contributions_via_rest_api(username, days)
        
        graphql_response = make_github_request('https://api.github.com/graphql', timeout=10)
        
        if graphql_response.status_code != 200:
            print(f"GraphQL API返回错误: {graphql_response.status_code}")
            return get_contributions_via_rest_api(username, days)
        
        import json
        data = graphql_response.json()
        
        # 解析贡献数据
        contributions_dict = {}
        try:
            weeks = data['data']['user']['contributionsCollection']['contributionCalendar']['weeks']
            for week in weeks:
                for day in week['contributionDays']:
                    if day['contributionCount'] > 0:
                        date_str = day['date']
                        contributions_dict[date_str] = day['contributionCount']
        except KeyError as e:
            print(f"解析GraphQL数据失败: {e}")
            return generate_default_contributions(days)
        
        # 生成最近 days 天的数据
        result = []
        today = datetime.now()
        
        for i in range(days - 1, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            result.append({
                'date': date.strftime('%m/%d'),
                'count': contributions_dict.get(date_str, 0)
            })
        
        print(f"贡献数据: {[(r['date'], r['count']) for r in result]}")
        return result
        
    except Exception as e:
        print(f"获取GitHub贡献数据失败: {e}")
        return get_contributions_via_rest_api(username, days)

# 通过 REST API 获取贡献数据（备用方案）
def get_contributions_via_rest_api(username, days=7):
    """通过 REST API 获取贡献数据"""
    from datetime import datetime, timedelta
    import collections
    
    print(f"使用 REST API 获取用户 {username} 的贡献数据")
    
    try:
        # 调用 GitHub Events API
        events_response = make_github_request(f'https://api.github.com/users/{username}/events/public?per_page=100')
        
        if events_response.status_code != 200:
            print(f"GitHub Events API返回错误: {events_response.status_code}")
            return generate_default_contributions(days)
        
        events = events_response.json()
        print(f"成功获取到 {len(events)} 个事件")
        
        # 统计每个日期的提交次数
        contributions = collections.defaultdict(int)
        # 记录每个仓库每个日期已经处理过的 commit SHA，避免重复计算
        processed_commits = set()
        
        for event in events:
            if event['type'] == 'PushEvent':
                # 获取提交日期（使用 created_at 的日期部分）
                created_at = event['created_at']
                date_str = created_at[:10]  # YYYY-MM-DD
                
                # 统计该日期的 commit 次数
                if 'payload' in event and 'commits' in event['payload']:
                    commits = event['payload']['commits']
                    if len(commits) > 0:
                        contributions[date_str] += len(commits)
                        print(f"  从 Event 获取到 {len(commits)} 个提交（{date_str}）")
                
                # 无论 Event 中是否有 commits，都尝试从仓库获取
                repo_name = event.get('repo', {}).get('name', '')
                if repo_name:
                    # 尝试获取该仓库的 commits（使用正确的日期范围）
                    date_start = f"{date_str}T00:00:00Z"
                    date_end = f"{date_str}T23:59:59Z"
                    commits_response = make_github_request(
                        f'https://api.github.com/repos/{repo_name}/commits?since={date_start}&until={date_end}&per_page=100'
                    )
                    if commits_response.status_code == 200:
                        repo_commits = commits_response.json()
                        if repo_commits:
                            # 使用 set 去重，避免同一个 commit 被多次计算
                            unique_commits = set()
                            for commit in repo_commits:
                                commit_sha = commit['sha']
                                commit_key = f"{repo_name}:{commit_sha}"
                                if commit_key not in processed_commits:
                                    processed_commits.add(commit_key)
                                    unique_commits.add(commit_sha)
                            contributions[date_str] += len(unique_commits)
                            print(f"  ✓ 从 {repo_name} 获取到 {len(unique_commits)} 个唯一提交（{date_str}）")
        
        # 生成最近 days 天的数据
        result = []
        today = datetime.now()
        
        for i in range(days - 1, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            result.append({
                'date': date.strftime('%m/%d'),
                'count': contributions.get(date_str, 0)
            })
        
        print(f"贡献数据: {[(r['date'], r['count']) for r in result]}")
        return result
        
    except Exception as e:
        print(f"通过REST API获取贡献数据失败: {e}")
        return generate_default_contributions(days)

# 生成默认贡献数据（API失败时使用）
def generate_default_contributions(days=7):
    """生成默认的随机贡献数据"""
    from datetime import datetime, timedelta
    import random
    
    result = []
    today = datetime.now()
    
    for i in range(days - 1, -1, -1):
        date = today - timedelta(days=i)
        result.append({
            'date': date.strftime('%m/%d'),
            'count': random.randint(0, 5)  # 随机0-5次提交
        })
    
    return result

@app.route('/')
def index():
    load_all_configs()
    
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
    
    # 获取贡献数据
    contributions = get_github_contributions(days=7)
    
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
                background_path = f'content/{background_image}'
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
    app.run(debug=False, host='0.0.0.0', port=5000)