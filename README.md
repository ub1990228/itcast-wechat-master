# itcast_wechat

### 运行环境搭建

  * 环境搭建：[阿里云 ubuntu-x64 python+django+mysql 开发环境搭建
](http://www.mycode.net.cn/platform/linux-unix/938.html)

### 如何部署

* 克隆项目到本地

  ```
  git clone https://github.com/nmgwddj/itcast_wechat.git
  ```
* 创建数据库

  使用如下命令在 mysql 中创建数据库
  ```
  CREATE DATABASE itcast_wechat DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
  ```

* 修改项目中连接数据库的配置信息

  打开 `itcast_wechat/settings.py` 找到如下信息，将信息修改为你得数据库用户名和密码即可
  ```
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.mysql',
          'NAME': 'itcast_wechat',
          'USER': 'root',
          'PASSWORD': 'your database password',
          'HOST': '',
          'PORT': '3306'
      }
  }
  ```

* 设定你的微信公共号信息

  在一切开始之前，你首先要具备一个开发者账号，可以到微信开发者页面申请一个临时的开发者账号，并配置好你的 URL 等信息，URL 地址见下方“修改你得回调 URL”

  打开 `wechat/config.py` 配置文件，修改 Token、AppID、AppSecret 为你微信开发者账号所分配的信息，如下所示

  ```
  WEIXIN_TOKEN = 'itcast_wechat'
  WEIXIN_APPID = 'wx63afd8910ac8****'
  WEIXIN_APPSECRET = '06abca4d83a582c46a37957c4c49****'
  ```
* 修改你的回调 URL

  `CREATE_MENU_URL` 参数表示了你接收微信的 URL 地址是什么，你只需要将 http://xxxx/user_info/ 中得 xxxx 替换成你的域名即可。（注意，该域名必须要在微信后台进行绑定，否则是无法使用的，更多请参考微信的开发者手册）

* 运行 django 后台程序

  ```
  同步数据库
  python manage.py migrate

  创建管理员，根据提示完成创建
  python manage.py createsuperuser

  运行后台程序
  python manage.py runserver
  ```
  运行成功后，你可以访问 http://xxxx/admin/ （xxxx为你得服务器管理地址）来添加数据以提供前台展示。

* 创建菜单

  由于微信的菜单接口是需要我们手动创建的，所以你需要访问项目中已经写好的创建菜单的 URL 地址来给你得微信公共号创建菜单，创建菜单的 URL 地址为 http://xxxx/create_menu/

  访问成功后你的微信公共号就可以看到一个名为“我得传智历程”的按钮（要修改按钮文字请参考相应 create_menu 地址的处理函数），在微信中点击该按钮就可以跳转到我们的程序页面。
