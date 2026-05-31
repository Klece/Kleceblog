## 项目说明

本项目基于 [SRInternet/Home_Page](https://github.com/SRInternet/Home_Page) 进行二次开发，感谢原作者的贡献。

博客展示：[https://klece.github.io/Kleceblog/](https://klece.github.io/Kleceblog/)

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

页面上的所有显示内容都可以通过修改文件来调整，不需要改代码。以下按文件说明各自控制什么。

### 主配置 (`config/config.json`)

这个文件控制页面最核心的信息和样式：

| 配置项 | 作用 |
|--------|------|
| `github_url` | 你的 GitHub 主页链接，用来获取仓库列表和贡献数据 |
| `dark_mode` | 深色模式行为：`auto` 跟随系统、`light` 浅色、`dark` 深色 |
| `name` / `bio` | 页面上显示的名字和个人简介 |
| `avatar_url` | 头像图片链接 |
| `introduction_file` | 个人介绍文件路径（相对于项目根目录） |
| `theme` | 主题色，分 `primary_color` 和 `secondary_color`，浅色和深色模式各一套 |
| `background` | 背景图文件名、模糊度、遮罩透明度/颜色 |
| `contact` | 社交链接，支持 qq/wechat/bilibili/douyin/xiaohongshu |
| `tech_stack` | 技术栈列表，每个需要填写 name/color/description |

如果 `config.json` 文件缺失或损坏，会自动从 `default/default_config.json` 恢复。备份图在 `default/background.jpg`。

### 个人介绍 (`content/Introduction.md`)

右侧栏显示的个人介绍内容，用 Markdown 格式写。修改后刷新页面即可看到变化。

支持标准的 Markdown 语法，包括标题、列表、图片、代码块等。如果文件不存在，页面会显示"这个人很懒，什么都没有留下"。

### 诗句轮播 (`config/poems.txt`)

每行一句诗，页面左侧会自动每隔 6 秒切换显示下一句。如果文件为空或不存在，默认显示"欢迎来到我的个人主页"。

### 悬浮窗提示 (`config/tooltips.json`)

鼠标悬停到头像或技术栈标签时弹出的文字。格式如下：

- `avatar`：头像悬浮窗，配置 title 和 content
- `tech_stack`：技术栈悬浮窗，按技术名称作为 key 配置
- content 中可以用 `<br>` 换行

### 项目数据 (`config/projects.json`)

GitHub API 请求失败时，页面会使用这个文件中的本地数据展示项目列表。数据结构为：

```json
{
  "projects": [
    {
      "name": "项目名",
      "description": "项目描述",
      "url": "项目链接",
      "language": "编程语言",
      "tags": ["标签1", "标签2"],
      "stars": 0,
      "updated": "2026-01-01"
    }
  ]
}
```

### 自定义字体 (`fonts/loli-font.ttf`)

页面的默认字体文件。如果想换字体，替换这个文件就行。

### 背景图片替换

把新的图片放到 `content/` 目录下，然后在 `config.json` 的 `background.image` 里填文件名。

### 文章管理 (`articles/` 目录)

在 `articles/` 目录下新建 `.md` 文件就是发布文章。文章的文件名会成为 URL 中的 slug，第一行 `# 标题` 作为文章标题。

如果不需要文章功能，把 `articles/` 目录清空就行，首页不会显示入口。

## 修改后的操作

改完以上文件后，重新运行应用再刷新页面就能看到效果：

```bash
cd src
python app.py
```

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