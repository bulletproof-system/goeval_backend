# Register your models here.
from django.contrib import admin

from . import models

admin.site.register(models.User)
admin.site.register(models.Like)
admin.site.register(models.Star)
admin.site.register(models.TagCourse)
admin.site.register(models.Tag)
admin.site.register(models.Announcement)
admin.site.register(models.Comment)
admin.site.register(models.Course)
admin.site.register(models.Notification)
admin.site.register(models.Review)