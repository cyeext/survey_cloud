from django import forms
from rbac.models import UserInfo
from django.core.exceptions import ValidationError


class UserInfoModelForm(forms.ModelForm):
    confirm_password = forms.CharField(max_length=32, label="确认密码")

    class Meta:
        model = UserInfo
        fields = ["name", "email", "password", "confirm_password"]

    def __init__(self, *args, **kwargs):
        super(UserInfoModelForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs["class"] = 'form-control'

    def clean_confirm_password(self):
        password = self.cleaned_data["password"]
        confirm_password = self.cleaned_data["confirm_password"]
        if password != confirm_password:
            raise ValidationError("两次输入的密码不一致!")
        return confirm_password


##################################################开始##################################################
class UpdateUserModelForm(forms.ModelForm):
    class Meta:
        model = UserInfo
        exclude = ['password',]

    def __init__(self, *args, **kwargs):
        super(UpdateUserModelForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"


class PasswordModelForm(forms.ModelForm):
    confirm_password = forms.CharField(max_length=32, label="确认密码")

    class Meta:
        model = UserInfo
        fields = ["password"]

    def __init__(self, *args, **kwargs):
        super(PasswordModelForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs["class"] = 'form-control'

    def clean_confirm_password(self):
        password = self.cleaned_data["password"]
        confirm_password = self.cleaned_data["confirm_password"]
        if password != confirm_password:
            raise ValidationError("两次输入的密码不一致!")
        return confirm_password
##################################################结束##################################################
