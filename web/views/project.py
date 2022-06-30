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
    field_list = ["name", "leader", get_m2m_display(
        "成员", "teammates"), get_datetime_display("开始日期", "start_date"), get_datetime_display("结束日期", "end_date"), ]

    model_form_class = ProjectModelForm
