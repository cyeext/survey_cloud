from django import forms
from markdownx.fields import MarkdownxFormField


class ManualForm(forms.Form):
    content = MarkdownxFormField()
