# Generated by Django 4.2.7 on 2023-12-02 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0006_remove_notification_review_id_newcommentnotification_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.CharField(default='http://dummyimage.com/100x100/FF0000/000000&text=Visitor', max_length=2000, verbose_name='头像'),
        ),
    ]
