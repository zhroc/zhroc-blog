---
title: "博客部署简要记录"
date: 2023-12-06
lastmod: 2023-12-06
author: "zhroc"
tags:
  - hugo

description: "这篇文章用来记录使用hugo构建博客的过程。"

showToc: true              # 显示目录
TocOpen: true              # 自动展开目录
hidemeta: false            # 是否隐藏文章的元信息，如发布日期、作者等
ShowLastMod: false         # 显示文章更新时间
showbreadcrumbs: false     # 顶部显示路径(面包屑)
---


#### 准备工作
创建好hugo源文件仓库和github pages仓库（均不要添加readme文件）,更新一下索引和软件包
```powershell
apt update
apt upgrade
```


#### 下载安装hugo
```powershell
wget https://github.com/spf13/hugo/releases/download/v0.14/hugo_0.14_amd64.deb
dpkg -i hugo*.deb
hugo version
```


#### 创建站点配置主题
```powershell
hugo new site myblog
```
进入目录初始化git和使用模块方式管理主题
```powershell
cd myblog/
git init
git submodule add https://github.com/zhroc/PaperMod.git themes/PaperMod
```
复制主题中这些文件到站点目录

{{< img src="deploy_blog_study-01.png">}}

新建一篇文章并预览
```powershell
hugo new posts/blog-test.md
hugo server -D
```


#### 添加github action
在 .github/workflows目录下新建deploy.yml文件
填写好以下内容
```powershell
name: deploy

on:
    push:
    workflow_dispatch:
    schedule:
        # Runs everyday at 8:00 AM
        - cron: "0 0 * * *"

jobs:
    build:
        runs-on: ubuntu-latest
        steps:
            - name: Checkout
              uses: actions/checkout@v2
              with:
                  submodules: true
                  fetch-depth: 0

            - name: Setup Hugo
              uses: peaceiris/actions-hugo@v2
              with:
                  hugo-version: "latest"

            - name: Build Web
              run: hugo

            - name: Deploy Web
              uses: peaceiris/actions-gh-pages@v3
              with:
                  PERSONAL_TOKEN: ${{ secrets.PERSONAL_TOKEN }}
                  EXTERNAL_REPOSITORY: zhroc/zhroc.github.io
                  PUBLISH_BRANCH: master
                  PUBLISH_DIR: ./public
                  commit_message: ${{ github.event.head_commit.message }}
```


#### 创建github的token
进入https://github.com/settings/tokens
创建经典令牌
权限需要开启 repo 与 workflow
进入github的Settings - Secrets - Actions - Repository secrets  - New repository secret 添加 PERSONAL_TOKEN 环境变量为刚才的 Token


#### 关联提交远程仓库
设置好git用户名
```powershell
git config --global user.email "git@github.com"
git config --global user.name "zhroc"
```
提交
```powershell
git remote add origin https://github.com/zhroc/zhroc-blog.git
git add .
git status 
git commit -m "new"
git push -u origin main
```



> 参考文章
* [hugo博客搭建 | PaperMod主题](https://www.sulvblog.cn/posts/blog/build_hugo/)
* [Hugo + GitHub Action，搭建你的博客自动发布系统](https://www.pseudoyu.com/zh/2022/05/29/deploy_your_blog_using_hugo_and_github_action/)
* [从零开始的 Hugo 博客搭建](https://stilig.me/posts/building-hugo)

