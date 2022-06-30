"""
用户管理
"""
from django.shortcuts import render, redirect,  HttpResponse
from rbac import models
from rbac.forms.user import UserInfoModelForm, PasswordModelForm, UpdateUserModelForm


def user_list(request):
    '''
    用户列表
    :param request:
    :return:
    '''
    user_queryset = models.UserInfo.objects.all()
    return render(request, 'rbac/user_list.html', {'user_queryset': user_queryset})


def user_add(request):
    '''
    添加用户
    :param request:
    :return:
    '''
    if request.method == "GET":
        form = UserInfoModelForm()
        return render(request, 'rbac/change.html', {'form': form})
    form = UserInfoModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect(reverse('rbac:user_list'))
    return render(request, 'rbac/change.html', {'form': form})


def user_edit(request, pk):
    '''
    编辑用户
    :param request:
    :param pk: 待编辑用户的id
    :return:
    '''
    obj = models.UserInfo.objects.filter(pk=pk).first()
    if not obj:
        return HttpResponse("该用户不存在!")
    if request.method == "GET":
        form = UpdateUserModelForm(instance=obj)
        return render(request, "rbac/change.html", {"form": form})
    form = UpdateUserModelForm(data=request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return redirect(reverse('rbac:user_list'))
    return render(request, 'rbac/change.html', {'form': form})


def user_reset(request, pk):
    '''
    重置密码
    :param request:
    :param pk:
    :return:
    '''
    obj = models.UserInfo.objects.filter(pk=pk).first()
    if not obj:
        return HttpResponse("该用户不存在！")
    if request.method == "GET":
        form = PasswordModelForm()
        return render(request, "rbac/change.html", {"form": form})
    form = PasswordModelForm(data=request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return redirect(reverse("rbac:user_list"))
    return render(request, "rbac/change.html", {"form": form})


def user_del(request, pk):
    '''
    删除用户
    :param request:
    :param pk:
    :return:
    '''
    original_url = reverse("rbac:user_list")
    if request.method == "GET":
        return render(request, 'rbac/del.html', {'cancel': original_url})
    models.UserInfo.objects.filter(pk=pk).delete()
    return redirect(reverse("rbac:user_list"))
