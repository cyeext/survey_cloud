from django.http import JsonResponse
from django.shortcuts import HttpResponse, render
from django.utils.safestring import mark_safe
from pyecharts.charts.base import json
from stark.service.v1 import SearchOption, StarkHandler, StarkModelForm, get_datetime_display, get_m2m_display, get_choice_display
from web import models
from stark.forms.widgets import DateTimePickerInput
from django.conf.urls import url
from django.conf import settings

from pyecharts.charts import Bar, Line
from pyecharts import options as opts
from django.shortcuts import render
from jinja2 import Environment, FileSystemLoader
from pyecharts.globals import CurrentConfig

CurrentConfig.GLOBAL_ENV = Environment(
    loader=FileSystemLoader("./web/templates/pyecharts"))


class SensorModelForm(StarkModelForm):
    class Meta:
        model = models.Sensor
        fields = "__all__"
        widgets = {
            "create_date": DateTimePickerInput,
        }


class SensorHandler(StarkHandler):
    def display_record_graph(self, obj=None, is_header=False):
        if is_header:
            return "查看数据"
        record_view_url = self.reverse_url(
            self.get_url_name('record_view'), pk=obj.pk)
        graph_view_url = self.reverse_url(
            self.get_url_name('graph_view'), pk=obj.pk)
        return mark_safe("<a href='%s'>表</a>|<a href='%s'>图</a>" % (record_view_url, graph_view_url))

    @property
    def extra_urls(self):
        patterns = [
            url(r'^record/(?P<pk>\d+)/$', self.wrapper(self.record_view),
                name=self.get_url_name("record_view")),
            url(r'^graph/(?P<pk>\d+)/$', self.wrapper(self.graph_view),
                name=self.get_url_name("graph_view")),
            url(r'^line/(?P<pk>\d+)/$', self.wrapper(self.line),
                name=self.get_url_name("line")),
        ]
        return patterns

    def record_view(self, request, pk):
        record_list = models.SensorRecord.objects.filter(sensor__id=pk)
        sensor = models.Sensor.objects.filter(pk=pk).first()
        return render(request, 'web/record_view.html', {'record_list': record_list, 'sensor': sensor})

    def line(self, request, pk):
        record_list = models.SensorRecord.objects.filter(sensor__id=pk)
        line = (
            Line(init_opts=opts.InitOpts(width="1600px", height="800px"))
            .add_xaxis(xaxis_data=[ele.date_time.strftime("%Y-%m-%d %H:%M:%S") for ele in record_list])
            .add_yaxis(
                series_name="实测值",
                y_axis=[float(ele.value) for ele in record_list],
                markpoint_opts=opts.MarkPointOpts(
                    data=[
                        opts.MarkPointItem(type_="max", name="最大值"),
                        opts.MarkPointItem(type_="min", name="最小值"),
                    ]
                ),
                markline_opts=opts.MarkLineOpts(
                    data=[opts.MarkLineItem(type_="average", name="平均值")]
                ),
            )
            .dump_options_with_quotes()
        )
        return JsonResponse({'data': json.loads(line)})

    def graph_view(self, request, pk):
        data_url = self.reverse_url(self.get_url_name("line"), pk)
        return render(request, 'web/graph_view.html', {'data_url': data_url})

    def multi_delete(self, request):
        """multi_delete.
        批量删除功能:
            执行成功后默认跳转回list，如果要跳转到其他地方，
            请返回一个重定向, e.g., return redirect('http://www.baidu.com')
        :param self:
        """
        pk_list = request.POST.getlist("pk")
        self.model_class.objects.filter(id__in=pk_list).delete()
        # return redirect('http://www.baidu.com')

    multi_delete.text = "批量删除"

    action_list = [multi_delete, ]
    field_list = [StarkHandler.display_checkbox, "name", "imei", get_choice_display("类型", "typo"), get_m2m_display("维护人", "maintainer"),
                  get_datetime_display("投产日期", "create_date"), get_choice_display("状态", "status"), display_record_graph]

    search_list = ["name__contains", "imei__contains", ]
    search_group = [
        SearchOption("typo"),
        SearchOption("maintainer"),
        SearchOption("status"),
    ]
    model_form_class = SensorModelForm
