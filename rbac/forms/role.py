from django import forms
from rbac.models import Role, UserInfo


class RoleModelForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ['title', ]
        labels = {"title": "角色名称"}
        widgets = {
            "title": forms.widgets.TextInput(attrs={"class": "form-control"})
        }


