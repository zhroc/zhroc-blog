---
title: "微软免费穿透工具使用"
date: 2025-07-02
lastmod: 2025-07-02
author: "zhroc"
tags:
  - tunnel
  
description: "Microsoft Dev Tunnel可以将本地HTTP(S)服务映射到公网上，方便预览调试等等。"

draft: false               # 是否为草稿
mermaid: false             # 是否开启mermaid
showToc: true              # 显示目录
TocOpen: true              # 自动展开目录
hidemeta: false            # 是否隐藏文章的元信息，如发布日期、作者等
ShowLastMod: false         # 显示文章更新时间
showbreadcrumbs: false     # 顶部显示路径(面包屑)

---


### 前言

微软开发隧道（Microsoft Dev Tunnel）允许开发人员跨 Internet 安全地共享本地 Web 服务。 使你能够将本地开发环境与云服务连接，与同事共享正在进行的工作或帮助构建 Webhook。 开发隧道适用于临时测试和开发，不适用于生产工作负荷。

### 下载

Windows x64： https://aka.ms/TunnelsCliDownload/win-x64

macOS (arm64)： https://aka.ms/TunnelsCliDownload/osx-arm64-zip

macOS (x64)： https://aka.ms/TunnelsCliDownload/osx-x64-zip

Linux x64： https://aka.ms/TunnelsCliDownload/linux-x64

### 使用

#### 登录账号

打开Windows Terminal，进入软件所在目录，执行命令：`./devtunnel.exe user login -g -d`  （如果电脑有浏览器优先调起浏览器实现登陆授权）出现如下提示

```powershell
PS C:\Users\Administrator> ./devtunnel.exe user login -g -d
Browse to https://github.com/login/device and enter the code: 932E-F865
Logged in as malaohu using GitHub.
```

浏览器打开： https://github.com/login/device 填写上面显示的CODE：xxxx-xxxx 

同意授权即可完成登录。

{{< img src="microsoft_dev_tunnel_docs-01.png">}}


#### 开启转发

输入转发端口命令：`./devtunnel.exe host -p 1313` 提示如下

```powershell
PS C:\Users\Administrator> .\devtunnel.exe host -p 1313
Hosting port: 1313
Connect via browser: https://0k5vjwtb.asse.devtunnels.ms:1313, https://0k5vjwtb-1313.asse.devtunnels.ms
Inspect network activity: https://0k5vjwtb-1313-inspect.asse.devtunnels.ms

Ready to accept connections for tunnel: puzzled-lake-mfcnjm9.asse
```

使用浏览器访问以下任意一个网址即可

`https://0k5vjwtb.asse.devtunnels.ms:1313` 和 `https://0k5vjwtb-1313.asse.devtunnels.ms` 

进入后需要使用上一步授权的GitHub账号登陆即可。

>  启动命令可选参数：` --allow-anonymous`

```powershell
PS C:\Users\Administrator> .\devtunnel.exe host -p 1313 --allow-anonymous
Hosting port: 1313
Connect via browser: https://0k5vjwtb.asse.devtunnels.ms:1313, https://0k5vjwtb-1313.asse.devtunnels.ms
Inspect network activity: https://0k5vjwtb-1313-inspect.asse.devtunnels.ms

Ready to accept connections for tunnel: puzzled-lake-mfcnjm9.asse
```

这种方法可以使任何获得链接的人无需授权直接访问，比较方便。

### 案例

>  使用Microsoft Dev Tunnel转发hugo server 进行预览

1. 先将Tunnel和hugo都添加好环境变量
2. 将下面代码中的 `hugoProjectDir` 修改为自己的hugo项目目录，保存文件后缀为 `ps1`
3. 使用Windows Powershell运行文件即可

