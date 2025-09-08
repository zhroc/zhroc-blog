---
title: "{{ replace .Name "-" " " | title }}"
date: {{ .Date | time.Format "2006-01-02"  }}
lastmod: {{ .Date | time.Format "2006-01-02"  }}
author: "zhroc"
tags:
  - 
  - 
description: ""

showToc: true              # 显示目录
TocOpen: true              # 自动展开目录
hidemeta: false            # 是否隐藏文章的元信息，如发布日期、作者等
ShowLastMod: false         # 显示文章更新时间
showbreadcrumbs: false     # 顶部显示路径(面包屑)
---

![](cover.jpg)