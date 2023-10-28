# Generated by Django 4.1.3 on 2023-10-28 01:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('cid', models.IntegerField(primary_key=True, serialize=False, verbose_name='课程id')),
                ('school', models.CharField(max_length=50, verbose_name='学习名称')),
                ('name', models.CharField(max_length=50, verbose_name='课程名')),
            ],
            options={
                'db_table': 'course',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('tid', models.IntegerField(primary_key=True, serialize=False, verbose_name='标签id')),
                ('content', models.CharField(max_length=50, verbose_name='内容')),
            ],
            options={
                'db_table': 'tag',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='用户id')),
                ('username', models.CharField(max_length=50, verbose_name='用户名')),
                ('password', models.CharField(max_length=50, verbose_name='密码')),
                ('email', models.CharField(max_length=50, verbose_name='邮箱')),
                ('avatar', models.CharField(max_length=2000, verbose_name='头像')),
                ('permission', models.IntegerField(verbose_name='权限')),
                ('last_login', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'user',
            },
        ),
        migrations.CreateModel(
            name='TagCourse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.course', verbose_name='课程id')),
                ('tag_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.tag', verbose_name='标签id')),
            ],
            options={
                'db_table': 'tag_course',
            },
        ),
        migrations.CreateModel(
            name='Star',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.course', verbose_name='课程id')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.user', verbose_name='用户id')),
            ],
            options={
                'db_table': 'star',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('rid', models.IntegerField(primary_key=True, serialize=False, verbose_name='评价id')),
                ('content', models.CharField(max_length=2000, verbose_name='内容')),
                ('date', models.DateTimeField(verbose_name='创建时间')),
                ('teachers', models.CharField(max_length=50, verbose_name='教师')),
                ('course_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.course', verbose_name='课程id')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.user', verbose_name='创建者id')),
            ],
            options={
                'db_table': 'review',
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('nid', models.IntegerField(primary_key=True, serialize=False, verbose_name='通知id')),
                ('content', models.CharField(max_length=2000, verbose_name='内容')),
                ('date', models.DateTimeField(verbose_name='发送日期')),
                ('status', models.IntegerField(verbose_name='状态')),
                ('review_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.review', verbose_name='评价id')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.user', verbose_name='接收者id')),
            ],
            options={
                'db_table': 'notification',
            },
        ),
        migrations.CreateModel(
            name='Like',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.review', verbose_name='评价id')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.user', verbose_name='用户id')),
            ],
            options={
                'db_table': 'like',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('cid', models.IntegerField(primary_key=True, serialize=False, verbose_name='评论id')),
                ('content', models.CharField(max_length=2000, verbose_name='内容')),
                ('date', models.DateTimeField(verbose_name='创建时间')),
                ('review_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.review', verbose_name='评价id')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.user', verbose_name='创建者id')),
            ],
            options={
                'db_table': 'comment',
            },
        ),
        migrations.CreateModel(
            name='Announcement',
            fields=[
                ('aid', models.IntegerField(primary_key=True, serialize=False, verbose_name='公告id')),
                ('title', models.CharField(max_length=50, verbose_name='标题')),
                ('content', models.CharField(max_length=2000, verbose_name='内容')),
                ('date', models.DateTimeField(verbose_name='发布日期')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='judge.user', verbose_name='发布者id')),
            ],
            options={
                'db_table': 'announcement',
            },
        ),
        migrations.AddConstraint(
            model_name='tagcourse',
            constraint=models.UniqueConstraint(fields=('tag_id', 'course_id'), name='primary_key3'),
        ),
        migrations.AddConstraint(
            model_name='star',
            constraint=models.UniqueConstraint(fields=('user_id', 'course_id'), name='primary_key2'),
        ),
        migrations.AddConstraint(
            model_name='like',
            constraint=models.UniqueConstraint(fields=('user_id', 'review_id'), name='primary_key1'),
        ),
    ]
