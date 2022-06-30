"""
Menu相关
"""
from collections import OrderedDict
from django.shortcuts import render, redirect, HttpResponse
from rbac import models
from rbac.forms.menu import StaticModelForm, DynamicModelForm, AccessModelForm, MultiAccessAddForm, MultiAccessUpdateForm
from rbac.services.url import reverse_with_state
from rbac.services.url_discover import get_all_urls_dict
from django.forms import formset_factory
from django.utils.module_loading import import_string

from django.conf import settings
UserInfo = import_string(settings.USERINFO)


def menu_list(request):
    """
    菜单和权限了列表
    :param request:
    :return:
    """
    menu_queryset = models.Menu.objects.all()
    menu_id = request.GET.get("mid")  # 被选中的静态菜单id
    # 检查menu_id是否有效，防止用户伪造menu_id
    if not models.Menu.objects.filter(pk=menu_id).exists():
        menu_id = None
    dynamic_id = request.GET.get("did")  # 被选中的动态菜单id
    if menu_id:
        # 注意: menu_id=None会筛选出所有非动态菜单权限而非输出空的queryset！
        dynamic_queryset = models.Access.objects.filter(menu_id=menu_id)
    else:
        dynamic_queryset = []
    # 检查dynamic_id是否有效，防止用户伪造
    if not models.Access.objects.filter(pk=dynamic_id).exists():
        dynamic_id = None
    if dynamic_id:
        access_queryset = models.Access.objects.filter(pid=dynamic_id)
    else:
        access_queryset = []
    return render(request, "rbac/menu_list.html", {
        "menu_queryset": menu_queryset,
        "menu_id": menu_id,
        "dynamic_queryset": dynamic_queryset,
        "dynamic_id": dynamic_id,
        "access_queryset": access_queryset,
    })


def static_add(request):
    """
    增加静态菜单
    :param request:
    :return:
    """
    url = reverse_with_state(request, "rbac:menu_list")
    if request.method == "GET":
        form = StaticModelForm()
        return render(request, "rbac/change.html", {'form': form})
    form = StaticModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect(url)
    return render(request, 'rbac/change.html', {'form': form})


def static_edit(request, pk):
    """
    修改静态菜单
    :param request:
    :param pk:
    :return:
    """
    url = reverse_with_state(request, "rbac:menu_list")
    obj = models.Menu.objects.filter(pk=pk).first()
    if not obj:
        return HttpResponse("该静态菜单不存在！")
    if request.method == "GET":
        form = StaticModelForm(instance=obj)
        return render(request, "rbac/change.html", {'form': form})
    form = StaticModelForm(data=request.POST, instance=obj)
    if form.is_valid():
        form.save()
        return redirect(url)
    return render(request, 'rbac/change.html', {'form': form})


def static_del(request, pk):
    """
    删除静态菜单
    :param request:
    :param pk:
    :return:
    """
    url = reverse_with_state(request, "rbac:menu_list")
    if request.method == "GET":
        return render(request, 'rbac/del.html', {'cancel': url})
    models.Menu.objects.filter(pk=pk).delete()
    return redirect(url)


def dynamic_add(request, mid):
    """
    添加动态菜单
    :param request:
    :param mid: 动态菜单所属静态菜单id(用预设值默认值)
    :return:
    """
    static_menu_obj = models.Menu.objects.filter(pk=mid).first()
    if request.method == "GET":
        # 默认值的设置方法`initial=xxx`
        form = DynamicModelForm(initial={"menu": static_menu_obj})
        return render(request, "rbac/change.html", {"form": form})
    form = DynamicModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect(reverse_with_state(request, "rbac:menu_list"))
    return render(request, "rbac/change.html", {"form": form})


def dynamic_edit(request, pk):
    """
    编辑动态菜单
    :param pk:
    :param request:
    :return:
    """
    dynamic_menu_obj = models.Access.objects.filter(pk=pk).first()
    if request.method == "GET":
        form = DynamicModelForm(instance=dynamic_menu_obj, initial={
            "menu": dynamic_menu_obj.menu})
        return render(request, "rbac/change.html", {"form": form})
    form = DynamicModelForm(data=request.POST, instance=dynamic_menu_obj)
    if form.is_valid():
        form.save()
        return redirect(reverse_with_state(request, "rbac:menu_list"))
    return render(request, "rbac/change.html", {"form": form})


