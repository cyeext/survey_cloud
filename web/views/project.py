from stark.forms.widgets import DateTimePickerInput
from stark.service.v1 import StarkHandler, get_datetime_display, get_m2m_display, StarkModelForm
from web import models


class ProjectModelForm(StarkModelForm):
    class Meta:
        model = models.Project
        fields = '__all__'

        widgets = {
            "start_date": DateTimePickerInput,
            'end_date': DateTimePickerInput,
        }


class ProjectHandler(StarkHandler):

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
            m2m_list = [ele.name for ele in queryset]
            return ', '.join(m2m_list)
        return inner

    field_list = ["name", "leader", get_m2m_display(
        "成员", "teammates"), get_m2m_display("设备", "sensors"), get_datetime_display("开始日期", "start_date"), get_datetime_display("结束日期", "end_date"), ]

    model_form_class = ProjectModelForm
    search_list = ["name__contains", 'leader__name__contains',
                   'leader__realname__contains', ]
