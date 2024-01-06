+++
title = '使用密钥连接ssh 关闭密码连接ssh'
date = 2024-01-06T18:27:34+08:00
draft = false
+++

### 创建密钥对
首先在客户端设备上打开终端，Windows端打开命令行即可，然后创建密钥对，这里使用ed25519的算法生成key，关于ssh key的各种不同算法的选择可以参考[这里](https://www.cnblogs.com/librarookie/p/15389876.html)
```
ssh-keygen -t ed25519
```
随后一路回即可，密钥对一般会保存在当前用户的隐藏目录`.ssh`中，windows用户应该去`C:\Users\用户名\.ssh\`寻找，linux用户应该去`/home/用户名/.ssh/`寻找，该目录应该包含两个密钥文件，`.pub`后缀的文件是公钥，无后缀的为私钥，私钥不需要移动，两个文件如下图所示。
![](1.jpg)


### 添加公钥内容至服务端
我们需要将公钥中的内容追加到服务端的`/home/用户名/.ssh/`目录中的`authorized_key`文件中去。如果没有上述目录与文件，则需要手动创建。可以通过密码连接ssh后用vim直接编辑authorized_key文件，当然也可以使用以下命令进行添加，两者的效果是一致的。
```
cat ~/.ssh/id_ed25519.pub | ssh username@remote_host "mkdir -p ~/.ssh && touch ~/.ssh/authorized_keys && chmod -R go= ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

### 服务端ssh连接配置修改
在服务端打开`/etc/ssh/sshd_config`配置文件，在空白处添加以下内容后保存退出。
```
PubkeyAuthentication yes
PasswordAuthentication no
```
接着重启ssh服务即可
```
sudo systemctl restart ssh
```

### 尝试密钥登录

现在就可以在客户端重新尝试ssh连接了，会发现不需要密码就连接上了。


> 参考文章
* [linux设置ssh密钥登录详细教程](https://blog.csdn.net/weixin_43693967/article/details/130789425)