"""
自动创建URL
"""
from django.conf.urls import url
from django.db.models import ForeignKey, ManyToManyField
from django.http.request import QueryDict
from django.shortcuts import HttpResponse, redirect, render
from types import FunctionType
from django.utils.safestring import mark_safe
from django.urls import reverse

from stark.utils.pagination import Paginator
from django import forms


def get_choice_display(header, field):
    """get_choice_display.
    专用于在列表中显示`Choice`类字段列
    :param header: 希望显示的表头
    :param field: 模型类中的字段
    """

    def inner(self, obj=None, is_header=False):

        if is_header:
            return header
        method = getattr(obj, 'get_%s_display' % field)
        return method()
    return inner


def get_datetime_display(header, field, format="%Y-%m-%d"):
    """get_datetime_display.
    格式化显示日期
    :param header: 表头
    :param field: DateField字段
    :param format: 日期显示格式
    """

    def inner(self, obj=None, is_header=False):
        if is_header:

            return header
        date_time = getattr(obj, field)
        return date_time.strftime(format)
    return inner


def get_m2m_display(header, field):
    """get_m2m_display.
    多对多字段的显示
    :param header:
    :param field:
    """

    def inner(self, obj=None, is_header=False):
        if is_header:
            return header
        queryset = getattr(obj, field).all()
        print(queryset)
        m2m_list = [ele.realname for ele in queryset]
        return ', '.join(m2m_list)
    return inner


class SearchGroup(object):
    def __init__(self, queryset_or_tuple, search_option, verbose_name, querydict):
        # 字段的关联数据
        self.queryset_or_tuple = queryset_or_tuple

        # 字段的SearchOption对象
        self.search_option = search_option

        # 字段的别名
        self.verbose_name = verbose_name

        # request.GET
        self.querydict = querydict

    def __iter__(self):
        yield '<div class="verbose_name">'
        yield self.verbose_name + ':'
        yield '</div>'
        yield '<div class="others">'

        # 获取原来的字段查询条件,用于后续比对
        original_value_list = self.querydict.getlist(self.search_option.field)

        # 全部标签的url设置
        total_querydict = self.querydict.copy()
        total_querydict._mutable = True
        if not original_value_list:
            # 查询条件中没有字段时表明当前全部标签应被选中
            yield '<a href="?%s" class="active">%s</a>' % (total_querydict.urlencode(), "全部")
        else:
            # 查询条件中有字段时，全部的url应该剔除该字段
            total_querydict.pop(self.search_option.field)
            yield '<a href="?%s">%s</a>' % (total_querydict.urlencode(), "全部")

        # 关联数据标签的url设置
        for item in self.queryset_or_tuple:
            text = self.search_option.get_text(item)
            value = str(self.search_option.get_value(item))
            querydict = self.querydict.copy()
            querydict._mutable = True
            if not self.search_option.is_multi:
                querydict[self.search_option.field] = value
                # 查询条件有字段时，对应值的标签应被选中(高亮)
                if value in original_value_list:
                    # 高亮标签再点一次后取消高亮，所以其url应移除该字段
                    querydict.pop(self.search_option.field)
                    yield '<a href="?%s" class="active">%s</a>' % (querydict.urlencode(), text)
                else:
                    yield '<a href="?%s">%s</a>' % (querydict.urlencode(), text)
            else:
                multi_values_list = querydict.getlist(self.search_option.field)
                if value in multi_values_list:
                    multi_values_list.remove(value)
                    querydict.setlist(
                        self.search_option.field, multi_values_list)
                    yield '<a href="?%s" class="active">%s</a>' % (querydict.urlencode(), text)
                else:
                    multi_values_list.append(value)
                    querydict.setlist(
                        self.search_option.field, multi_values_list)
                    yield '<a href="?%s">%s</a>' % (querydict.urlencode(), text)

        yield '</div>'


