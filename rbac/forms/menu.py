from django import forms
from rbac.models import Menu, Access
from django.utils.safestring import mark_safe
from rbac.forms.base import FormControlModelForm

ICON_LIST = [
    ['fa-hand-scissors-o', '<i aria-hidden="true" class="fa fa-hand-scissors-o"></i>'],
    ['fa-hand-spock-o', '<i aria-hidden="true" class="fa fa-hand-spock-o"></i>'],
    ['fa-hand-stop-o', '<i aria-hidden="true" class="fa fa-hand-stop-o"></i>'],
    ['fa-handshake-o', '<i aria-hidden="true" class="fa fa-handshake-o"></i>'],
    ['fa-hard-of-hearing', '<i aria-hidden="true" class="fa fa-hard-of-hearing"></i>'],
    ['fa-hashtag', '<i aria-hidden="true" class="fa fa-hashtag"></i>'],
    ['fa-hdd-o', '<i aria-hidden="true" class="fa fa-hdd-o"></i>'],
    ['fa-headphones', '<i aria-hidden="true" class="fa fa-headphones"></i>'],
    ['fa-heart', '<i aria-hidden="true" class="fa fa-heart"></i>'],
    ['fa-heart-o', '<i aria-hidden="true" class="fa fa-heart-o"></i>'],
    ['fa-heartbeat', '<i aria-hidden="true" class="fa fa-heartbeat"></i>'],
    ['fa-history', '<i aria-hidden="true" class="fa fa-history"></i>'],
    ['fa-home', '<i aria-hidden="true" class="fa fa-home"></i>'],
    ['fa-hotel', '<i aria-hidden="true" class="fa fa-hotel"></i>'],
    ['fa-hourglass', '<i aria-hidden="true" class="fa fa-hourglass"></i>'],
    ['fa-hourglass-1', '<i aria-hidden="true" class="fa fa-hourglass-1"></i>'],
    ['fa-hourglass-2', '<i aria-hidden="true" class="fa fa-hourglass-2"></i>'],
    ['fa-hourglass-3', '<i aria-hidden="true" class="fa fa-hourglass-3"></i>'],
    ['fa-hourglass-end', '<i aria-hidden="true" class="fa fa-hourglass-end"></i>'],
    ['fa-hourglass-half', '<i aria-hidden="true" class="fa fa-hourglass-half"></i>'],
    ['fa-hourglass-o', '<i aria-hidden="true" class="fa fa-hourglass-o"></i>'],
    ['fa-hourglass-start', '<i aria-hidden="true" class="fa fa-hourglass-start"></i>'],
    ['fa-i-cursor', '<i aria-hidden="true" class="fa fa-i-cursor"></i>'],
    ['fa-id-badge', '<i aria-hidden="true" class="fa fa-id-badge"></i>'],
    ['fa-id-card', '<i aria-hidden="true" class="fa fa-id-card"></i>'],
    ['fa-id-card-o', '<i aria-hidden="true" class="fa fa-id-card-o"></i>'],
    ['fa-image', '<i aria-hidden="true" class="fa fa-image"></i>'],
    ['fa-mail-reply-all', '<i aria-hidden="true" class="fa fa-mail-reply-all"></i>'],
    ['fa-reply', '<i aria-hidden="true" class="fa fa-reply"></i>'],
    ['fa-reply-all', '<i aria-hidden="true" class="fa fa-reply-all"></i>'],
    ['fa-retweet', '<i aria-hidden="true" class="fa fa-retweet"></i>'],
    ['fa-wrench', '<i aria-hidden="true" class="fa fa-wrench"></i>']]

for item in ICON_LIST:
    item[1] = mark_safe(item[1])


class StaticModelForm(forms.ModelForm):
    class Meta:
        model = Menu
        fields = ['title', 'icon']
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "icon": forms.RadioSelect(choices=ICON_LIST, attrs={"class": "clearfix"})
        }


class DynamicModelForm(FormControlModelForm):
    class Meta:
        model = Access
        fields = ["title", "url", "name", "menu"]


class AccessModelForm(FormControlModelForm):
    class Meta:
        model = Access
        fields = ["title", "url", "name"]


##############################开始##############################
class MultiAccessAddForm(forms.Form):
    title = forms.CharField(widget=forms.widgets.TextInput(attrs={"class": "form-control"}))
    url = forms.CharField(widget=forms.widgets.TextInput(attrs={"class": "form-control"}))
    name = forms.CharField(widget=forms.widgets.TextInput(attrs={"class": "form-control"}))
    menu_id = forms.ChoiceField(choices=[(None, "------"),], widget=forms.Select(attrs={"class": "form-control"}), required=False)
    pid_id = forms.ChoiceField(choices=[(None, "------")], widget=forms.Select(attrs={"class": "form-control"}), required=False)

    def __init__(self, *args, **kwargs) -> None:
        super(MultiAccessAddForm, self).__init__(*args, **kwargs)
        self.fields["menu_id"].choices += Menu.objects.all().values_list("id", "title")
        self.fields["pid_id"].choices += Access.objects.filter(pid__isnull=True).exclude(menu_id__isnull=True).values_list("id", "title")


class MultiAccessUpdateForm(forms.Form):
    id = forms.IntegerField(widget=forms.widgets.HiddenInput(attrs={"class": "form-control"}))
    title = forms.CharField(widget=forms.widgets.TextInput(attrs={"class": "form-control"}))
    url = forms.CharField(widget=forms.widgets.TextInput(attrs={"class": "form-control"}))
    name = forms.CharField(widget=forms.widgets.TextInput(attrs={"class": "form-control"}))
    menu_id = forms.ChoiceField(choices=[(None, "------"),], widget=forms.Select(attrs={"class": "form-control"}), required=False)
    pid_id = forms.ChoiceField(choices=[(None, "------")], widget=forms.Select(attrs={"class": "form-control"}), required=False)

    def __init__(self, *args, **kwargs) -> None:
        super(MultiAccessUpdateForm, self).__init__(*args, **kwargs)
        self.fields["menu_id"].choices += Menu.objects.all().values_list("id", "title")
        self.fields["pid_id"].choices += Access.objects.filter(pid__isnull=True).exclude(menu_id__isnull=True).values_list("id", "title")
##############################结束##############################







