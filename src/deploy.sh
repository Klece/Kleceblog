#!/bin/bash

# 个人主页部署脚本
# 此脚本提供在 GitHub Pages 上部署个人主页的指南和自动化步骤

# 注意：在 Windows 上，您可以使用 Git Bash 或 WSL 来运行此脚本

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # 无颜色

# 帮助信息
show_help() {
    echo "${YELLOW}用法: ./deploy.sh [选项]${NC}"
    echo ""
    echo "选项:"
    echo "  install     安装项目依赖"
    echo "  run         在本地运行开发服务器"
    echo "  build       构建静态文件（准备部署）"
    echo "  deploy      部署到 GitHub Pages"
    echo "  help        显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  ./deploy.sh install  # 安装依赖"
    echo "  ./deploy.sh run      # 运行本地服务器"
};

# 安装依赖
install_deps() {
    echo -e "${GREEN}正在安装项目依赖...${NC}"
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}依赖安装成功！${NC}"
    else
        echo -e "${RED}依赖安装失败，请检查错误信息。${NC}"
        exit 1
    fi
};

# 运行开发服务器
run_dev() {
    echo -e "${GREEN}正在启动开发服务器...${NC}"
    echo -e "${YELLOW}服务器将在 http://localhost:5000 上运行${NC}"
    python app.py
};

# 构建静态文件
build_static() {
    echo -e "${GREEN}正在构建静态文件...${NC}"
    
    # 直接运行build_static.py脚本，静态HTML将生成在项目根目录
    python build_static.py
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}静态文件构建完成！HTML文件已生成在项目根目录。${NC}"
        echo -e "${YELLOW}注意：您可以直接将index.html等文件推送到GitHub Pages或其他静态站点托管服务。${NC}"
    else
        echo -e "${RED}静态文件构建失败，请检查错误信息。${NC}"
        exit 1
    fi
};

# 部署到 GitHub Pages
deploy_gh_pages() {
    echo -e "${YELLOW}部署到 GitHub Pages 的指南：${NC}"
    echo ""
    echo "1. 确保您已经创建了一个 GitHub 仓库"
    echo "2. 根据您的需求选择以下方法之一进行部署："
    echo ""
    echo "方法一：使用 GitHub Actions 自动化部署（推荐）"
    echo "   - 项目已配置自动编译，每天UTC时间0点（北京时间8点）自动运行"
    echo "   - 配置文件位于 .github/workflows/build-deploy.yml"
    echo "   - 也可以在GitHub仓库的Actions页面手动触发运行"
    echo ""
    echo "方法二：手动部署静态文件"
    echo "   - 运行 './deploy.sh build' 生成静态文件（HTML将直接生成在项目根目录）"
    echo "   - 添加生成的文件: git add index.html background.jpg"
    echo "   - 提交更改: git commit -m 'Update static website'"
    echo "   - 推送到gh-pages分支: git push origin master:gh-pages"
    echo ""
    echo "方法三：使用 Vercel、Netlify 等平台部署"
    echo "   - 注册 Vercel 或 Netlify 账号"
    echo "   - 连接您的 GitHub 仓库"
    echo "   - 按照平台指引完成部署配置"
    echo ""
    echo "更多信息，请参考 Flask 和 GitHub Pages 的官方文档。"
};

# 主函数
main() {
    # 检查参数
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    # 根据参数执行相应的函数
    case "$1" in
        install)
            install_deps
            ;;
        run)
            run_dev
            ;;
        build)
            build_static
            ;;
        deploy)
            deploy_gh_pages
            ;;
        help)
            show_help
            ;;
        *)
            echo -e "${RED}未知选项: $1${NC}"
            show_help
            exit 1
            ;;
    esac
};

# 执行主函数
main "$@"