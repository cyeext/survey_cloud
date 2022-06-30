# Generated by Django 3.2 on 2022-06-30 06:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('rbac', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=32, verbose_name='部门')),
            ],
        ),
        migrations.CreateModel(
            name='Sensor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='传感器名称')),
                ('imei', models.CharField(max_length=32, verbose_name='IMEI')),
                ('create_date', models.DateField(blank=True, null=True, verbose_name='投产日期')),
            ],
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='用户名')),
                ('password', models.CharField(max_length=64, verbose_name='密码')),
                ('email', models.CharField(max_length=32, verbose_name='邮箱')),
                ('realname', models.CharField(max_length=32, verbose_name='真实姓名')),
                ('phone', models.CharField(max_length=32, verbose_name='手机号')),
                ('gender', models.IntegerField(choices=[(0, '女'), (1, '男')], default=1, verbose_name='性别')),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.department', verbose_name='部门')),
                ('role', models.ManyToManyField(blank=True, to='rbac.Role', verbose_name='所拥有的的角色')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SensorRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField(auto_now_add=True, verbose_name='创建日期')),
                ('value', models.DecimalField(decimal_places=2, max_digits=5, verbose_name='数值')),
                ('sensor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='web.sensor', verbose_name='传感器名称')),
            ],
        ),
        migrations.AddField(
            model_name='sensor',
            name='maintainer',
            field=models.ManyToManyField(to='web.UserInfo', verbose_name='维护人'),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='项目名称')),
                ('start_date', models.DateField(verbose_name='开始日期')),
                ('graduate_date', models.DateField(blank=True, null=True, verbose_name='结束日期')),
                ('leader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='project_leader', to='web.userinfo', verbose_name='负责人')),
                ('sensors', models.ManyToManyField(to='web.Sensor', verbose_name='传感器')),
                ('teammates', models.ManyToManyField(related_name='project_teammates', to='web.UserInfo', verbose_name='成员')),
            ],
        ),
    ]
