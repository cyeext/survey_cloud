"""
给所有继承FormContralModelForm的ModelForm增加form-control样式
"""
from django import forms


class FormControlModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(FormControlModelForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
