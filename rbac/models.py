import markdown
from django.db import models
from django.db.models.fields import CharField
from django.db.models.fields.related import ForeignKey, ManyToManyField
from mdeditor.fields import MDTextField


# Create your models here.
class Menu(models.Model):
    """
    Static Menu Table
    """
    title = CharField(verbose_name='标题', max_length=32)
    icon = CharField(verbose_name='图标', max_length=32)

    def __str__(self):
        return self.title


class Access(models.Model):
    """
    Access Table
    """
    title = CharField(verbose_name='标题', max_length=32)
    url = CharField(verbose_name='含正则的URL', max_length=128)
    menu = ForeignKey(verbose_name='所属一级菜单', to='Menu', null=True, blank=True,
                      on_delete=models.CASCADE, help_text='null表示不是菜单；非null则为所属一级菜单的ID')
    pid = ForeignKey(verbose_name='关联二级菜单id', to='Access', null=True, related_name='parent_access',
                     blank=True, on_delete=models.CASCADE, help_text="null表示自身即为所关联的二级菜单")
    name = CharField(verbose_name='URL别名', unique=True, max_length=32)

    def __str__(self) -> str:
        return self.title


class Role(models.Model):
    """
    Role Table
    """
    title = CharField(verbose_name='角色名称', max_length=32)
    access = ManyToManyField(to='Access', verbose_name='所拥有的的权限', blank=True)

    def __str__(self) -> str:
        return self.title


class UserInfo(models.Model):
    """
    UserInfo Table
    """
    name = CharField(verbose_name="用户名", max_length=32)
    password = CharField(verbose_name="密码", max_length=64)
    email = CharField(verbose_name="邮箱", max_length=32)
    role = ManyToManyField(verbose_name="所拥有的的角色", to=Role, blank=True)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name


class Manual(models.Model):
    """
    使用文档
    """
    name = models.CharField(max_length=32, verbose_name="文档名称")
    content = MDTextField(verbose_name="文档内容")

    def get_markdown_content(self):
        return markdown.markdown(self.content, extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ])

    def __str__(self):
        return self.name

