from django.shortcuts import render, HttpResponse
from rbac import models

def manual_list(request):
    '''
    用户列表
    :param request:
    :return:
    '''
    md_obj = models.Manual.objects.all().first()
    content = md_obj.get_markdown_content()

    return render(request, 'rbac/manual_list.html', {"content": content})