```powershell
# 设置控制台编码为UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 | Out-Null

<#
.SYNOPSIS
    自动化Dev Tunnel设置和Hugo服务器启动（无需切换目录版）
.DESCRIPTION
    此脚本：
    1. 在端口1313上启动Microsoft Dev Tunnel
    2. 提取隧道URL
    3. 使用--source参数直接指定Hugo项目目录启动服务器
    4. 错误时自动清理Dev Tunnel进程
.NOTES
    文件名      : RunHugoWithDevTunnelNoCD.ps1
    前提条件   : PowerShell 5.1或更高版本, Hugo, Microsoft Dev Tunnel CLI
#>

# 用户可自定义的变量
$hugoProjectDir = ""  # 修改为您的Hugo项目目录
$devTunnelProcess = $null

try {
    # 第一步：启动Dev Tunnel
    Write-Host "`n=== 第一步：启动 Microsoft Dev Tunnel ===" -ForegroundColor Green
    $devTunnelCommand = ".\devtunnel.exe host -p 1313 --allow-anonymous"
    Write-Host "执行命令: $devTunnelCommand`n" -ForegroundColor Cyan

    # 启动Dev Tunnel并捕获进程对象
    $devTunnelProcess = Start-Process -FilePath "devtunnel.exe" -ArgumentList "host -p 1313 --allow-anonymous" -NoNewWindow -PassThru -RedirectStandardOutput "devtunnel_output.txt"

    # 等待几秒让Dev Tunnel初始化
    Start-Sleep -Seconds 5

    # 读取Dev Tunnel输出
    $devTunnelOutput = Get-Content "devtunnel_output.txt" -Raw
    Write-Host $devTunnelOutput

    # 从输出中提取URL
    $tunnelUrl = $devTunnelOutput | Select-String -Pattern "Connect via browser: (https://[^\s,]+)" | ForEach-Object { $_.Matches.Groups[1].Value }

    if (-not $tunnelUrl) {
        Write-Host "无法从Dev Tunnel输出中提取URL" -ForegroundColor Red
        throw "Dev Tunnel URL提取失败"
    }

    Write-Host "`n提取的隧道URL: $tunnelUrl`n" -ForegroundColor Yellow

    # 第二步：启动Hugo服务器（不切换目录）
    Write-Host "`n=== 第二步：启动 Hugo 服务器 ===" -ForegroundColor Green

    # 检查Hugo项目目录是否存在
    if (-not (Test-Path $hugoProjectDir)) {
        Write-Host "错误：Hugo项目目录不存在: $hugoProjectDir" -ForegroundColor Red
        throw "目录不存在"
    }

    # 构建Hugo命令（使用--source参数）
    $hugoCommand = "hugo server --source `"$hugoProjectDir`" --baseURL=`"$tunnelUrl`" --bind=0.0.0.0 --port=1313"
    Write-Host "执行命令: $hugoCommand`n" -ForegroundColor Cyan

    # 启动Hugo服务器
    try {
        # 直接调用hugo命令，输出会显示在控制台
        Invoke-Expression $hugoCommand
    }
    catch {
        Write-Host "启动Hugo服务器时出错: $_" -ForegroundColor Red
        throw $_
    }
}
catch {
    Write-Host "`n发生错误: $_" -ForegroundColor Red
    Write-Host "正在清理Dev Tunnel进程..." -ForegroundColor Yellow
    
    # 停止Dev Tunnel进程
    if ($devTunnelProcess -and -not $devTunnelProcess.HasExited) {
        Stop-Process -Id $devTunnelProcess.Id -Force -ErrorAction SilentlyContinue
        Write-Host "已停止Dev Tunnel进程" -ForegroundColor Yellow
    }
    
    # 退出脚本并返回错误代码
    exit 1
}
finally {
    # 清理临时文件
    if (Test-Path "devtunnel_output.txt") {
        Remove-Item "devtunnel_output.txt" -ErrorAction SilentlyContinue
    }
}
```

### 参考

> 更多高级使用方法请看[这里](https://51.ruyo.net/18563.html)。