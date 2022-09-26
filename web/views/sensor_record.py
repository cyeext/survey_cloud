from django.http import HttpResponse
from django.http.request import HttpRequest
from stark.forms.widgets import DateTimePickerInput
from stark.service.v1 import SearchOption, StarkHandler, StarkModelForm
from web import models
import json


class SensorRecordModelForm(StarkModelForm):
    class Meta:
        model = models.SensorRecord
        fields = "__all__"
        widgets = {
            "create_date": DateTimePickerInput,
        }


def get_datetime_display(header, field, format="%Y-%m-%d %H:%M:%S"):
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


class SensorRecordHandler(StarkHandler):

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
    field_list = [StarkHandler.display_checkbox, "sensor", get_datetime_display(
        "记录时间", "date_time"), "value", ]

    search_list = ['date_time__gt', ]

    search_group = [
        SearchOption("sensor")
    ]
    order_list = ['sensor__name', ]
    # order_list = ['value', ]

    def add_view(self, request):
        """add_view.
        添加
        :param self:
        """
        value = request.GET.get('value')
        data = json.loads(value)
        imei = data["imei"]
        value = data["Rex1"]
        value = float(value)

        sensor_obj = models.Sensor.objects.filter(imei=imei).first()
        if sensor_obj:
            record_obj = models.SensorRecord.objects.create(value=value)
            record_obj.sensor = sensor_obj
            record_obj.save()
            return HttpResponse('ok!')
        return HttpResponse("sensor does not exist!")