def dynamic_del(request, pk):
    """
    删除动态菜单
    :param request:
    :param pk:
    :return:
    """
    url = reverse_with_state(request, "rbac:menu_list")
    if request.method == "GET":
        return render(request, 'rbac/del.html', {'cancel': url})
    models.Access.objects.filter(pk=pk).delete()
    return redirect(url)


def access_add(request, did):
    """
    添加权限
    :param request:
    :param did:
    :return:
    """
    if request.method == "GET":
        # 默认值的设置方法`initial=xxx`
        form = AccessModelForm()
        return render(request, "rbac/change.html", {"form": form})
    form = AccessModelForm(data=request.POST)
    if form.is_valid():
        dynamic_obj = models.Access.objects.filter(pk=did).first()
        # 防止用户伪造选定的动态菜单
        if not dynamic_obj:
            return HttpResponse("该动态菜单不存在，请重新选择")
        form.instance.pid = dynamic_obj
        form.save()
        return redirect(reverse_with_state(request, "rbac:menu_list"))
    return render(request, "rbac/change.html", {"form": form})


def access_edit(request, pk):
    """
    编辑权限
    :param pk:
    :param request:
    :return:
    """
    access_obj = models.Access.objects.filter(pk=pk).first()
    if request.method == "GET":
        form = AccessModelForm(instance=access_obj, initial={
            "menu": access_obj.menu})
        return render(request, "rbac/change.html", {"form": form})
    form = AccessModelForm(data=request.POST, instance=access_obj)
    if form.is_valid():
        form.save()
        return redirect(reverse_with_state(request, "rbac:menu_list"))
    return render(request, "rbac/change.html", {"form": form})


def access_del(request, pk):
    """
    删除权限
    :param request:
    :param pk:
    :return:
    """
    url = reverse_with_state(request, "rbac:menu_list")
    if request.method == "GET":
        return render(request, "rbac/del.html", {"cancel": url})
    models.Access.objects.filter(pk=pk).delete()
    return redirect(url)


def multi_access(request):
    """multi_access.
    批量权限操作
    Args:
        request:
    """
    post_type = request.GET.get("type")
    generate_formset_class = formset_factory(MultiAccessAddForm, extra=0)
    update_formset_class = formset_factory(MultiAccessUpdateForm, extra=0)
    generate_formset = None
    update_formset = None
    if request.method == "POST" and post_type == "generate":
        formset = generate_formset_class(data=request.POST)
        if formset.is_valid():
            proxy = formset.cleaned_data
            has_error = False
            object_list = []
            for i in range(0, formset.total_form_count()):
                row_dict = proxy[i]
                try:
                    new_object = models.Access(**row_dict)
                    new_object.validate_unique()
                    object_list.append(new_object)
                except Exception as e:
                    formset.errors[i].update(e)
                    generate_formset = formset
                    has_error = True
            if not has_error:
                models.Access.objects.bulk_create(object_list, batch_size=100)
        else:
            generate_formset = formset
    if request.method == "POST" and post_type == "update":
        formset = update_formset_class(data=request.POST)
        if formset.is_valid():
            proxy = formset.cleaned_data
            for i in range(0, formset.total_form_count()):
                row_dict = proxy[i]
                access_id = row_dict.pop("id")
                update_obj = models.Access.objects.filter(pk=access_id).first()
                try:
                    for k, v in row_dict.items():
                        setattr(update_obj, k, v)
                    update_obj.validate_unique()
                    update_obj.save()
                except Exception as e:
                    formset.errors[i].update(e)
                    update_formset = formset
        else:
            update_formset = formset
    # 1. 获取项目中所有的url
    auto_discover_url_dict = get_all_urls_dict()
    auto_discover_url_name_set = set(auto_discover_url_dict.keys())
    # 2. 获取数据库中所有url
    access_queryset = models.Access.objects.all().values(
        "id", "title", "url", "name", "menu_id", "pid_id")
    access_dict = OrderedDict()
    access_name_set = set()

    for item in access_queryset:
        access_dict[item["name"]] = item
        access_name_set.add(item["name"])
    # 3. 计算待添加、删除和修改的url
    # 3.1 待添加的url的formset
    generate_url_set = auto_discover_url_name_set - access_name_set
    print(access_dict)
    # generate_formset为空，说明为GET请求
    if not generate_formset:
        generate_formset = generate_formset_class(
            initial=[v for k, v in auto_discover_url_dict.items() if k in generate_url_set])
    # 3.2 待删除的url的list
    delete_set = access_name_set - auto_discover_url_name_set
    delete_list = [v for k, v in access_dict.items() if k in delete_set]
    # 3.3 待更新url的formset
    update_set = access_name_set & auto_discover_url_name_set
    # 对access_dict进行处理，如果同名情况下自动发现的url和数据库中不一致，则将其设置为“数据不一致，请检查！”
    for k, v in access_dict.items():
        auto_discover_row = auto_discover_url_dict.get(k)
        if not auto_discover_row:
            continue
        if auto_discover_row["url"] != v["url"]:
            v["url"] = "数据不一致，请检查!"
    # update_formset为空，说明为GET请求
    if not update_formset:
        update_formset = update_formset_class(
            initial=[v for k, v in access_dict.items() if k in update_set])
    return render(request, "rbac/multi_access.html", {
        "generate_formset": generate_formset,
        "delete_list": delete_list,
        "update_formset": update_formset,
    }
    )


