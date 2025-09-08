---
title: "flask实现网站接入钉钉sso登录"
date: 2024-01-19
lastmod: 2024-01-19
author: "zhroc"
tags:
  - SSO
  
description: "看到很多项目都接入了钉钉登录，这次自己来尝试一下具体如何操作。"

draft: false               # 是否为草稿
mermaid: false             # 是否开启mermaid
showToc: true              # 显示目录
TocOpen: true              # 自动展开目录
hidemeta: false            # 是否隐藏文章的元信息，如发布日期、作者等
ShowLastMod: false         # 显示文章更新时间
showbreadcrumbs: false     # 顶部显示路径(面包屑)
---


### 准备工作
1. 首先需要安装好python环境，下载好flask库
2. [注册钉钉开放平台](https://open-dev.dingtalk.com/#/)，进入应用开发界面，创建企业内部应用
3. 记录好创建的应用的`Client ID (原 AppKey 和 SuiteKey)`和`Client Secret (原 AppSecret 和 SuiteSecret)`这两个数据
{{< img src="dingtalk_sso_login-01.png">}}

### 流程分析
本文一共需要使用到3个钉钉的api接口，分别是钉钉的页面登录授权、获取用户token接口和获取用户个人信息的接口。


用户使用流程为，点击钉钉登录的超链接，此处为构造的钉钉登录授权页面url，用户使用钉钉账号登录后，带着code数据跳转至开发者设置的回调url中，开发者通过传过来的code使用钉钉接口获取用户tonken，然后再通过token来获取用户的个人信息（包含用户对于当前应用的唯一标识unionid），接着就可以按照登录成功的逻辑进行处理了。

### 具体实现

#### 构造钉钉登录授权页面url
按照钉钉开发者文档的要求进行构造，`redirect_uri`参数填写urlencode编码后的回调网址，`client_id`参数填写上文提到的应用的`Client ID (原 AppKey 和 SuiteKey)`即可。
```shell
https://login.dingtalk.com/oauth2/auth?
redirect_uri=https%3A%2F%2Fwww.aaaaa.com%2Fauth   //换成自己的回调网址，需要进行urlencode
&response_type=code
&client_id=dingxxxxxxx   //应用的AppKey 
&scope=openid   //此处的openId保持不变
&state=dddd
&prompt=consent
```

#### 钉钉开放平台配置
进入钉钉开放平台应用管理，找到分享设置，在`回调域名`处填写好回调域名保存。
{{< img src="dingtalk_sso_login-02.png">}}
再找到权限管理处，开通`通讯录个人信息读权限`的权限。
{{< img src="dingtalk_sso_login-03.png">}}
钉钉开放平台配置就完成了。

#### 使用flask构建web服务
需要使用flask构建两个页面，第一个是将我们构造好的钉钉登录授权页面的url插入其中，第二个页面路径必须是自己设置的回调网址。简要代码如下。

```python
# 页面一
@app.route('/')
def index():
    return '<a href="https://login.dingtalk.com/oauth2/auth?redirect_uri=https%3A%2F%2Fwww.aaaaa.com%2Fauth&response_type=code&client_id=dingpoksntxzuqmbz5oq&scope=openid&prompt=consent">钉钉扫码登录</a>'
```

第一个页面构建好了之后部署测试下能否成功进入钉钉登录授权页面，成功的话如下图所示。
{{< img src="dingtalk_sso_login-04.png">}}

页面二编写接收到code后的业务逻辑代码，实现通过code获取用户token，接着通过token获取用户的个人信息，别忘了将里面的appid和appsecret换成准备工作提到的两个数据。
```python
# 页面二
@app.route('/auth')
def auth():
	# 捕获code
	code = request.args.get('code')
	# 获取access_token，有效期2小时
    access_token = get_access_token(code)
    # 获取user_info
    user_info = get_user_info(access_token)
    # 返回个人信息
    return str(user_info)

def get_access_token(code):
    appid = 'xxx'
    appsecret = 'xxx'
    token_url = "https://api.dingtalk.com/v1.0/oauth2/userAccessToken"
    json_data = {
        "clientId" : appid,
        "clientSecret" : appsecret,
        "code" : code,
        "grantType" : "authorization_code"
    }
    res = requests.post(token_url, json = json_data)
    res_dict = json.loads(res.text)
    access_token = res_dict.get('accessToken')
    return access_token

def get_user_info(access_token):
    headers = {
        'Content-Type': 'application/json',
        'x-acs-dingtalk-access-token': access_token
    }
    res = requests.get('https://api.dingtalk.com/v1.0/contact/users/me', headers = headers)

    res_dict = json.loads(res.text)
    # unionid = res_dict.get('user_info').get('unionid')
    # print("unionid为{}".format(unionid))
    # return unionid
    return res_dict
```
简单整理一下，完整代码如下。
```python
from flask import  Flask    #导入Flask类
from flask import request

import time, requests, urllib, json
app=Flask(__name__)         #实例化并命名为app实例

@app.route('/')
def index():
    return '<a href="https://login.dingtalk.com/oauth2/auth?redirect_uri=https%3A%2F%2Fwww.aaaaa.com%2Fauth&response_type=code&client_id=dingpoksntxzuqmbz5oq&scope=openid&prompt=consent">钉钉扫码登录</a>'

@app.route('/auth')
def auth():
	# 捕获code
	code = request.args.get('code')
	# 获取access_token，有效期2小时
    access_token = get_access_token(code)
    # 获取user_info
    user_info = get_user_info(access_token)
    # 返回个人信息
    return str(user_info)

def get_access_token(code):
    appid = 'xxx'
    appsecret = 'xxx'
    token_url = "https://api.dingtalk.com/v1.0/oauth2/userAccessToken"
    json_data = {
        "clientId" : appid,
        "clientSecret" : appsecret,
        "code" : code,
        "grantType" : "authorization_code"
    }
    res = requests.post(token_url, json = json_data)
    res_dict = json.loads(res.text)
    access_token = res_dict.get('accessToken')
    return access_token

def get_user_info(access_token):
    headers = {
        'Content-Type': 'application/json',
        'x-acs-dingtalk-access-token': access_token
    }
    res = requests.get('https://api.dingtalk.com/v1.0/contact/users/me', headers = headers)

    res_dict = json.loads(res.text)
    # unionid = res_dict.get('user_info').get('unionid')
    # print("unionid为{}".format(unionid))
    # return unionid
    return res_dict

if __name__=="__main__":
    app.run(port=8080,host="127.0.0.1",debug=True)
```

### 测试
部署好并启动服务进行访问，会有钉钉扫码登录的一个超链接
{{< img src="dingtalk_sso_login-05.png">}}
点击超链接跳转到钉钉登录的页面
{{< img src="dingtalk_sso_login-04.png">}}
通过钉钉登录后会展示获取的用户信息
{{< img src="dingtalk_sso_login-06.png">}}
拿到个人信息后就可以无缝接入用户登录成功后的逻辑代码了，比如返回token之类的。

> 参考文章
* [钉钉开放平台实现登录第三方网站](https://open.dingtalk.com/document/orgapp/tutorial-obtaining-user-personal-information)