class SearchOption(object):
    def __init__(self, field, db_condition={}, text_func=None, value_func=None, is_multi=False):
        self.field = field
        self.db_condition = db_condition
        self.text_func = text_func
        self.value_func = value_func
        self.is_multi = is_multi

    # 改写后可以自定义搜索条件
    def get_db_condition(self, request, *args, **kwargs):
        return self.db_condition

    def get_queryset_or_tuple(self, model_class, request, *args, **kwargs):
        """get_queryset_or_tuple.
        根据字段获取对应的关联数据
        :param self:
        :param model_class: 模型类
        """
        # 根据字段名获取model_class中对应的字段对象
        field_obj = model_class._meta.get_field(self.field)
        verbose_name = field_obj.verbose_name

        if isinstance(field_obj, ForeignKey) or isinstance(field_obj, ManyToManyField):
            # ForeignKey|ManyToManyField 应该获取关联表中的数据
            return SearchGroup(field_obj.related_model.objects.filter(**self.get_db_condition(request, *args, **kwargs)), self, verbose_name, request.GET)
        else:
            # IntegerField应该获取choices中的数据
            return SearchGroup(field_obj.choices, self, verbose_name, request.GET)

    def get_text(self, field_obj):
        """get_text.
        自定制组合搜索标签显示的文本:
            1. 如果SearchOption对象没有传入text_func, 则默认IntegerField字段显示其choices内元组的第1位;
            ForeignKey或ManyToMany字段显示其__str__的返回值。
            2. 如果传入text_func, 则显示text_func处理后的文本。
        :param self:
        :param field_obj: 字段对象的关联数据
        """
        if self.text_func:
            return self.text_func(field_obj)
        elif isinstance(field_obj, tuple):
            return field_obj[1]
        else:
            return str(field_obj)

    def get_value(self, field_obj):
        if self.value_func:
            return self.value_func(field_obj)
        elif isinstance(field_obj, tuple):
            return field_obj[0]
        else:
            return field_obj.pk


class StarkModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StarkModelForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control"}


class StarkForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(StarkForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control"}


class StarkHandler(object):
    # 定制页面显示的列
    field_list = []
    # 每页显示数据条数
    per_page_count = 15
    # 是否有添加按钮
    has_add_btn = True

    def get_field_list(self):
        """get_field_list.
        钩子，用于自定义显示的列，如果子类不改写，
        则默认显示self.field_list中规定的列。
        :param self:
        """
        value = []
        if self.field_list:
            value.extend(self.field_list)
            # 这里必须用StarkHandler.xxx, 绑定对象的函数的类型不是Functiontype!
            value.append(StarkHandler.display_edit_delete)
        return value

    def __init__(self, site, model_class, prev):
        self.model_class = model_class
        self.prev = prev
        self.site = site
        self.request = None

    def reverse_url(self, name, *args, **kwargs):
        url_name = '%s:%s' % (self.site.namespace, name)
        base_url = reverse(url_name, args=args, kwargs=kwargs)
        if not self.request.GET:
            return base_url
        else:
            params = self.request.GET.urlencode()
            querydict = QueryDict(mutable=True)
            querydict['_filter'] = params
            return "%s?%s" % (base_url, querydict.urlencode())

    def reverse_add_url(self, *args, **kwargs):
        return self.reverse_url(self.add_url_name, *args, **kwargs)

    def reverse_list_url(self):
        url_name = "%s:%s" % (self.site.namespace, self.list_url_name)
        base_url = reverse(url_name)
        params = self.request.GET.get("_filter")
        if not params:
            url = base_url
        else:
            url = "%s?%s" % (base_url, params)
        return url

    def reverse_edit_url(self, *args, **kwargs):
        return self.reverse_url(self.edit_url_name, *args, **kwargs)

    def reverse_del_url(self, *args, **kwargs):
        return self.reverse_url(self.del_url_name, *args, **kwargs)

    def get_add_btn(self):
        if self.has_add_btn:
            add_url = self.reverse_add_url()
            return "<a class='btn btn-primary' href='%s'>添加</a>" % add_url

    # 自定义ModelForm, 配合get_model_form_class方法使用
    model_form_class = None

    def get_model_form_class(self, is_add=True):
        if self.model_form_class:
            return self.model_form_class

        class DynamicModelClass(StarkModelForm):
            class Meta:
                model = self.model_class
                fields = "__all__"
        return DynamicModelClass

    def save(self, form, is_update=False):
        """save.
        利用ModelForm保存数据之前，预留的钩子
        :param self:
        :param form:
        :param is_update:
        """
        form.save()

    order_list = []

    def get_order_list(self):
        return self.order_list or ["id", ]

    search_list = []

    def get_search_list(self):
        """get_search_list.
        钩子，获取搜索列表
        :param self:
        """
        return self.search_list

    action_list = []

    def get_action_list(self):
        return self.action_list

    search_group = []

    def get_search_group(self):
        return self.search_group

    def get_search_group_condition(self, request):
        condition = {}
        for search_option in self.get_search_group():
            values_list = request.GET.getlist(search_option.field)
            if not values_list:
                continue
            condition['%s__in' % search_option.field] = values_list
        return condition

    def changelist_view(self, request, *args, **kwargs):
        """changelist_view
        列表页面
        1 关于分页器的说明:
            1) 修改每页显示条数请在子类中重写`per_page_count`

        2 关于定制列表的说明:
            1) 注册时采用默认的StarkHandler无定制功能
            2) 将要自定义的字段放入`field_list`类属性中: e.g. ["name", "age",
            `get_choice_display("性别", "gender")`, `display_edit`]
                a) 可以传入字符串或函数
                b) `Choice`类字段采用`get_choice_display`函数处理
                c) 其他自定制列函数参照`display_edit`方法进行定义:

        :param request:
        """

        # 0 批量操作
        action_list = self.get_action_list()

        # 通过函数得到函数名的字符串: func.__name__
        action_dict = {func.__name__: func.text for func in action_list}
        if request.method == "POST":
            action_func_name = request.POST.get("action")
            if action_func_name and action_func_name in action_dict:
                # 利用反射，通过函数名的字符串执行函数
                action_response = getattr(self, action_func_name)(request)
                if action_response:
                    return action_response

        # 1 模糊搜索
        search_list = self.get_search_list()
        search_value = request.GET.get("q", "")
        # Q, 用于构造复杂的ORM查询条件
        from django.db.models import Q
        conn = Q()
        # 各查询条件通过or来连接
        conn.connector = 'OR'
        # search_value不为空时构造查询条件
        if search_value:
            for item in search_list:
                conn.children.append((item, search_value,))

        # 2 组合搜索
        # 2.1 获取配置
        search_group = self.get_search_group()
        # 2.2 根据配置获取字段对象
        search_group_row_list = []
        for ele in search_group:
            search_group_row_list.append(ele.get_queryset_or_tuple(
                self.model_class, request, *args, **kwargs))
        search_group_condition = self.get_search_group_condition(request)

        # 3 排序
        order_list = self.get_order_list()
        queryset = self.model_class.objects.filter(conn).filter(
            **search_group_condition).distinct().order_by(*order_list)

        # 4 分页器
        total_count = queryset.count()
        current_page = request.GET.get("page")
        base_url = request.path_info
        query_params = request.GET.copy()
        query_params._mutable = True
        paginator = Paginator(
            current_page=current_page,
            total_count=total_count,
            base_url=base_url,
            query_params=query_params,
            per_page_count=self.per_page_count,
        )

        # 5 表格
        field_list = self.get_field_list()
        # 5.1 处理表头
        thead_list = []
        if self.field_list:
            for field in field_list:
                # 字段为函数时执行该函数
                if not isinstance(field, FunctionType):
                    verbose_name = self.model_class._meta.get_field(
                        field).verbose_name
                else:
                    verbose_name = field(self, is_header=True)
                thead_list.append(verbose_name)
        else:
            # e.g. [userinfo]
            thead_list.append(self.model_class._meta.model_name)

        # 5.2 处理数据
        data_list = queryset[paginator.start:paginator.end]
        tbody_list = []  # e.g. [[陈洋, cyeext@qq.com, 市场部],]
        for row in data_list:
            tr = []
            if field_list:
                for field in field_list:
                    if not isinstance(field, FunctionType):
                        td = getattr(row, field)
                    else:
                        td = field(self, row)
                    tr.append(td)
            else:
                tr.append(row)  # e.g. [[obj1,], [obj2,]]
            tbody_list.append(tr)

        # 6 增加添加按钮
        add_btn = self.get_add_btn()

        return render(request, "stark/changelist.html", {
            'thead_list': thead_list,
            'tbody_list': tbody_list,
            'paginator': paginator,
            'add_btn': add_btn,
            'search_list': search_list,
            'search_value': search_value,
            'action_dict': action_dict,
            'search_group_row_list': search_group_row_list,
        })

    def add_view(self, request):
        """add_view.
        添加
        :param self:
        """
        model_form_class = self.get_model_form_class()
        form = model_form_class()
        if request.method == "GET":
            return render(request, "stark/change.html", {"form": form})
        form = model_form_class(data=request.POST)
        if form.is_valid():
            self.save(form)
            # 数据保存成功后，跳转回列表页面（携带原来的查询条件）
            return redirect(self.reverse_list_url())
        else:
            return render(request, "stark/change.html", {'form': form})

    def edit_view(self, request, pk):
        """edit_view.
        编辑
        :param self:
        """
        obj = self.model_class.objects.filter(pk=pk).first()
        if not obj:
            return HttpResponse("要修改的对象不存在!")
        model_form_class = self.get_model_form_class(is_add=False)
        if request.method == "GET":
            form = model_form_class(instance=obj)
            return render(request, "stark/change.html", {'form': form})
        form = model_form_class(data=request.POST, instance=obj)
        if form.is_valid():
            self.save(form)
            return redirect(self.reverse_list_url())
        return render(request, "stark/change.html", {'form': form})

    def delete_view(self, request, pk):
        """delete_view.
        删除
        :param self:
        """
        cancel = self.reverse_list_url()
        if request.method == "GET":
            return render(request, 'stark/del.html', {'cancel': cancel})
        self.model_class.objects.filter(pk=pk).delete()
        return redirect(self.reverse_list_url())

    def get_url_name(self, param):
        app_label, model_name = self.model_class._meta.app_label, self.model_class._meta.model_name
        if not self.prev:
            url_name = "%s_%s_%s" % (app_label, model_name, param)
        else:
            url_name = "%s_%s_%s_%s" % (
                app_label, model_name, self.prev, param)
        return url_name

    @property
    def list_url_name(self):
        return self.get_url_name("list")

    @property
    def add_url_name(self):
        return self.get_url_name("add")

    @property
    def edit_url_name(self):
        return self.get_url_name("edit")

    @property
    def del_url_name(self):
        return self.get_url_name("del")

    def wrapper(self, func):
        def inner(request, *args, **kwargs):
            self.request = request
            return func(request, *args, **kwargs)
        return inner

    @property
    def urls(self):
        """urls.
        自定制url, 默认增删查改，子类改写可进行删改
        :param self:
        """
        patterns = [
            url(r'^list/$', self.wrapper(self.changelist_view),
                name=self.list_url_name),
            url(r'^add/$', self.wrapper(self.add_view), name=self.add_url_name),
            url(r'^edit/(?P<pk>\d+)/$', self.wrapper(self.edit_view),
                name=self.edit_url_name),
            url(r'^del/(?P<pk>\d+)/$', self.wrapper(self.delete_view),
                name=self.del_url_name),
        ]

        patterns.extend(self.extra_urls)
        return patterns

    @property
    def extra_urls(self):
        """extra_urls.
        钩子，用于添加自定制的url
        :param self:
        """
        return []

    def display_edit(self, obj=None, is_header=False):
        """display_edit.
         生成编辑列的表头和内容
        :param self:
        :param obj: 可以是字符串或者模型类的实例对象
        :param is_header: 是否为表头
        :return: 可以是传入模型类的某个属性或者字符串
                 如果字符串为标签，需要用mark_safe函数处理后才能在页面渲染

        """
        if is_header:
            return "编辑"
        url = self.reverse_edit_url(obj.pk)
        return mark_safe("<a href='%s'>编辑</a>" % url)

    def display_delete(self, obj=None, is_header=False):
        if is_header:
            return "删除"
        url = self.reverse_del_url(obj.pk)
        return mark_safe("<a href='%s'>删除</a>" % url)

    def display_edit_delete(self, obj=None, is_header=False):
        if is_header:
            return "操作"
        edit_url = self.reverse_edit_url(obj.pk)
        del_url = self.reverse_del_url(obj.pk)
        tpl = "<a href='%s'>编辑</a>|<a href='%s'>删除</a>"
        return mark_safe(tpl % (edit_url, del_url))

    def display_checkbox(self, obj=None, is_header=False):
        if is_header:
            return "选择"
        return mark_safe('<input type="checkbox" name="pk" value="%s"/>' % obj.pk)


class StarkSite(object):
    def __init__(self):
        self._registry = []
        self.app_name = "stark"
        self.namespace = "stark"

    def registry(self, model_class, handler_class=StarkHandler, prev=None):
        """registry.

        :param self:
        :param model_class: models中与数据库相关的模型类
        :param handler_class: 处理请求的视图函数所在的类
        :param prev: 自定义前缀, e.g. /app_label/model_name/prev/list
        """
        self._registry.append({

            "model_class": model_class, "handler": handler_class(self, model_class, prev),
            "prev": prev,
        })

    def get_urls(self):
        """get_urls.
        为注册过的模型类自动生成增删改查路由
        :param self:
        """
        patterns = []

        for item in self._registry:
            model_class = item["model_class"]
            handler = item['handler']
            prev = item['prev']
            app_label, model_name = model_class._meta.app_label, model_class._meta.model_name
            if not prev:
                patterns.append(url(r'^%s/%s/' %
                                    (app_label, model_name), (handler.urls, None, None)))
            else:
                patterns.append(url(r'^%s/%s/%s/' %
                                    (app_label, model_name, prev), (handler.urls, None, None)))
        return patterns

    @property
    def urls(self):
        return self.get_urls(), self.app_name, self.namespace


site = StarkSite()