def multi_access_del(request, pk):
    """multi_access_del.
    批量操作页面的权限删除
    Args:
        request:
        pk:
    """
    url = reverse_with_state(request, "rbac:multi_access")
    if request.method == "GET":
        return render(request, 'rbac/del.html', {'cancel': url})
    models.Access.objects.filter(pk=pk).delete()
    return redirect(url)


def access_distribute(request):
    """access_distribute.
    用户、角色、权限的分配
    Args:
        request:
    """
    # 获取当前用户
    uid = request.GET.get("uid")
    user_obj = UserInfo.objects.filter(id=uid).first()
    # 防止用户伪造
    if not user_obj:
        uid = None
    # 获取当前角色
    rid = request.GET.get("rid")
    role_obj = models.Role.objects.filter(id=rid).first()
    if not role_obj:
        rid = None

##############################开始##############################
    if request.method == "POST" and request.POST.get("type") == "roles":
        roles_list = request.POST.getlist("roles")
        if not user_obj:
            return HttpResponse("请先选择用户再分配角色")
        user_obj.role.set(roles_list)
    if request.method == "POST" and request.POST.get("type") == "access":
        access_list = request.POST.getlist("access")
        if not role_obj:
            return HttpResponse("请先选择角色再分配权限")
        role_obj.access.set(access_list)
##############################结束##############################

    # 获取当前用户所拥有的的角色
    if uid:
        roles_owned_by_user = user_obj.role.all()
    else:
        roles_owned_by_user = []
    roles_owned_by_user_dict = {item.id: None for item in roles_owned_by_user}

    # 如果选中角色，优先显示角色所拥有的的权限
    # 如果没有选中角色，才显示用户所有用的权限
    access_owned_dict = {}
    if rid:
        access_owned = role_obj.access.all()
        access_owned_dict = {item.id for item in access_owned}
    elif uid:
        access_owned = user_obj.role.filter(
            access__isnull=False).values("access").distinct()
        access_owned_dict = {item["access"]: None for item in access_owned}
    else:
        access_owned = []
        access_owned_dict = {}


    # 获取所有用户数据
    user_queryset = UserInfo.objects.all()

    # 获取所有角色数据
    role_queryset = models.Role.objects.all()

    """
    获取所有的静态菜单、动态菜单、权限，数据结构如下:
    [
        {
            'id': 1,
            'title': '信息管理',
            'children': [
            {
                'id': 84,
                'title': '客户列表',
                'menu_id': 1,
                'children': [
                {
                    'id': 86,
                    'title': '编辑客户',
                    'pid_id': 84
                },
                ],
            }],
        },
    ]
    """

    static_queryset = models.Menu.objects.all().values("id", "title")
    dynamic_queryset = models.Access.objects.filter(
        menu__isnull=False).values("id", "title", "menu_id")
    access_queryset = models.Access.objects.filter(
        menu__isnull=True).values("id", "title", "pid_id")
    static_dict = {}
    for item in static_queryset:
        item["children"] = []
        static_dict[item["id"]] = item
    dynamic_dict = {}
    for item in dynamic_queryset:
        item["children"] = []
        dynamic_dict[item["id"]] = item
        static_dict[item["menu_id"]]["children"].append(item)
    for item in access_queryset:
        if not item["pid_id"]:
            continue
        dynamic_dict[item["pid_id"]]["children"].append(item)
    return render(request, 'rbac/access_distribute.html', {
        "user_queryset": user_queryset,
        "role_queryset": role_queryset,
        "static_queryset": static_queryset,
        "uid": uid,
        "roles_owned_by_user_dict": roles_owned_by_user_dict,
        "rid": rid,
        "access_owned_dict": access_owned_dict,
    })

