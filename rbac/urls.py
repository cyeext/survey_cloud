from django.conf.urls import url
from rbac.views import role, user, menu

app_name = 'rbac'

urlpatterns = [
    url(r'^role/list/$', role.role_list, name='role_list'),
    url(r'^role/add/$', role.role_add, name='role_add'),
    url(r'^role/edit/(?P<pk>\d+)/$', role.role_edit, name='role_edit'),
    url(r'^role/del/(?P<pk>\d+)/$', role.role_del, name='role_del'),
    # url(r'^user/list/$', user.user_list, name='user_list'),
    # url(r'^user/add/$', user.user_add, name='user_add'),
    # url(r'^user/edit/(?P<pk>\d+)/$', user.user_edit, name='user_edit'),
    # url(r'^user/del/(?P<pk>\d+)/$', user.user_del, name='user_del'),
    # url(r'^user/reset/password/(?P<pk>\d+)/$', user.user_reset, name='user_reset'),
    url(r'^menu/list/$', menu.menu_list, name='menu_list'),
    url(r'^static/add/$', menu.static_add, name='static_add'),
    url(r'^static/edit/(?P<pk>\d+)/$', menu.static_edit, name='static_edit'),
    url(r'^static/del/(?P<pk>\d+)/$', menu.static_del, name='static_del'),
    url(r'^dynamic/add/(?P<mid>\d+)/$', menu.dynamic_add, name='dynamic_add'),
    url(r'^dynamic/edit/(?P<pk>\d+)/$', menu.dynamic_edit, name='dynamic_edit'),
    url(r'^dynamic/del/(?P<pk>\d+)/$', menu.dynamic_del, name='dynamic_del'),
    url(r'^access/add/(?P<did>\d+)/$', menu.access_add, name='access_add'),
    url(r'^access/edit/(?P<pk>\d+)/$', menu.access_edit, name='access_edit'),
    url(r'^access/del/(?P<pk>\d+)/$', menu.access_del, name='access_del'),
    url(r'^multi/access/$', menu.multi_access, name="multi_access"),
    url(r'^multi/access/del/(?P<pk>\d+)/$', menu.multi_access_del, name="multi_access_del"),
##############################开始##############################
    url(r'^access/distribute/$', menu.access_distribute, name="access_distribute"),
##############################结束##############################
]
