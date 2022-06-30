import re
from django.template import Library
from django.conf import settings
from collections import OrderedDict
from rbac.services import url

register = Library()


# 会搜索rbac/templates/rbac/static_menu.html
@register.inclusion_tag('rbac/static_menu.html')
def static_menu(request):
    '''
    一级菜单创建
    :param request:
    :return:
    '''

    menu_list = request.session.get(settings.MENU_SESSION_KEY)

    # static_menu.html中的所有{{ menu_list }}都会被替换为`menu_list`
    return {'menu_list': menu_list}


@register.inclusion_tag('rbac/dynamic_menu.html')
def dynamic_menu(request):
    '''
    二级菜单创建
    :param request:
    :return:
    '''
    print(request.navi)

    menu_dict = request.session.get(settings.MENU_SESSION_KEY)
    # 对`menu_dict`的key进行排序-->key的列表
    keys_list = sorted(menu_dict)
    # 初始化有序列表
    ordered_menu = OrderedDict()

    for key in keys_list:
        # 取出key对应val
        val = menu_dict[key]

        # 对val进行修改
        # 以及菜单默认附带`hide``class`
        val['class'] = 'hide'
        for child in val['children']:
            if child['id'] == request.related_menu_id:
                child['class'] = 'active'
                val['class'] = ''
                break
        # 将修改后的key-val对放入有序列表中
        ordered_menu[key] = val

    return {'menu_dict': ordered_menu}


@register.inclusion_tag('rbac/navi.html')
def navi(request):
    '''
    导航条创建
    :param request:
    :return:
    '''
    return {'navi_list': request.navi}


@register.filter
def has_access(request, name):
    '''
    判断是否有权限
    :param request:
    :param name:
    :return:
    '''
    if name in request.session[settings.ACCESS_SESSION_KEY]:
        return True


##############################开始##############################
@register.simple_tag
def url_with_state(request, name, *args, **kwargs):
    return url.url_with_state(request, name, *args, **kwargs)
##############################结束##############################
