+++
title = 'Deploy_blog_study'
date = 2023-12-06T21:29:57+08:00
draft = true
+++


---
#### 准备工作
创建好hugo源文件仓库和github pages仓库（均不要添加readme文件）
#### 首先更新一下索引和软件包
```
apt update
apt upgrade
```
#### 接着下载安装和验证一下hugo
```
wget https://github.com/spf13/hugo/releases/download/v0.14/hugo_0.14_amd64.deb
dpkg -i hugo*.deb
hugo version
```
#### 使用hugo创建站点
```
hugo new site myblog
```
#### 进入目录初始化git和使用模块方式管理主题
```
cd myblog/
git init
git submodule add https://github.com/zhroc/hugo-PaperMod.git themes/hugo-PaperMod
```
#### 复制主题中这些文件到站点目录
![](1.png)
#### 新建一篇文章并预览
```
hugo new posts/blog-test.md
hugo server -D
```
#### 添加github action
在 .github/workflows目录下新建deploy.yml文件
填写好以下内容
```
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
#### 设置好git用户名
```
git config --global user.email "git@github.com"
git config --global user.name "zhroc"
```
#### 关联远程仓库 提交到远程仓库
```
git remote add origin https://github.com/zhroc/zhroc-blog.git
git add .
git status 
git commit -m "new"
git push -u origin main
```