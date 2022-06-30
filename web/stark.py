from stark.service.v1 import site
from web.views.department import DepartmentHandler
from web.views.project import ProjectHandler
from web.views.sensor import SensorHandler
from web.views.sensor_record import SensorRecordHandler
from web.views.userinfo import UserInfoHandler
from web import models

site.registry(models.UserInfo, UserInfoHandler)
site.registry(models.Department, DepartmentHandler)
site.registry(models.Project, ProjectHandler)
site.registry(models.Sensor, SensorHandler)
site.registry(models.SensorRecord, SensorRecordHandler)
