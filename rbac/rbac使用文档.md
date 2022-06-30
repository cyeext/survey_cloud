# 基于角色的权限控制(rbac)组件使用文档

## 目录

- [简介](#1)
- [功能](#2)
- [用法](#3)

## 1 简介



本组件用于在任何项目中快速创建权限系统。

## 2 功能

- 权限校验

- 动态菜单

- 导航条

- 项目URL的自动发现与权限的批量增删改查

- 权限的快速分配 

- 权限粒度控制到按钮 



3 用法
---

##### 3.1 将`rbac`组件拷贝至项目根目录

注册`rbac`组件：

```python
# 项目名/settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app01.apps.App01Config',
    'rbac.apps.RbacConfig', # 注册rbac组件
]
```

##### 3.2 将`rbac/migrations`目录中的数据库迁移记录删除

##### 3.3 业务系统中表结构的设计

业务结构的中的用户表需与`rbac`中的用户有继承关系，如：

```python
# rbac/models.py
class UserInfo(models.Model):
    """
    UserInfo Table
    """
    name = CharField(verbose_name="用户名", max_length=32)
    password = CharField(verbose_name="密码", max_length=64)
    email = CharField(verbose_name="邮箱", max_length=32)
    # 严重提醒：Role不要加引号
    role = ManyToManyField(verbose_name="所拥有的的角色", to=Role, blank=True) 

    class Meta:
      	# django以后再做数据库迁移时，不再为UserInfo类创建相关的表以及表结构了。
        # 此类可以当做"父类"，被其他Model类继承。
        abstract = True

    def __str__(self) -> str:
        return self.name
```

```python
# app名/models.py
class UserInfo(RBACUserInfo):
    """
    用户表
    """
    phone = models.CharField(max_length=32, verbose_name='联系方式')
    level_choices = [
        (1, 'T1'),
        (2, 'T2'),
        (3, 'T3'),
    ]

    level = models.IntegerField(choices=level_choices, verbose_name='职级')
    department = models.ForeignKey(to='Department', verbose_name='部门', on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.name
```

##### 3.4 将业务系统中的用户表的路径写到配置文件中

```python
# 项目名/setting.py
# 业务中的用户表
USERINFO = 'app01.models.UserInfo'
```

用于在`rbac`在分配权限时，读取业务表中的用户信息

##### 3.5 业务逻辑开发

将所有的路由都设置一个`name`，如:

```python
# 项目名/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^index/$', acount.index),
    url(r'^login/$', acount.login),
    url(r'^logout/$', acount.logout),
    url(r'^user/list/$', user.user_list, name="user_list"),
    url(r'^user/add/$', user.user_add, name="user_add"),
    url(r'^user/edit/(?P<pk>\d+)/$', user.user_edit, name='user_edit'),
    url(r'^user/del/(?P<pk>\d+)/$', user.user_del, name='user_del'),
    url(r'^user/reset/password/(?P<pk>\d+)/$', user.user_reset, name='user_reset'),
    url(r'^host/list/$', host.host_list, name="host_list"),
    url(r'^host/add/$', host.host_add, name="host_add"),
    url(r'^host/edit/(?P<pk>\d+)/$', host.host_edit, name='host_edit'),
    url(r'^host/del/(?P<pk>\d+)/$', host.host_del, name='host_del'),
]
```

用于反向生成url和粒度控制到按钮级别的权限控制

##### 3.6 权限信息录入

在路由中加入rbac的路由分发，注意：必须设置`namespace`参数

```python
urlpatterns = [
  	...,
  	url(r'^rbac/', include('rbac.urls', namespace='rbac')),
]
```

禁用动态菜单和导航条组件

```django
{# rbac/templates/layouts.html #}
...
    <div class="pg-body">
        <div class="left-menu">
            <div class="menu-body">
                {# {% dynamic_menu request %} #}
            </div>
        </div>
        <div class="right-body">
            {# {% navi request %} #}
            {% block content %} {% endblock %}
        </div>
    </div>
...
```



在`rbac`组件提供的地址进行权限录入

 - 用户信息录入: http://127.0.0.1/8000/rbac/user/list/
 - 角色信息录入: http://127.0.0.1/8000/rbac/role/list/
 - 菜单和权限信息录入: http://127.0.0.1/8000/rbac/menu/list/

相关配置: 

自动发现路由中的URL时，应排除的URL：

```python
# 项目名/settings.py
AUTO_DISCOVER_EXCLUDE = [
    '/index/',
    '/login/',
    '/logout/',
    '/admin/.*',
]
```

##### 3.7 编写首页、用户登录和注销的逻辑

```python
# app名/views/account.py

import requests
from django.shortcuts import render, HttpResponse, redirect
from app01 import models
from rbac.services import init_access


def index(request):
    """
    首页
    Args:
        request:

    Returns:

    """
    return render(request, 'app01/index.html')


def login(request):
    """
    登录
    Args:
        request:

    Returns:

    """
    if request.method == "GET":
        return render(request, 'app01/login.html')
    usr = request.POST.get("usr")
    psw = request.POST.get("psw")
    print(usr, psw)
    user_obj = models.UserInfo.objects.filter(name=usr, password=psw).first()
    print(user_obj)
    if not user_obj:
        error = "用户名或密码错误!"
        return render(request, "app01/login.html", {"error": error})
    else:
        init_access.init_access(user_obj, request)
        return redirect("/index/")


def logout(request):
    """
    注销
    Args:
        reqeust:

    Returns:
    """
    request.session.delete()
    return redirect('/login/')
```

相关配置:

```python
# 项目名/settings.py

# 权限在session中存储的key
ACCESS_SESSION_KEY = "access_url_list_key"

# 静态菜单在session中存储的key
MENU_SESSION_KEY = "menu_list_key"
```

##### 3.8 激活rbac组件的权限校验中间件

```python
# 项目名/settings.py

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'rbac.middlewares.rbac.RbacMiddleware', # rbac组件的权限校验中间件
]
```

相关配置:

```python
# 项目名/settings.py

# 无需登录就能访问的URL名单
VALID_URLS = [
    '/login/',
    '/admin/.*/',
]

# 登录成功就可以访问的URL名单
LOGGED_URLS = [
    '/index/',
    '/logout/',
]
```

启用动态菜单和导航条组件

##### 3.9 权限粒度控制到按钮级别

利用`has_permision` `simple tag`来给页面的按钮进行权限控制，示例:

```django
{# rbac/temlates/rbac/menu_list.html #}
<table class="table">
  <thead>
    <tr>
      <th>名称</th>
      <th>CODE&URL</th>
      {% if reqeuest|has_access:"access_edit" or request|has_access:"access_del" %}
      <th>选项</th>
      {% endif %}
    </tr>
  </thead>
  <tbody>
    {% for row in access_queryset %}
    <tr>
      <td rowspan="2">
        {{ row.title }}
      </td>
      <td>
        {{ row.name }}
      </td>
      <td>
        {% if request|has_access:"access_edit" %}
        <a style="color: #333333;"
           href="{% url_with_state request 'rbac:access_edit' pk=row.id %}">
          <i class="fa fa-edit" aria-hidden="true"></i>
        </a>
        {% endif %}
        {% if request|has_access:"access_del" %}
        <a style="color: #d9534f;"
           href="{% url_with_state request 'rbac:access_del' pk=row.id %}">
          <i class="fa fa-trash-o"></i>
        </a>
        {% endif %}
      </td>

    </tr>
    <tr>
      <td colspan="2" style="border-top: 0">
        {{ row.url }}
      </td>
    </tr>

    {% endfor %}

  </tbody>
</table>

```
