import re

from django.conf import settings
from django.http.response import HttpResponse
from django.utils.deprecation import MiddlewareMixin


class RbacMiddleware(MiddlewareMixin):
    """
    权限检查
    """

    def process_request(self, request):
        """process_request.

        :param self:
        :param request:
        """
        # step1 获取当前路径
        current_url = request.path_info

        # step2 将通用的权限设置为白名单
        valid_urls = settings.VALID_URLS

        # step3 当前访问路径与白名单正则匹配
        for item in valid_urls:
            if re.match(item, current_url):
                # step3.1 匹配成功跳过此中间件
                return None

        # 获取权限列表
        access_dict = request.session.get(settings.ACCESS_SESSION_KEY)

        # 初始化导航条
        navi = [
            {'title': '首页', 'url': '/index/', 'class': 'active'}
        ]

        # 以下URL登录成功后即可访问
        for item in settings.LOGGED_URLS:
            if re.match(item, current_url):
                # 无展开的动态菜单
                request.related_menu_id = 0
                # 无导航信息
                request.navi = navi
                return None

        # 权限列表为空，提示先登录
        if not access_dict:
            return HttpResponse("未获取到用户权限信息，请登录！")

        navi[0]['class'] = None

        # 设置权限flag
        flag = False
        for item in access_dict.values():
            pattern = r"^%s$" % item.get('url')
            # step5.1 正则匹配，匹配则将权限flag设置为True并跳出循环
            if re.match(pattern, current_url):
                flag = True
                # 设置request.related_menu_id以于传入inclusion_tag中
                request.related_menu_id = item.get('pid') or item.get('id')

                # 设置request.navi以传入inclusion_tag中
                if item.get('pid'):
                    navi.extend([
                        {'title': item.get('p_title'), 'url': item.get('p_url')},
                        {'title': item.get('title'), 'url': item.get('url'), 'class': 'active'},
                    ])
                else:
                    navi.extend([
                        {'title': item.get('title'), 'url': item.get('url'), 'class': 'active'},
                    ])
                request.navi = navi
                break
        # 权限flag为False无权访问
        if not flag:
            return HttpResponse("无权访问")
