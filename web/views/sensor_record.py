from stark.forms.widgets import DateTimePickerInput
from stark.service.v1 import StarkHandler, StarkModelForm
from web import models


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

    field_list = ["sensor", get_datetime_display(
        "记录时间", "date_time"), "value", ]

    order_list = ['sensor__name', ]
    # order_list = ['value', ]
