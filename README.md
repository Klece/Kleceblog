# Kleceblog

Klece 的个人主页，基于 Flask + Tailwind CSS 构建，支持深色模式和响应式设计。

## 项目说明

本项目基于 [SRInternet/Home_Page](https://github.com/SRInternet/Home_Page) 进行二次开发，感谢原作者的贡献。

## 功能特性

- ✨ **美观的 UI 设计**：玻璃态效果、动画过渡、响应式布局
- 🌓 **深色模式支持**：自动跟随系统主题，也可手动切换
- 📱 **移动端友好**：完美适配各种屏幕尺寸
- 🎨 **自定义配置**：轻松修改主题颜色、背景图片、社交链接等
- 🚀 **GitHub 集成**：自动从 GitHub 获取项目信息
- 📜 **诗句轮播**：展示经典诗句，每 6 秒自动切换
- 💬 **悬浮窗提示**：鼠标悬停显示详细信息
- 📅 **日期显示**：实时显示当前日期和星期
- 🔧 **静态部署**：支持生成静态 HTML，可部署到 GitHub Pages

## 运行方式

### 方式一：本地运行（推荐用于开发）

1. **克隆仓库**
```bash
git clone https://github.com/Klece/Kleceblog.git
cd Kleceblog
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **运行应用**
```bash
cd src
python app.py
```

4. **访问网站**
打开浏览器访问：`http://localhost:5000`

### 方式二：生成静态文件（用于部署）

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **生成静态 HTML**
```bash
cd src
python build_static.py
```

3. **部署**
将生成的 `index.html` 文件部署到你的 Web 服务器或 GitHub Pages。

## 配置说明

### 1. 主配置文件 (`config/config.json`)

```json
{
  "github_url": "https://github.com/Klece",
  "dark_mode": "auto",
  "name": "Klece",
  "bio": "一个普通人",
  "avatar_url": "https://avatars.githubusercontent.com/u/241420622?v=4",
  "introduction_file": "Introduction.md",
  "theme": {
    "primary_color": "#6a11cb",
    "secondary_color": "#2575fc",
    "dark_primary_color": "#a855f7",
    "dark_secondary_color": "#60a5fa"
  },
  "background": {
    "image": "background.jpg",
    "blur": 4,
    "overlay_opacity": 0.6,
    "overlay_color": "#f3f4f6",
    "dark_overlay_color": "#121212"
  },
  "contact": {
    "qq": "2962065406",
    "wechat": "",
    "bilibili": "",
    "douyin": "",
    "xiaohongshu": ""
  },
  "tech_stack": [
    {
      "name": "Python",
      "color": "#6a11cb",
      "description": "熟练使用Python进行后端开发和脚本编写"
    }
  ]
}
```

**配置项说明：**
- `github_url`: 你的 GitHub 主页链接
- `dark_mode`: 深色模式（`auto` 自动、`light` 浅色、`dark` 深色）
- `name`: 你的名字
- `bio`: 个人简介
- `avatar_url`: 头像图片链接
- `introduction_file`: 个人介绍文件路径（相对于 content/ 目录）
- `theme`: 主题颜色配置
- `background`: 背景图片配置
- `contact`: 社交联系方式
- `tech_stack`: 技术栈展示

### 2. 个人介绍文件 (`content/Introduction.md`)

编辑此文件来修改"个人介绍"部分的内容，支持 Markdown 语法。

```markdown
# 个人主页

欢迎你来到我的个人主页

## 关于我
一名普通的高中生
```

### 3. 诗句轮播文件 (`config/poems.txt`)

每行一句诗，会自动轮播显示。

```text
人生若只如初见，何事秋风悲画扇
山有木兮木有枝，心悦君兮君不知
两情若是久长时，又岂在朝朝暮暮
```

### 4. 悬浮窗配置文件 (`config/tooltips.json`)

配置鼠标悬停时显示的详细信息。

```json
{
  "avatar": {
    "title": "我",
    "content": "你好呀喵~<br>我是Klece"
  },
  "tech_stack": {
    "Python": {
      "title": "Python",
      "content": "一种语言"
    }
  }
}
```

**注意：** 使用 `<br>` 标签可以实现换行。

### 5. 项目数据文件 (`config/projects.json`)

当 GitHub API 不可用时，会使用此文件中的数据。

```json
{
  "projects": []
}
```

### 6. 技能数据文件 (`config/skills.json`)

当前未使用，保留用于未来扩展。

## 修改后的操作

修改配置文件后，执行以下操作查看效果：

1. **如果是本地运行**：
```bash
cd src
python app.py
```
然后刷新浏览器页面。

2. **如果要生成静态文件**：
```bash
cd src
python build_static.py
```

## 部署到 GitHub Pages

### 方式一：使用 GitHub Actions 自动部署（推荐）

1. **推送代码到 GitHub**
```bash
git add .
git commit -m "更新配置"
git push origin main
```

2. **启用 GitHub Pages**
   - 访问仓库设置页面
   - 点击 "Pages"
   - 选择 `main` 分支，保存

3. **自动部署**
   - 当你推送到 main 或 master 分支时，GitHub Actions 会自动运行
   - GitHub Actions 也会在每天 UTC 时间 0 点（北京时间 8 点）自动运行
   - 你也可以通过 GitHub 仓库的 Actions 页面手动触发运行
   - 构建产物会直接部署到 GitHub Pages

4. **访问你的网站**
   - 等待几分钟后，访问 `https://你的用户名.github.io/仓库名/`

### 方式二：手动部署静态文件

1. **生成静态文件**
```bash
cd src
python build_static.py
```

2. **上传文件到 GitHub**
   需要上传以下文件到你的 GitHub 仓库：
   - `index.html`（生成的静态文件）
   - `content/` 目录（包含 Introduction.md 和 background.jpg）
   - `config/` 目录（包含所有配置文件）
   - `templates/` 目录（包含 index.html 模板）
   - `src/` 目录（包含 app.py 和 build_static.py）
   - `default/` 目录（包含默认配置）
   - `requirements.txt`
   - `README.md`
   - 其他必要文件（LICENSE、.gitignore 等）

3. **启用 GitHub Pages**
   - 访问仓库设置页面
   - 点击 "Pages"
   - 选择 `main` 分支，保存

4. **访问你的网站**
   - 等待几分钟后，访问 `https://你的用户名.github.io/仓库名/`

**注意：**
- 使用 GitHub Pages 部署时，背景图片路径使用相对路径 `content/background.jpg`
- 确保所有配置文件都已正确上传
- 生成的 `index.html` 会自动使用 `content/` 目录中的资源文件

## 项目结构

```
Home_Page/
├── src/                    # 源代码目录
│   ├── app.py             # Flask 应用主文件
│   ├── build_static.py    # 生成静态文件的脚本
│   └── deploy.sh          # 部署脚本
├── config/                 # 配置文件目录
│   ├── config.json        # 主配置文件
│   ├── tooltips.json      # 悬浮窗配置
│   ├── skills.json        # 技能数据
│   ├── projects.json      # 项目数据
│   └── poems.txt          # 诗句轮播
├── content/                # 内容文件目录
│   ├── Introduction.md    # 个人介绍
│   └── background.jpg     # 背景图片
├── templates/              # 模板文件目录
│   └── index.html         # 模板文件
├── default/                # 默认配置和资源
│   ├── default_config.json
│   └── background.jpg
├── requirements.txt        # Python 依赖
├── README.md               # 项目文档
└── index.html              # 生成的静态文件（用于部署）
```
