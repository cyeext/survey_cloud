from stark.service.v1 import StarkHandler, StarkModelForm, StarkForm, SearchOption, get_choice_display
from django import forms
from django.core.exceptions import ValidationError
from web import models
from stark.utils.md5 import gen_md5
from django.shortcuts import render, redirect, HttpResponse
from django.conf.urls import url
from django.utils.safestring import mark_safe


class UserInfoAddModelForm(StarkModelForm):
    confirm_password = forms.CharField(label="确认密码")

    class Meta:
        model = models.UserInfo
        fields = ["name", "password", "confirm_password", "realname",
                  "gender", "phone", "email", "department", "role", ]

    def clean_confirm_password(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        if password == confirm_password:
            return confirm_password
        else:
            raise ValidationError("两次输入的密码不一致")

    def clean(self):
        password = self.cleaned_data["password"]
        self.cleaned_data["password"] = gen_md5(password)
        return self.cleaned_data


class UserInfoForm(StarkForm):
    password = forms.CharField(label="密码", widget=forms.PasswordInput)
    # PasswordInput: 输入密码时显示密文
    confirm_password = forms.CharField(
        label="确认密码", widget=forms.PasswordInput)

    def clean_confirm_password(self):
        password = self.cleaned_data["password"]
        confirm_password = self.cleaned_data["confirm_password"]
        if password != confirm_password:
            raise ValidationError("两次输入的密码不一致！")
        return confirm_password

    def clean(self):
        password = self.cleaned_data["password"]
        self.cleaned_data['password'] = gen_md5(password)
        return self.cleaned_data


class UserInfoEditModelForm(StarkModelForm):
    class Meta:
        model = models.UserInfo
        fields = ["name", "realname",
                  "gender", "phone", "email", "department", "role", ]


class UserInfoHandler(StarkHandler):

    def get_model_form_class(self, is_add=True):
        if is_add:
            return UserInfoAddModelForm
        return UserInfoEditModelForm

    def reset_password(self, request, pk):
        obj = self.model_class.objects.filter(pk=pk)
        if not obj:
            return HttpResponse("该用户不存在")
        if request.method == "GET":
            form = UserInfoForm()
            return render(request, 'stark/change.html', {'form': form})
        form = UserInfoForm(data=request.POST)
        if form.is_valid():
            obj.update(password=form.cleaned_data['password'])
            return redirect(self.reverse_list_url())
        return render(request, 'stark/change.html', {'form': form})

    def display_reset_password(self, obj=None, is_header=False):
        if is_header:
            return "重置密码"
        url = self.reverse_reset_password_url(obj.pk)
        return mark_safe('<a href="%s">重置密码</a>' % url)

    def reverse_reset_password_url(self, *args, **kwargs):
        return self.reverse_url(self.reset_password_url_name, *args, **kwargs)

    @property
    def reset_password_url_name(self):
        return self.get_url_name("reset_password")

    @property
    def extra_urls(self):
        patterns = [
            url(r'^reset/password/(?P<pk>\d+)/$', self.wrapper(self.reset_password),
                name=self.reset_password_url_name),
        ]
        return patterns

    field_list = ["realname", "email",
                  get_choice_display("性别", "gender"), "phone", "email", "department", display_reset_password, ]

    search_list = ['name__contains', 'realname__contains']
    search_group = [
        SearchOption("gender"),
        SearchOption("department"),
    ]
