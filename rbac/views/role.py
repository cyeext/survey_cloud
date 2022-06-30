"""
角色管理
"""
from django.shortcuts import render, redirect, reverse, HttpResponse
from rbac import models
from rbac.forms.role import RoleModelForm


def role_list(request):
    '''
    角色列表
    :param request:
    :return:
    '''
    role_queryset = models.Role.objects.all()
    return render(request, 'rbac/role_list.html', {'role_queryset': role_queryset})


def role_add(request):
    '''
    添加角色
    :param request:
    :return:
    '''
    if request.method == "GET":
        form = RoleModelForm()
        return render(request, 'rbac/change.html', {'form': form})
    form = RoleModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect(reverse('rbac:role_list'))
    return render(request, 'rbac/change.html', {'form': form})


def role_edit(request, pk):
    '''
    编辑角色
    :param request:
    :param pk: 待编辑角色的id
    :return:
    '''
    obj = models.Role.objects.filter(pk=pk).first()
    if not obj:
        return HttpResponse("该用户不存在!")
    if request.method == "GET":
        form = RoleModelForm(instance=obj)
        return render(request, "rbac/change.html", {"form": form})
    form = RoleModelForm(data=request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return redirect(reverse('rbac:role_list'))
    return render(request, 'rbac/change.html', {'form': form})


##################################################开始##################################################
def role_del(request, pk):
    '''
    删除角色
    :param request:
    :param pk:
    :return:
    '''
    original_url = reverse("rbac:role_list")
    if request.method == "GET":
        return render(request, 'rbac/del.html', {'cancel': original_url})
    models.Role.objects.filter(pk=pk).delete()
    return redirect(reverse("rbac:role_list"))
##################################################结束##################################################

