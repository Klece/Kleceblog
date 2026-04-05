## 项目说明

本项目基于 [SRInternet/Home_Page](https://github.com/SRInternet/Home_Page) 进行二次开发，感谢原作者的贡献。

## 功能特性

- ✨ **美观的 UI 设计**：玻璃态效果、动画过渡、响应式布局
- 🌓 **深色模式支持**：自动跟随系统主题，也可手动切换
- 📱 **移动端友好**：完美适配各种屏幕尺寸
- 🎨 **自定义配置**：轻松修改主题颜色、背景图片、社交链接等
- 🚀 **GitHub 集成**：自动从 GitHub 获取项目信息和贡献数据
- 📈 **贡献统计**：展示最近 7 天的 GitHub 提交记录
- 📜 **诗句轮播**：展示经典诗句，每 6 秒自动切换
- 💬 **悬浮窗提示**：鼠标悬停显示详细信息
- 📅 **日期显示**：实时显示当前日期和星期
- 🔧 **静态部署**：支持生成静态 HTML，可部署到 GitHub Pages
- 🎭 **极简模式**：一键切换极简背景模式

## 运行方式

### 本地运行

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

## 配置说明

### 1. 主配置文件 (`config/config.json`)

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

每行一句诗，会自动轮播显示(6s)

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

## 修改后的操作

修改配置文件后，执行以下操作查看效果：

1. **本地运行**：
```bash
cd src
python app.py
```
然后刷新浏览器页面。

## 部署到 GitHub Pages

1. **生成静态文件**
```bash
cd src
python build_static.py
```

2. **推送代码到 GitHub**
```bash
git add .
git commit -m "更新配置"
git push origin main
```

3. **启用 GitHub Pages**
   - 访问仓库设置页面
   - 点击 "Pages"
   - 选择 `main` 分支，保存

4. **自动部署**
   - 当你推送到 main 或 master 分支时，GitHub Actions 会自动运行
   - GitHub Actions 也会在每天 UTC 时间 0 点（北京时间 8 点）自动运行
   - 你也可以通过 GitHub 仓库的 Actions 页面手动触发运行
   - 构建产物会直接部署到 GitHub Pages

5. **访问你的网站**
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
│   ├── projects.json      # 项目数据
│   └── poems.txt          # 诗句轮播
├── content/                # 内容文件目录
│   ├── Introduction.md    # 个人介绍
│   ├── background.jpg     # 背景图片
│   └── image.png          # 图片资源
├── fonts/                  # 字体文件目录
│   └── loli-font.ttf      # 自定义字体
├── templates/              # 模板文件目录
│   └── index.html         # 主页面模板
├── default/                # 默认配置和资源
│   ├── default_config.json
│   └── background.jpg
├── .dockerignore           # Docker 忽略文件
├── .gitignore              # Git 忽略文件
├── Dockerfile              # Docker 配置
├── LICENSE                 # MIT 许可证
├── README.md               # 项目文档
├── requirements.txt        # Python 依赖
└── index.html              # 生成的静态文件（用于部署）
```