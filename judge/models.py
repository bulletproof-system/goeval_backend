from django.db import models
from django.contrib.auth.models import AbstractUser
MAX_LEN = 50  # 字符串最大长度
MAX_LEN_LONG = 2000  # 字符串最大长度(长)


# 用户
class User(models.Model):
    uid = models.IntegerField(primary_key=True, verbose_name='用户id')
    username = models.CharField(max_length=MAX_LEN, verbose_name='用户名')
    password = models.CharField(max_length=MAX_LEN, verbose_name='密码')
    email = models.CharField(max_length=MAX_LEN, verbose_name='邮箱')
    avatar = models.CharField(max_length=MAX_LEN_LONG, verbose_name='头像')
    permission = models.IntegerField(verbose_name='权限')  # 0:普通用户 1:管理员
    last_login = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.username

    class Meta:
        db_table = 'user'

class Teacher(models.Model):
    tid = models.IntegerField(primary_key=True, verbose_name='老师id')
    teacher_name = models.CharField(max_length=MAX_LEN, verbose_name='老师姓名')

    def __str__(self):
        return self.teacher_name

    class Meta:
        db_table = 'teacher'


# 课程
class Course(models.Model):
    cid = models.IntegerField(primary_key=True, verbose_name='课程id')
    school = models.CharField(max_length=MAX_LEN, verbose_name='学习名称')
    name = models.CharField(max_length=MAX_LEN, verbose_name='课程名')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'course'


# 标签
class Tag(models.Model):
    tid = models.IntegerField(primary_key=True, verbose_name='标签id')
    content = models.CharField(max_length=MAX_LEN, verbose_name='内容')

    def __str__(self):
        return self.content

    class Meta:
        db_table = 'tag'


# 评价
class Review(models.Model):
    rid = models.IntegerField(primary_key=True, verbose_name='评价id')
    content = models.CharField(max_length=MAX_LEN_LONG, verbose_name='内容')
    date = models.DateTimeField(verbose_name='创建时间')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者id')
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='课程id')
    rating = models.IntegerField(verbose_name='课程评分', default=0)

    def __str__(self):
        return self.content

    class Meta:
        db_table = 'review'


# 评论
class Comment(models.Model):
    cid = models.IntegerField(primary_key=True, verbose_name='评论id')
    content = models.CharField(max_length=MAX_LEN_LONG, verbose_name='内容')
    date = models.DateTimeField(verbose_name='创建时间')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建者id')
    review_id = models.ForeignKey(Review, on_delete=models.CASCADE, verbose_name='评价id')

    def __str__(self):
        return self.content

    class Meta:
        db_table = 'comment'


# 通知
class Notification(models.Model):
    nid = models.IntegerField(primary_key=True, verbose_name='通知id')
    content = models.CharField(max_length=MAX_LEN_LONG, verbose_name='内容')
    date = models.DateTimeField(verbose_name='发送日期')
    status = models.IntegerField(verbose_name='状态')  # 1:已读 0:未读
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='接收者id')
    review_id = models.ForeignKey(Review, on_delete=models.CASCADE, verbose_name='评价id')

    def __str__(self):
        return self.content

    class Meta:
        db_table = 'notification'


# 公告
class Announcement(models.Model):
    aid = models.IntegerField(primary_key=True, verbose_name='公告id')
    title = models.CharField(max_length=MAX_LEN, verbose_name='标题')
    content = models.CharField(max_length=MAX_LEN_LONG, verbose_name='内容')
    date = models.DateTimeField(verbose_name='发布日期')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='发布者id')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'announcement'


# 用户-评价点赞关系
class Like(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户id')
    review_id = models.ForeignKey(Review, on_delete=models.CASCADE, verbose_name='评价id')

    class Meta:
        db_table = 'like'
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'review_id'], name='primary_key1')
        ]


# 用户-课程收藏关系
class Star(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户id')
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='课程id')

    class Meta:
        db_table = 'star'
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'course_id'], name='primary_key2')
        ]


# 标签-课程对应关系
class TagCourse(models.Model):
    tag_id = models.ForeignKey(Tag, on_delete=models.CASCADE, verbose_name='标签id')
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='课程id')

    class Meta:
        db_table = 'tag_course'
        constraints = [
            models.UniqueConstraint(fields=['tag_id', 'course_id'], name='primary_key3')
        ]

#评价-老师对应关系表
class ReviewTeacher(models.Model):
    review_id = models.ForeignKey(Review, on_delete=models.CASCADE, verbose_name='评价id')
    teacher_id = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='老师id')
    class Meta:
        db_table = 'review_teacher'
        constraints = [
            models.UniqueConstraint(fields=['review_id', 'teacher_id'], name='primary_key4')
        ]

#课程-教师对应关系表
class CourseTeacher(models.Model):
    course_id = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='课程id')
    teacher_id = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='老师id')

    class Meta:
        db_table = 'course_teacher'
        constraints = [
            models.UniqueConstraint(fields=['course_id', 'teacher_id'], name='primary_key5')
        ]