"""
url相关工具
"""
from django.shortcuts import reverse
from django.template import Library
from django.http import QueryDict

register = Library()


def reverse_with_state(request, name, *args, **kwargs):
    """
    利用reverse反向生成带初始状态的url
    :param request:
    :param name:
    :param args:
    :param kwargs:
    :return:
    """
    # 根据"namespace:name"反向生成url
    url = reverse(name, args=args, kwargs=kwargs)
    # 获取初始状态
    original_state = request.GET.get("_filter")
    # 有初始状态则将初始状态拼接到url上
    if original_state:
        url = "%s?%s" % (url, original_state)
    return url


@register.simple_tag
def url_with_state(request, name, *args, **kwargs):
    """
    保留选中状态的url标签
    :param request:
    :param name:
    :return:
    """
    original_url = reverse(name, args=args, kwargs=kwargs)
    if not request.GET.urlencode():
        return original_url
    query_dict = QueryDict(mutable=True)
    query_dict["_filter"] = request.GET.urlencode()
    final_url = "%s?%s" % (original_url, query_dict.urlencode())
    return final_url
