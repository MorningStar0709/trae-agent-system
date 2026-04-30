# GitHub Pages 设置指南

## 如何启用 GitHub Pages

本项目包含精美的 GitHub Pages 入口页面，让你的项目更加专业和易于访问。

### 启用步骤

1. **访问仓库设置**
   - 打开 https://github.com/MorningStar0709/trae-agent-os/settings/pages

2. **配置 GitHub Pages**
   - **Source**: 选择 `Deploy from a branch`
   - **Branch**: 选择 `main` 分支
   - **Folder**: 选择 `/ (root)`
   - **Theme**: 选择 Jekyll（可选）

3. **保存设置**
   - 点击 "Save" 按钮

4. **等待部署**
   - 部署通常需要 1-2 分钟
   - 访问 https://MorningStar0709.github.io/trae-agent-os 查看效果

## 页面结构

项目入口页面位于根目录：

- **入口页面**: `index.html` - GitHub Pages 首页

文档位于 `docs/` 目录，包含完整的中英双语文档：
- [docs/01-intro_zh.md](docs/01-intro_zh.md) - 中文极简介绍
- [docs/02-overview_zh.md](docs/02-overview_zh.md) - 中文亮点介绍
- [docs/03-components_zh.md](docs/03-components_zh.md) - 中文组件速查
- [docs/04-design_zh.md](docs/04-design_zh.md) - 中文设计思路
- [docs/05-architecture_zh.md](docs/05-architecture_zh.md) - 中文完整架构

## 页面特性

### 🎨 设计特点

- 现代渐变背景设计
- 完全响应式布局
- 移动端友好
- 快速开始指南
- 技能卡片展示
- 统一的品牌风格

### 📱 响应式设计

页面会自动适配不同设备：
- 桌面电脑
- 笔记本电脑
- 平板设备
- 手机

### 🚀 性能优化

- 纯 HTML/CSS，无外部依赖
- 轻量级设计，加载速度快
- 优化字体加载
- 最小化重绘和回流

## 自定义域名（可选）

如果你想使用自定义域名：

1. 在 `Custom domain` 输入你的域名
2. 在你的域名提供商处添加 CNAME 记录
3. 等待 DNS 传播（通常几分钟到48小时）

## 故障排除

### 页面未显示

- 确保 GitHub Pages 已启用
- 检查分支名称是否正确
- 等待部署完成（通常 1-2 分钟）

### 样式问题

- 清除浏览器缓存
- 尝试使用无痕模式访问
- 检查是否有 CSS 加载错误

### 404 错误

- 确保 `index.html` 在仓库根目录
- 检查文件名大小写是否正确

## 更多资源

- [GitHub Pages 文档](https://docs.github.com/en/pages)
- [Jekyll 主题](https://pages.github.com/themes/)
- [自定义域名设置](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)

---

💡 **提示**: GitHub Pages 会自动处理 Jekyll 构建，如果你想在页面中使用 Markdown，只需将 `.md` 文件放在仓库中即可。
