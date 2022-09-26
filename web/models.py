from django.db import models
from rbac.models import UserInfo as RbacUserInfo

# Create your models here.


class Department(models.Model):
    """
    部门表
    """
    title = models.CharField(verbose_name="部门", max_length=32)

    def __str__(self):
        return self.title


class UserInfo(RbacUserInfo):
    """
    用户表
    """
    realname = models.CharField(verbose_name="真实姓名", max_length=32)
    phone = models.CharField(verbose_name="手机号", max_length=32)
    gender_choices = [
        (0, '女'),
        (1, '男'),
    ]
    gender = models.IntegerField(
        verbose_name="性别", choices=gender_choices, default=1)
    department = models.ForeignKey(
        verbose_name="部门", to='Department', on_delete=models.CASCADE)

    def __str__(self):
        return self.realname


class Project(models.Model):
    """
    项目表
    """
    name = models.CharField(verbose_name="项目名称", max_length=32)
    start_date = models.DateField(verbose_name='开始日期')
    end_date = models.DateField(
        verbose_name='结束日期', null=True, blank=True)
    leader = models.ForeignKey(verbose_name="负责人", to="userinfo",
                               related_name="project_leader", on_delete=models.CASCADE, limit_choices_to={'role__title': '项目经理'})
    teammates = models.ManyToManyField(
        verbose_name="成员", to='userinfo', related_name='project_teammates')

    sensors = models.ManyToManyField(verbose_name="传感器", to='sensor')

    def __str__(self):
        return self.name


class Sensor(models.Model):
    """
    传感器表
    """
    name = models.CharField(verbose_name="传感器名称", max_length=32)
    type_choices = [
        (0, "位移"),
        (1, "称重"),
        (2, "应变"),
        (3, "流量"),
        (4, "测斜"),
        (5, "GPS"),
    ]
    typo = models.IntegerField(verbose_name="类型", choices=type_choices)
    imei = models.CharField(verbose_name="IMEI", max_length=32)
    status_choices = [
        (0, "离线"),
        (1, "在线"),
    ]
    status = models.IntegerField(verbose_name="状态", choices=status_choices)
    maintainer = models.ManyToManyField(verbose_name="维护人", to='userinfo')
    create_date = models.DateField(verbose_name="投产日期", null=True, blank=True)

    def __str__(self):
        return self.name


class SensorRecord(models.Model):
    """
    传感器数据表
    """
    date_time = models.DateTimeField(verbose_name="创建日期", auto_now_add=True)
    value = models.DecimalField(
        verbose_name="数值", max_digits=5, decimal_places=2)
    sensor = models.ForeignKey(
        verbose_name="传感器名称", to='sensor', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.date_time) + ': ' + str(self.value)
