"""
首页、登录、注销
"""
from django.shortcuts import render, redirect
from web import models
from rbac.services import init_access


def index(request):
    """
    首页
    Args:
        request:

    Returns:

    """
    return render(request, 'web/index.html')


def login(request):
    """
    登录
    Args:
        request:

    Returns:

    """
    if request.method == "GET":
        return render(request, 'web/login.html')
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
