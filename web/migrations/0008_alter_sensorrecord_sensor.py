# Generated by Django 3.2 on 2022-09-26 05:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0007_alter_project_leader'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sensorrecord',
            name='sensor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='web.sensor', verbose_name='传感器名称'),
        ),
    ]
