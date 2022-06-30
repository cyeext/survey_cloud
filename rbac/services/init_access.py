from django.conf import settings


def init_access(current_user, request):
    '''
    :param current_user:
    :param request:
    :return:
    '''
    access_queryset = current_user.role.filter(access__isnull=False).values(
        'access__name',
        'access__title',
        'access__url',
        'access__pid__id',
        'access__pid__title',
        'access__pid__url',
        'access__id',
        'access__menu__id',
        'access__menu__title',
        'access__menu__icon',
    ).distinct()

    access_dict = {}
    menu_dict = {}

    for item in access_queryset:
        access_dict[item.get('access__name')] = {
            'id': item.get('access__id'),
            'title': item.get('access__title'),
            'url': item.get('access__url'),
            'pid': item.get('access__pid__id'),
            'p_title': item.get('access__pid__title'),
            'p_url': item.get('access__pid__url'),
        }
        print(access_dict.keys())

        # 获取一级菜单id
        menu_id = item.get('access__menu__id')

        # 非二级菜单，跳过
        if not menu_id:
            continue

        # 是二级菜单，创建二级菜单信息
        node = {
            "id": item.get('access__id'),
            "title": item.get('access__title'),
            "url": item.get('access__url'),
        }
        # node对应的一级菜单在字典中，将其append到对应的children列表中
        if menu_id in menu_dict:
            menu_dict[menu_id]["children"].append(node)
        else:
            menu_dict[menu_id] = {
                'title': item.get('access__menu__title'),
                'icon': item.get('access__menu__icon'),
                'children': [node],
            }

    request.session[settings.ACCESS_SESSION_KEY] = access_dict
    request.session[settings.MENU_SESSION_KEY] = menu_dict
