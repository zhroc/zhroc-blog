---
title: "{{ replace .Name "-" " " | title }}"
date: {{ .Date | time.Format "2006-01-02"  }}
lastmod: {{ .Date | time.Format "2006-01-02"  }}
author: "zhroc"
tags:
  - weekly review
  
description: ""

draft: false               # 是否草稿
showToc: false             # 是否显示目录
hidemeta: false            # 是否隐藏文章的元信息
showbreadcrumbs: false     # 是否显示顶部路径(面包屑)
---

![](cover.jpg)