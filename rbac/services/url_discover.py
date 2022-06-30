
import re
from django.urls.resolvers import URLPattern, URLResolver
from collections import OrderedDict
from django.conf import settings
from django.utils.module_loading import import_string

def rule_out_url(url):
    """rule_out_url.
    url自动发现功能中排除特定的url
    Args:
        url:
    """
    for pattern in settings.AUTO_DISCOVER_EXCLUDE:

        if re.match(pattern, url):
            return True

def recursively_fetch_url_dict(pre_namespace, pre_url, urlpatterns, ordered_url_dict):
    """recursively_fetch_url_dict.
    递归的获取所有url并以类似于:
    {"user_list": {"name": "rbac:user_list", "url": "/rbac/user/list"},}
    的结构存储
    Args:
        pre_namespace: 上一级的命名空间，用于拼接"name"
        pre_url: 上一级的url, 用于拼接"url"
        urlpatterns: urlconf中的路由表
        ordered_url_dict: 有序字典对象, 用于存放最终的结果
    """
    for item in urlpatterns:
        if isinstance(item, URLPattern):
            # 没有名字的url不予处理
            if not item.name:
                continue
            if pre_namespace:
                name = "%s:%s" % (pre_namespace, item.name)
            else:
                name = item.name
            url = pre_url + item.pattern.regex.pattern
            url = url.replace('^', '').replace('$', '')
            if rule_out_url(url):
                continue
            ordered_url_dict[name] = {
                "name": name,
                "url": url
            }
        elif isinstance(item, URLResolver):
            if pre_namespace:
                if item.namespace:
                    namespace = "%s:%s" % (pre_namespace, item.namespace)
                else:
                    namespace = pre_namespace
            else:
                if item.namespace:
                    namespace = item.namespace
                else:
                    namespace = None
            recursively_fetch_url_dict(namespace, pre_url+item.pattern.regex.pattern, item.url_patterns, ordered_url_dict)

def get_all_urls_dict():
    """get_all_url_dict.
    获取所有的url并存为有序字典
    """
    ordered_url_dict = OrderedDict()
    url_module = import_string(settings.ROOT_URLCONF)
    recursively_fetch_url_dict(None, "/", url_module.urlpatterns, ordered_url_dict)
    print(ordered_url_dict)
    return ordered_url_dict
