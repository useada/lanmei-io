# -*- coding: utf-8 -*-

import datetime
from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class UserManager(BaseUserManager):
    """通过邮箱，密码创建用户"""
    def create_user(self, email, username, password=None, type=None, **kwargs):
        if not email:
            raise ValueError(u'用户必须要有邮箱')

        user = self.model(
            email=UserManager.normalize_email(email),
            username=username,
            type=type if type else 0
        )
        user.set_password(password)
        if kwargs:
            if kwargs.get('sex', None): user.sex = kwargs['sex']
            # if kwargs.get('is_active', None): user.is_active=kwargs['is_active']
            # if kwargs.get('uid', None): user.uid=kwargs['uid']
            # if kwargs.get('access_token', None): user.access_token=kwargs['access_token']
            if kwargs.get('grade', None): user.url=kwargs['grade']
            if kwargs.get('profile', None): user.profile=kwargs['profile']
            if kwargs.get('avatar', None): user.avatar=kwargs['avatar']

        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(email,
                                password=password,
                                username=username,
                                grade=9,
                                )
        # user.is_admin = True
        user.save(using=self._db)
        return user

    def get_user_by_email(self, email):
        query = self.get_queryset().filter(email=email)
        if query.count() > 0:
            return query[0]
        else:
            return None

    def get_user_by_username(self, username):
        pass


class CustomAuth(object):
    """自定义用户验证"""
    def authenticate(self, email=None, password=None):
        try:
            user = MyUser.objects.get(email=email)
            if user.check_password(password):
                return user
        except MyUser.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            user = MyUser.objects.get(pk=user_id)
            if user.is_active:
                return user
            return None
        except MyUser.DoesNotExist:
            return None


###############################################################################
class TopicManager(models.Manager):
    def query_by_column(self, column_id):
        query = self.get_queryset().filter(column_id=column_id)
        return query

    # def query_by_user(self, user_id):
    #     user = User.objects.get(id=user_id)
    #     article_list = user.article_set.all()
    #     return article_list

    def query_by_polls(self):
        query = self.get_queryset().order_by('poll_num')
        return query

    def query_by_time(self):
        query = self.get_queryset().order_by('-pub_date')
        return query

    def query_by_keyword(self, keyword):
        query = self.get_queryset().filter(title__contains=keyword)
        return query


class ArticleManager(models.Manager):
    def query_by_topic(self, topic_id):
        query = self.get_queryset().filter(topic_id=topic_id).order_by('-poll_num')
        return query

    # def query_by_user(self, user_id):
    #     user = User.objects.get(id=user_id)
    #     article_list = user.article_set.all()
    #     return article_list

    def query_by_polls(self):
        query = self.get_queryset().order_by('-poll_num')
        return query

    def query_by_time(self):
        query = self.get_queryset().order_by('-pub_date')
        return query

    def query_by_keyword(self, keyword):
        query = self.get_queryset().filter(title__contains=keyword)
        return query


class StatusManager(models.Manager):
    def get_current(self):
        try:
            status = self.get(name="current")
            return status
        except:
            return None


# @python_2_unicode_compatible
# class NewUser(AbstractUser):
#     profile = models.CharField('profile', default='', max_length=256)
#
#     def __str__(self):
#         return self.username


@python_2_unicode_compatible
class MyUser(AbstractBaseUser):
    """扩展User"""
    email = models.EmailField(verbose_name='Email', max_length=255, unique=True, db_index=True)
    username = models.CharField(max_length=50, unique=True, db_index=True)
    # is_active = models.BooleanField(default=True)
    # is_admin = models.BooleanField(default=False)
    status = models.IntegerField(default=0)             # 状态,　0:正常,　1:无效
    grade = models.IntegerField(default=0)              # 级别,最低为0,最高为9
    type = models.IntegerField(default=0)				# 类型，0本站，1微博登录
    sex = models.IntegerField(default=0)				# sex, 0 female, 1 male
    # uid = models.CharField(max_length=50, null=True)				# weibo uid
    # access_token = models.CharField(max_length=100, null=True)		# weibo access_token
    # url = models.URLField(null=True)							    # 个人站点
    profile = models.CharField(max_length=200, null=True)		    # 个人信息简介
    avatar = models.CharField(max_length=200, null=True)		    # 头像
    date_joined = models.DateTimeField(auto_now=True, null=True)               # 加入时间
    date_operate = models.DateTimeField(auto_now=True, null=True)              # 数据变化时间

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __unicode__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.grade >= 9

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'user'


@python_2_unicode_compatible
class Column(models.Model):
    name = models.CharField('column_name', max_length=256)
    intro = models.TextField('introduction', default='')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'column'
        verbose_name_plural = 'column'
        ordering = ['name']


@python_2_unicode_compatible
class Topic(models.Model):
    column = models.ForeignKey(Column, blank=True, null=True, verbose_name='belong to')
    author = models.ForeignKey('MyUser')
    status = models.IntegerField(default=0)  # 状态,　0:正常,　1:无效
    content = models.CharField(max_length=256)
    pub_date = models.DateTimeField(auto_now_add=True, editable=True)

    # published = models.BooleanField('notDraft', default=True)
    article_num = models.IntegerField(default=0)
    comment_num = models.IntegerField(default=0)
    poll_num = models.IntegerField(default=0)
    keep_num = models.IntegerField(default=0)

    date_operate = models.DateTimeField(auto_now=True, null=True)
    user_operate = models.ForeignKey('MyUser', related_name="topic_operator", null=True)

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = 'topic'
        verbose_name_plural = 'topic'

    objects = TopicManager()


@python_2_unicode_compatible
class Article(models.Model):
    topic = models.ForeignKey(Topic, blank=True, null=True, verbose_name='belong to')
    author = models.ForeignKey('MyUser', blank=True)
    status = models.IntegerField(default=0)  # 状态,　0:正常,　1:无效
    content = models.TextField('content')
    pub_date = models.DateTimeField(auto_now_add=True, editable=True)
    # update_time = models.DateTimeField(auto_now=True, null=True)
    # published = models.BooleanField('notDraft', default=True)
    comment_num = models.IntegerField(default=0)
    # 投票
    poll_num = models.IntegerField(default=0)
    # 收藏
    keep_num = models.IntegerField(default=0)

    date_operate = models.DateTimeField(auto_now=True, null=True)
    user_operate = models.ForeignKey('MyUser', related_name="article_operator", null=True)

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = 'article'
        verbose_name_plural = 'article'

    objects = ArticleManager()


@python_2_unicode_compatible
class Comment(models.Model):
    author = models.ForeignKey('MyUser', null=True)
    refer_to = models.ForeignKey('MyUser', related_name="refer_to", null=True)
    article = models.ForeignKey(Article, null=True)
    content = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True, editable=True)
    poll_num = models.IntegerField(default=0)

    def __str__(self):
        return self.content


class Poll(models.Model):
    user = models.ForeignKey('MyUser', null=True)
    article = models.ForeignKey(Article, null=True)
    comment = models.ForeignKey(Comment, null=True)


@python_2_unicode_compatible
class Status(models.Model):
    name = models.CharField(max_length=36, unique=True, db_index=True)
    curr_topic = models.ForeignKey(Topic, blank=True, null=True, related_name="curr_topic", verbose_name='current topic')
    objects = StatusManager()

    def __str__(self):
        return self.name
